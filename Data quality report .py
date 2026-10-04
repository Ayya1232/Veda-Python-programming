#!/usr/bin/env python3
"""
Data Quality Reporting Tool
---------------------------
Profiles any CSV file and reports:
  * missing values (completeness)
  * duplicate rows / uniqueness
  * invalid data types (values that don't match a column's dominant type)
  * unique-value counts
  * suspicious records (outliers, negatives, impossible ages, bad emails,
    future dates, stray whitespace, constant columns)

Usage:
  python data_quality_report.py data.csv
  python data_quality_report.py data.csv --out reports --type-threshold 0.8
  python data_quality_report.py --demo          # generates sample data and runs on it

Outputs (in --out directory):
  data_quality_report.md   human-readable report
  quality_metrics.csv      per-column metrics
  invalid_records.csv      row-level list of every issue found
"""
import argparse
import os
import re
import sys

import numpy as np
import pandas as pd

MISSING_TOKENS = {"", "na", "n/a", "nan", "null", "none", "nil", "-", "--", "?", "missing", "unknown"}
NON_NEGATIVE_HINTS = ("age", "price", "amount", "quantity", "qty", "salary", "income",
                      "cost", "count", "total", "weight", "height", "revenue")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
BOOL_TOKENS = {"true", "false", "yes", "no", "y", "n", "t", "f", "0", "1"}


# ----------------------------------------------------------------- loading
def load_csv(path: str) -> pd.DataFrame:
    """Read everything as text so we can judge types ourselves."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False, skipinitialspace=False)
    return df


def normalise_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Convert blank / placeholder tokens to real NaN (whitespace kept for later checks)."""
    out = df.copy()
    for c in out.columns:
        s = out[c]
        mask = s.str.strip().str.lower().isin(MISSING_TOKENS)
        out[c] = s.mask(mask, np.nan)
    return out


# ----------------------------------------------------------- type inference
def _parse(series: pd.Series, kind: str) -> pd.Series:
    s = series.dropna().str.strip()
    if kind == "numeric":
        return pd.to_numeric(s.str.replace(",", "", regex=False), errors="coerce")
    if kind == "datetime":
        return pd.to_datetime(s, errors="coerce")
    if kind == "boolean":
        return s.str.lower().where(s.str.lower().isin(BOOL_TOKENS))
    raise ValueError(kind)


def infer_type(series: pd.Series, threshold: float) -> str:
    """Return the dominant type if >= threshold of non-null values fit it."""
    s = series.dropna()
    if s.empty:
        return "empty"
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # boolean only if values are clearly yes/no/true/false (not just 0/1)
        lowered = s.str.strip().str.lower()
        if lowered.isin({"true", "false", "yes", "no", "y", "n"}).mean() >= threshold:
            return "boolean"
        for kind in ("numeric", "datetime"):
            if _parse(series, kind).notna().mean() >= threshold:
                return kind
    return "text"


def find_invalid_types(series: pd.Series, expected: str) -> pd.Index:
    """Index labels whose (non-null) value does not match the expected type."""
    if expected in ("text", "empty"):
        return pd.Index([])
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        parsed = _parse(series, expected)
    return parsed.index[parsed.isna()]


# ------------------------------------------------------- suspicious records
def suspicious_checks(df: pd.DataFrame, col: str, dtype: str):
    """Yield (row_index, issue, value) for suspicious values in one column."""
    s = df[col]
    name = col.lower()

    # stray whitespace
    ws = s.dropna()
    ws = ws[ws != ws.str.strip()]
    for i, v in ws.items():
        yield i, "Leading/trailing whitespace", v

    if dtype == "numeric":
        nums = _parse(s, "numeric")
        if len(nums) >= 4:
            q1, q3 = nums.quantile(0.25), nums.quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                lo, hi = q1 - 3 * iqr, q3 + 3 * iqr
                for i in nums[(nums < lo) | (nums > hi)].index:
                    yield i, f"Extreme outlier (outside {lo:.2f}..{hi:.2f})", s[i]
        if any(h in name for h in NON_NEGATIVE_HINTS):
            for i in nums[nums < 0].index:
                yield i, "Negative value in non-negative field", s[i]
        if "age" in name.split("_") or name == "age":
            for i in nums[nums > 120].index:
                yield i, "Impossible age (>120)", s[i]

    if dtype == "datetime":
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            dates = _parse(s, "datetime").dropna()
        for i in dates[dates > pd.Timestamp.now()].index:
            yield i, "Date in the future", s[i]
        for i in dates[dates < pd.Timestamp("1900-01-01")].index:
            yield i, "Date before 1900", s[i]

    if "email" in name:
        vals = s.dropna().str.strip()
        for i in vals[~vals.str.match(EMAIL_RE)].index:
            yield i, "Malformed email address", s[i]


