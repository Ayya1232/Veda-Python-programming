# Data Quality Report

**Source:** `sample_data.csv`

## 1. Summary

| Metric | Value |
|---|---|
| Rows | 202 |
| Columns | 8 |
| Completeness | 99.44% (9 missing cells) |
| Uniqueness | 99.01% (2 duplicate rows) |
| Validity (type conformity) | 99.88% |
| Rows with non-missing issues | 10 |
| **Overall quality score** | **99.44 / 100** |

## 2. Column Profile

| Column | Type | Missing | Complete % | Unique | Invalid types |
|---|---|---|---|---|---|
| customer_id | numeric | 0 | 100.0 | 200 | 0 |
| name | text | 0 | 100.0 | 200 | 0 |
| email | text | 8 | 96.04 | 192 | 0 |
| age | numeric | 0 | 100.0 | 60 | 1 |
| purchase_amount | numeric | 1 | 99.5 | 197 | 0 |
| signup_date | datetime | 0 | 100.0 | 200 | 1 |
| country | text | 0 | 100.0 | 3 | 0 |
| status | text | 0 | 100.0 | 1 | 0 |

## 3. Issues by Category

| Issue | Count |
|---|---|
| Missing value | 9 |
| Extreme outlier | 2 |
| Duplicate row | 2 |
| Invalid data type (expected numeric) | 1 |
| Impossible age (>120) | 1 |
| Negative value in non-negative field | 1 |
| Malformed email address | 1 |
| Date in the future | 1 |
| Invalid data type (expected datetime) | 1 |
| Leading/trailing whitespace | 1 |

## 4. Flags

- `age` has 1 value(s) that don't match type `numeric`.
- `signup_date` has 1 value(s) that don't match type `datetime`.
- `status` is constant (one unique value) and adds no information.
- 2 duplicate row(s) detected.

See `invalid_records.csv` for the row-level issue list.
