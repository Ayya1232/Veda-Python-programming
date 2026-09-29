"""Run with the server up:  python demo.py"""
import time, requests
B = "http://127.0.0.1:8000"
ids = [requests.post(f"{B}/jobs", json=j).json()["job_id"] for j in [
    {"type": "report", "payload": {"name": "Q3 sales", "rows": 5000}},
    {"type": "email", "payload": {"recipients": ["a@x.com", "b@x.com"]}},
    {"type": "flaky", "payload": {"fail_rate": 0.7}},
    {"type": "flaky", "payload": {"fail_rate": 1.0}},   # always fails -> 'failed'
]]
print("submitted (returned instantly):", ids)
while True:
    st = [requests.get(f"{B}/jobs/{i}").json()["status"] for i in ids]
    print(st)
    if all(s in ("completed", "failed") for s in st): break
    time.sleep(1)
for i in ids:
    print("\n==", i[:8]); [print(" ", l["level"], l["message"]) for l in requests.get(f"{B}/jobs/{i}/logs").json()]