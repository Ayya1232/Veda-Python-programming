"""
Duplicate Record Detection System
---------------------------------
Finds exact and near-duplicate customer records using Pandas + difflib.

Usage:
    python duplicate_detector.py                # uses/creates sample_customers.csv
    python duplicate_detector.py my_data.csv    # your own file

Expected columns: customer_id, name, email, phone, address, city, zip
(Adjust MATCH_FIELDS / WEIGHTS below for other datasets.)

Outputs:
    exact_duplicates_report.csv
    potential_duplicates_report.csv
    cleaned_dataset.csv
"""
import re
import sys
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

import pandas as pd

# ---------- Configuration ----------
EXACT_KEYS = ["name_norm", "email_norm", "phone_norm"]   # all must match for "exact"
WEIGHTS = {"name_norm": 0.40, "email_norm": 0.25, "phone_norm": 0.15, "address_norm": 0.20}
REVIEW_THRESHOLD = 0.85   # score >= this -> flagged for human review
ABBREVIATIONS = {"street": "st", "avenue": "ave", "road": "rd", "drive": "dr",
                 "lane": "ln", "boulevard": "blvd", "apartment": "apt"}


# ---------- 1. Normalization ----------
def norm_text(value) -> str:
    """Lowercase, remove punctuation, collapse whitespace."""
    if pd.isna(value):
        return ""
    s = re.sub(r"[^a-z0-9\s]", " ", str(value).lower())
    return re.sub(r"\s+", " ", s).strip()


def norm_address(value) -> str:
    words = norm_text(value).split()
    return " ".join(ABBREVIATIONS.get(w, w) for w in words)


def norm_phone(value) -> str:
    digits = re.sub(r"\D", "", "" if pd.isna(value) else str(value))
    return digits[-10:]  # ignore country code


def norm_email(value) -> str:
    return "" if pd.isna(value) else str(value).strip().lower()


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["name_norm"] = df["name"].map(norm_text)
    df["email_norm"] = df["email"].map(norm_email)
    df["phone_norm"] = df["phone"].map(norm_phone)
    df["address_norm"] = (df["address"].fillna("") + " " + df["city"].fillna("")).map(norm_address)
    return df


# ---------- 2. Exact duplicates ----------
def find_exact(df: pd.DataFrame) -> pd.DataFrame:
    mask = df.duplicated(subset=EXACT_KEYS, keep=False) & (df["name_norm"] != "")
    dups = df[mask].copy()
    dups["group_id"] = dups.groupby(EXACT_KEYS).ngroup() + 1
    return dups.sort_values(["group_id", "customer_id"])


