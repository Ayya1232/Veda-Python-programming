"""Background Job Processor - FastAPI + worker threads + SQLite.

Flow: POST /jobs -> job saved as 'queued' -> returns 202 immediately ->
worker thread picks it up -> status/logs updated -> GET /jobs/{id} to track.
"""
import json, logging, queue, random, sqlite3, threading, time, uuid
from contextlib import asynccontextmanager, closing
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = "jobs.db"
NUM_WORKERS = 2
MAX_RETRIES = 3          # total attempts per job
BACKOFF_BASE = 1.0       # seconds; doubles each retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(levelname)s %(message)s",
    handlers=[logging.FileHandler("execution.log"), logging.StreamHandler()],
)
log = logging.getLogger("jobs")
job_queue: "queue.Queue[str]" = queue.Queue()   # the "message queue"
db_lock = threading.Lock()


# ---------- persistence ----------
def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")

def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with closing(db()) as c, c:
        c.execute("""CREATE TABLE IF NOT EXISTS jobs(
            id TEXT PRIMARY KEY, type TEXT, payload TEXT, status TEXT,
            attempts INTEGER DEFAULT 0, result TEXT, error TEXT,
            created_at TEXT, updated_at TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS job_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT, ts TEXT,
            level TEXT, message TEXT)""")

def update(job_id, **fields):
    fields["updated_at"] = now()
    cols = ", ".join(f"{k}=?" for k in fields)
    with db_lock, closing(db()) as c, c:
        c.execute(f"UPDATE jobs SET {cols} WHERE id=?", (*fields.values(), job_id))

def job_log(job_id, message, level="INFO"):
    log.log(getattr(logging, level), "job=%s %s", job_id[:8], message)
    with db_lock, closing(db()) as c, c:
        c.execute("INSERT INTO job_logs(job_id, ts, level, message) VALUES(?,?,?,?)",
                  (job_id, now(), level, message))


# ---------- the slow tasks ----------
def generate_report(payload, jid):
    rows = int(payload.get("rows", 1000))
    for pct in (25, 50, 75, 100):
        time.sleep(1)
        job_log(jid, f"report {pct}% built")
    return {"report": payload.get("name", "report"), "rows": rows}

def process_emails(payload, jid):
    recipients = payload.get("recipients", [])
    for r in recipients:
        time.sleep(0.5)
        job_log(jid, f"sent email to {r}")
    return {"sent": len(recipients)}

def flaky_task(payload, jid):
    """Fails randomly - demonstrates retries."""
    time.sleep(0.5)
    if random.random() < payload.get("fail_rate", 0.7):
        raise RuntimeError("simulated transient failure")
    return {"ok": True}

TASKS = {"report": generate_report, "email": process_emails, "flaky": flaky_task}


# ---------- worker ----------
def run_job(job_id):
    with closing(db()) as c:
        row = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    payload = json.loads(row["payload"])
    attempts = row["attempts"]
    while attempts < MAX_RETRIES:
        attempts += 1
        update(job_id, status="running", attempts=attempts)
        job_log(job_id, f"started (attempt {attempts}/{MAX_RETRIES})")
        try:
            result = TASKS[row["type"]](payload, job_id)
            update(job_id, status="completed", result=json.dumps(result), error=None)
            job_log(job_id, "completed")
            return
        except Exception as e:
            job_log(job_id, f"failed: {e}", "ERROR")
            update(job_id, error=str(e))
            if attempts < MAX_RETRIES:
                delay = BACKOFF_BASE * 2 ** (attempts - 1)
                update(job_id, status="retrying")
                job_log(job_id, f"retrying in {delay:.0f}s", "WARNING")
                time.sleep(delay)
    update(job_id, status="failed")
    job_log(job_id, "gave up after max retries", "ERROR")

def worker_loop():
    while True:
        job_id = job_queue.get()
        try:
            run_job(job_id)
        except Exception:
            log.exception("worker crashed on %s", job_id)
        finally:
            job_queue.task_done()


# ---------- API ----------
@asynccontextmanager
async def lifespan(app):
    init_db()
    # re-queue anything left over from a previous run
    with closing(db()) as c:
        for r in c.execute("SELECT id FROM jobs WHERE status IN ('queued','running','retrying')"):
            job_queue.put(r["id"])
    for i in range(NUM_WORKERS):
        threading.Thread(target=worker_loop, daemon=True, name=f"worker-{i}").start()
    yield

app = FastAPI(title="Background Job Processor", lifespan=lifespan)

class JobRequest(BaseModel):
    type: str
    payload: dict = {}

@app.post("/jobs", status_code=202)
def submit(req: JobRequest):
    if req.type not in TASKS:
        raise HTTPException(400, f"unknown type; choose from {list(TASKS)}")
    job_id = str(uuid.uuid4())
    with db_lock, closing(db()) as c, c:
        c.execute("INSERT INTO jobs(id,type,payload,status,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                  (job_id, req.type, json.dumps(req.payload), "queued", now(), now()))
    job_queue.put(job_id)
    job_log(job_id, f"queued ({req.type})")
    return {"job_id": job_id, "status": "queued"}   # returns instantly

@app.get("/jobs/{job_id}")
def status(job_id: str):
    with closing(db()) as c:
        row = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row: raise HTTPException(404, "job not found")
    d = dict(row); d["payload"] = json.loads(d["payload"])
    d["result"] = json.loads(d["result"]) if d["result"] else None
    return d

@app.get("/jobs/{job_id}/logs")
def logs(job_id: str):
    with closing(db()) as c:
        return [dict(r) for r in c.execute(
            "SELECT ts, level, message FROM job_logs WHERE job_id=? ORDER BY id", (job_id,))]

@app.get("/jobs")
def list_jobs(status: str | None = None):
    q, args = "SELECT id,type,status,attempts,updated_at FROM jobs", ()
    if status: q, args = q + " WHERE status=?", (status,)
    with closing(db()) as c:
        return [dict(r) for r in c.execute(q + " ORDER BY created_at DESC", args)]