# ------------------------------------------------------------------ profile
def profile(df_raw: pd.DataFrame, threshold: float = 0.8):
    df = normalise_missing(df_raw)
    n_rows = len(df)
    metrics, issues = [], []
    col_types = {}

    for col in df.columns:
        s = df[col]
        dtype = infer_type(s, threshold)
        col_types[col] = dtype
        non_null = s.dropna()
        missing = int(s.isna().sum())

        bad_type_idx = find_invalid_types(s, dtype)
        for i in bad_type_idx:
            issues.append((i, col, f"Invalid data type (expected {dtype})", s[i]))

        for i, issue, val in suspicious_checks(df, col, dtype):
            issues.append((i, col, issue, val))

        for i in s.index[s.isna()]:
            issues.append((i, col, "Missing value", ""))

        n_unique = int(non_null.nunique())
        metrics.append({
            "column": col,
            "inferred_type": dtype,
            "non_null": len(non_null),
            "missing": missing,
            "completeness_pct": round(100 * (1 - missing / n_rows), 2) if n_rows else 0,
            "unique_values": n_unique,
            "uniqueness_pct": round(100 * n_unique / len(non_null), 2) if len(non_null) else 0,
            "invalid_type_count": len(bad_type_idx),
            "validity_pct": round(100 * (1 - len(bad_type_idx) / len(non_null)), 2) if len(non_null) else 100,
            "constant_column": n_unique <= 1 and len(non_null) > 1,
        })

    metrics_df = pd.DataFrame(metrics)

    # duplicates (full-row, on normalised data)
    dup_mask = df.duplicated(keep="first")
    for i in df.index[dup_mask]:
        issues.append((i, "(entire row)", "Duplicate row", ""))

    issues_df = pd.DataFrame(issues, columns=["row_index", "column", "issue", "value"])
    if not issues_df.empty:
        issues_df.insert(0, "csv_row", issues_df["row_index"] + 2)  # +2: header + 1-based
        issues_df = issues_df.sort_values(["row_index", "column"]).reset_index(drop=True)

    overall = {
        "rows": n_rows,
        "columns": df.shape[1],
        "total_cells": n_rows * df.shape[1],
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(dup_mask.sum()),
        "rows_with_issues": int(issues_df[issues_df["issue"] != "Missing value"]["row_index"].nunique())
        if not issues_df.empty else 0,
    }
    cells = max(overall["total_cells"], 1)
    overall["completeness_pct"] = round(100 * (1 - overall["missing_cells"] / cells), 2)
    overall["uniqueness_pct"] = round(100 * (1 - overall["duplicate_rows"] / max(n_rows, 1)), 2)
    overall["validity_pct"] = round(float(metrics_df["validity_pct"].mean()), 2) if len(metrics_df) else 100
    overall["quality_score"] = round(np.mean([overall["completeness_pct"],
                                              overall["uniqueness_pct"],
                                              overall["validity_pct"]]), 2)
    return overall, metrics_df, issues_df


