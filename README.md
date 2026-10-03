# Task 26 — Configuration-Driven ETL Pipeline

## Requirements
Python 3.9+ and pandas.

## Run on Windows
1. Open PowerShell or Command Prompt in this folder.
2. Install dependency: `py -m pip install pandas`
3. Run: `py etl_pipeline.py`

If `py` is unavailable, use `python` instead.

## How it works
- Reads paths and transformation rules from `config.json`.
- Extracts `input/raw_data.csv`.
- Writes a raw copy, trims whitespace, fills selected missing text values,
  removes duplicate rows, uppercases department, and converts salary to numeric.
- Validates salary >= 0. Invalid rows are saved separately.
- Writes transformed and final CSVs and logs processing counts.

Change `config.json` to alter the source path, required columns, cleaning rules,
validation threshold, or output filenames without changing the pipeline code.
