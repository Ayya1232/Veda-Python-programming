import json
import logging
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent

def load_config():
    with open(ROOT / "config.json", encoding="utf-8") as file:
        return json.load(file)

def setup_logging(log_path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=log_path, level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        force=True
    )

def main():
    cfg = load_config()
    output_dir = ROOT / cfg["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(ROOT / cfg["log_file"])

    source = ROOT / cfg["input_file"]
    df = pd.read_csv(source)
    logging.info("EXTRACT: rows=%d columns=%d", len(df), len(df.columns))
    df.to_csv(output_dir / cfg["output_files"]["raw"], index=False)

    missing_cols = [c for c in cfg["required_columns"] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Required columns missing: {missing_cols}")

    if cfg.get("strip_whitespace", True):
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].str.strip()

    for col, replacement in cfg.get("missing_values", {}).items():
        if col in df.columns:
            df[col] = df[col].fillna(replacement)

    if cfg.get("drop_duplicates", True):
        before = len(df)
        df = df.drop_duplicates()
        logging.info("TRANSFORM: duplicates_removed=%d", before - len(df))

    for col in cfg.get("uppercase_columns", []):
        if col in df.columns:
            df[col] = df[col].astype("string").str.upper()

    for col in cfg.get("numeric_columns", []):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df.to_csv(output_dir / cfg["output_files"]["transformed"], index=False)
    logging.info("TRANSFORM: rows=%d", len(df))

    valid = pd.Series(True, index=df.index)
    for col, minimum in cfg.get("min_values", {}).items():
        if col in df.columns:
            valid &= df[col].notna() & (df[col] >= minimum)

    rejected = df.loc[~valid].copy()
    final_df = df.loc[valid].copy()
    rejected.to_csv(output_dir / "rejected_rows.csv", index=False)
    final_df.to_csv(output_dir / cfg["output_files"]["final"], index=False)

    logging.info("VALIDATE: accepted=%d rejected=%d", len(final_df), len(rejected))
    logging.info("LOAD: final_file=%s", cfg["output_files"]["final"])
    print("ETL pipeline completed successfully.")
    print(f"Rows read: {len(pd.read_csv(source))}")
    print(f"Rows accepted: {len(final_df)}")
    print(f"Rows rejected: {len(rejected)}")
    print(f"Final output: {output_dir / cfg['output_files']['final']}")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("Pipeline failed")
        raise