# ---------- 3. Near duplicates (fuzzy) ----------
def sim(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def find_potential(df: pd.DataFrame, exact_ids: set) -> pd.DataFrame:
    # Blocking: only compare records sharing zip OR first letter of name,
    # which avoids comparing every pair in large datasets.
    df = df.assign(block=df["zip"].astype(str).str[:3] + "|" + df["name_norm"].str[:1])
    rows = []
    for _, block in df.groupby("block"):
        for (_, a), (_, b) in combinations(block.iterrows(), 2):
            # skip pairs that are already exact duplicates of each other
            if all(a[k] == b[k] for k in EXACT_KEYS):
                continue
            scores = {f: sim(a[f], b[f]) for f in WEIGHTS}
            total = sum(scores[f] * w for f, w in WEIGHTS.items())
            if total >= REVIEW_THRESHOLD:
                rows.append({
                    "id_a": a["customer_id"], "id_b": b["customer_id"],
                    "name_a": a["name"], "name_b": b["name"],
                    "email_a": a["email"], "email_b": b["email"],
                    "phone_a": a["phone"], "phone_b": b["phone"],
                    "address_a": a["address"], "address_b": b["address"],
                    "name_sim": round(scores["name_norm"], 2),
                    "email_sim": round(scores["email_norm"], 2),
                    "phone_sim": round(scores["phone_norm"], 2),
                    "address_sim": round(scores["address_norm"], 2),
                    "match_score": round(total, 3),
                    "decision": "REVIEW",   # a human confirms/rejects
                })
    cols = ["id_a", "id_b", "match_score"]
    return (pd.DataFrame(rows).sort_values("match_score", ascending=False)
            if rows else pd.DataFrame(columns=cols))


# ---------- 4. Cleaned dataset ----------
def clean(df: pd.DataFrame, potential: pd.DataFrame) -> pd.DataFrame:
    """Drop ONLY exact duplicates (keep first). Uncertain matches are kept
    and flagged so nothing is deleted without human review."""
    cleaned = df.drop_duplicates(subset=EXACT_KEYS, keep="first").copy()
    flagged = set(potential["id_a"]).union(potential["id_b"]) if len(potential) else set()
    cleaned["needs_review"] = cleaned["customer_id"].isin(flagged)
    return cleaned.drop(columns=["name_norm", "email_norm", "phone_norm", "address_norm"])


# ---------- Sample data ----------
def make_sample(path: Path):
    data = [
        (1, "John Smith", "john.smith@mail.com", "(555) 123-4567", "12 Oak Street", "Austin", "73301"),
        (2, "john smith", "JOHN.SMITH@mail.com", "555-123-4567", "12 Oak St.", "Austin", "73301"),   # exact after normalizing
        (3, "Jon Smith", "jon.smith@mail.com", "5551234567", "12 Oak St", "Austin", "73301"),        # near
        (4, "Maria Garcia", "maria.g@mail.com", "555-222-3333", "88 Pine Avenue", "Dallas", "75001"),
        (5, "Maria Garcia", "maria.g@mail.com", "+1 555 222 3333", "88 Pine Ave", "Dallas", "75001"),  # exact
        (6, "Maria Garcia-Lopez", "mgarcia@work.com", "555-222-3333", "88 Pine Ave", "Dallas", "75001"),  # near
        (7, "Aisha Khan", "aisha.khan@mail.com", "555-777-8888", "5 Lake Road", "Houston", "77001"),
        (8, "Aisha Khan", "aisha.khan@mail.com", "555-777-8888", "5 Lake Rd", "Houston", "77001"),   # exact
        (9, "Robert Brown", "rbrown@mail.com", "555-901-2345", "300 Main Street", "Austin", "73301"),
        (10, "Roberto Brown", "r.brown@mail.com", "555-901-2345", "300 Main St", "Austin", "73301"), # near
        (11, "Linda Chen", "linda.chen@mail.com", "555-444-5555", "9 Hill Lane", "Plano", "75023"),
        (12, "David Lee", "dlee@mail.com", "555-666-1212", "71 Elm Drive", "Austin", "73301"),
        (13, "Priya Nair", "priya.n@mail.com", "555-313-4141", "40 Cedar Blvd", "Dallas", "75001"),
        (14, "Priya Nayar", "priya.n@mail.com", "555-313-4141", "40 Cedar Boulevard", "Dallas", "75001"),  # near
    ]
    pd.DataFrame(data, columns=["customer_id", "name", "email", "phone", "address", "city", "zip"]).to_csv(path, index=False)


# ---------- Main ----------
def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("sample_customers.csv")
    if not src.exists():
        make_sample(src)
        print(f"Created sample data: {src}")

    df = normalize(pd.read_csv(src, dtype=str))
    exact = find_exact(df)
    potential = find_potential(df, set(exact["customer_id"]))
    cleaned = clean(df, potential)

    exact.drop(columns=["name_norm", "email_norm", "phone_norm", "address_norm"]).to_csv("exact_duplicates_report.csv", index=False)
    potential.to_csv("potential_duplicates_report.csv", index=False)
    cleaned.to_csv("cleaned_dataset.csv", index=False)

    print(f"Records loaded:            {len(df)}")
    print(f"Exact duplicate records:   {len(exact)} in {exact['group_id'].nunique() if len(exact) else 0} groups")
    print(f"Potential duplicate pairs: {len(potential)} (threshold {REVIEW_THRESHOLD})")
    print(f"Cleaned dataset rows:      {len(cleaned)} (removed {len(df) - len(cleaned)} exact dups)")


if __name__ == "__main__":
    main()