# ------------------------------------------------------------------- report
def build_report(source: str, overall: dict, metrics: pd.DataFrame, issues: pd.DataFrame) -> str:
    L = []
    L.append(f"# Data Quality Report\n\n**Source:** `{source}`\n")
    L.append("## 1. Summary\n")
    L.append(f"| Metric | Value |\n|---|---|")
    L.append(f"| Rows | {overall['rows']} |")
    L.append(f"| Columns | {overall['columns']} |")
    L.append(f"| Completeness | {overall['completeness_pct']}% ({overall['missing_cells']} missing cells) |")
    L.append(f"| Uniqueness | {overall['uniqueness_pct']}% ({overall['duplicate_rows']} duplicate rows) |")
    L.append(f"| Validity (type conformity) | {overall['validity_pct']}% |")
    L.append(f"| Rows with non-missing issues | {overall['rows_with_issues']} |")
    L.append(f"| **Overall quality score** | **{overall['quality_score']} / 100** |\n")

    L.append("## 2. Column Profile\n")
    L.append("| Column | Type | Missing | Complete % | Unique | Invalid types |")
    L.append("|---|---|---|---|---|---|")
    for _, r in metrics.iterrows():
        L.append(f"| {r['column']} | {r['inferred_type']} | {r['missing']} | "
                 f"{r['completeness_pct']} | {r['unique_values']} | {r['invalid_type_count']} |")
    L.append("")

    L.append("## 3. Issues by Category\n")
    if issues.empty:
        L.append("No issues found.\n")
    else:
        cleaned = issues["issue"].str.replace(r"\s*\(outside .*?\)", "", regex=True)
        counts = cleaned.value_counts()
        L.append("| Issue | Count |\n|---|---|")
        for k, v in counts.items():
            L.append(f"| {k} | {v} |")
        L.append("")

    L.append("## 4. Flags\n")
    flags = []
    for _, r in metrics.iterrows():
        if r["completeness_pct"] < 90:
            flags.append(f"- `{r['column']}` is only {r['completeness_pct']}% complete.")
        if r["constant_column"]:
            flags.append(f"- `{r['column']}` is constant (one unique value) and adds no information.")
        if r["validity_pct"] < 100:
            flags.append(f"- `{r['column']}` has {r['invalid_type_count']} value(s) that don't match type `{r['inferred_type']}`.")
        if r["uniqueness_pct"] == 100 and r["non_null"] > 1:
            flags.append(f"- `{r['column']}` is fully unique, a candidate key/ID.")
    if overall["duplicate_rows"]:
        flags.append(f"- {overall['duplicate_rows']} duplicate row(s) detected.")
    L.extend(flags or ["- None."])
    L.append("\nSee `invalid_records.csv` for the row-level issue list.")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------- demo
def make_demo(path: str):
    rng = np.random.default_rng(42)
    n = 200
    df = pd.DataFrame({
        "customer_id": range(1, n + 1),
        "name": [f"Customer {i}" for i in range(1, n + 1)],
        "email": [f"user{i}@example.com" for i in range(1, n + 1)],
        "age": rng.integers(18, 80, n).astype(object),
        "purchase_amount": np.round(rng.normal(120, 30, n), 2).astype(object),
        "signup_date": pd.date_range("2023-01-01", periods=n).strftime("%Y-%m-%d").astype(object),
        "country": rng.choice(["IN", "US", "UK"], n),
        "status": "active",
    })
    df.loc[3, "age"] = "abc"; df.loc[10, "age"] = 250; df.loc[15, "age"] = -5
    df.loc[20:27, "email"] = ""; df.loc[30, "email"] = "not-an-email"
    df.loc[40, "purchase_amount"] = 99999; df.loc[41, "purchase_amount"] = "N/A"
    df.loc[50, "signup_date"] = "2031-05-01"; df.loc[51, "signup_date"] = "not a date"
    df.loc[60, "name"] = "  Padded Name "
    df = pd.concat([df, df.iloc[[5, 6]]], ignore_index=True)  # duplicates
    df.to_csv(path, index=False)


# --------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description="Profile a CSV and generate a data-quality report.")
    ap.add_argument("csv", nargs="?", help="Path to CSV file")
    ap.add_argument("--out", default="dq_output", help="Output directory (default: dq_output)")
    ap.add_argument("--type-threshold", type=float, default=0.8,
                    help="Share of values that must fit a type to infer it (default 0.8)")
    ap.add_argument("--demo", action="store_true", help="Generate sample data and profile it")
    a = ap.parse_args(argv)
    if not a.csv and not a.demo:
        a.demo = True

    os.makedirs(a.out, exist_ok=True)
    if a.demo:
        a.csv = os.path.join(a.out, "sample_data.csv")
        make_demo(a.csv)
    if not a.csv:
        ap.error("provide a CSV path or use --demo")

    df = load_csv(a.csv)
    overall, metrics, issues = profile(df, a.type_threshold)

    report = build_report(os.path.basename(a.csv), overall, metrics, issues)
    with open(os.path.join(a.out, "data_quality_report.md"), "w", encoding="utf-8") as f:
        f.write(report)
    metrics.to_csv(os.path.join(a.out, "quality_metrics.csv"), index=False)
    issues.to_csv(os.path.join(a.out, "invalid_records.csv"), index=False)

    print(report)
    print(f"Files written to: {os.path.abspath(a.out)}")


if __name__ == "__main__":
    sys.exit(main())