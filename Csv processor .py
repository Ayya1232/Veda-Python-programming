"""
CSV Data Processor
-------------------
Reads a CSV file of sales/employee data and calculates useful statistics:
totals, averages, highest values, and counts.

Design notes (per the task's mini-guide):
- Uses Python's built-in `csv` module (csv.DictReader) to read the file.
- Missing or invalid numeric values are detected and skipped from
  calculations, but tracked and reported separately so nothing is silently
  lost.
- Data-processing logic (the `process_rows` function) is kept separate
  from output formatting (the `format_report` / `write_report` functions),
  as suggested in the hints.

Usage:
    python csv_processor.py <input_csv> [output_report_txt]

If no arguments are given, it defaults to sales_data.csv -> summary_report.txt
in the same directory as this script.
"""

import csv
import sys
from pathlib import Path


def is_missing(value):
    """Return True if a CSV field is empty / missing."""
    return value is None or str(value).strip() == ""


def to_float(value):
    """
    Try to convert a value to float.
    Returns (float_value, ok) where ok is False if the value was
    missing or could not be parsed as a number.
    """
    if is_missing(value):
        return None, False
    try:
        return float(value), True
    except (TypeError, ValueError):
        return None, False


def to_int(value):
    """Same idea as to_float, but for whole-number fields like units sold."""
    if is_missing(value):
        return None, False
    try:
        return int(float(value)), True
    except (TypeError, ValueError):
        return None, False


def process_rows(rows):
    """
    Given a list of dict rows (from csv.DictReader), compute statistics.

    Expects columns: employee, region, sales_amount, units_sold, date
    (extra columns are ignored; missing columns are handled gracefully).

    Returns a dict of computed statistics, plus a list of problem rows
    for transparency about what was skipped and why.
    """
    total_sales = 0.0
    total_units = 0
    valid_sales_count = 0
    valid_units_count = 0

    highest_sale = None
    highest_sale_employee = None

    sales_by_employee = {}
    sales_by_region = {}
    row_count = 0
    problem_rows = []

    for i, row in enumerate(rows, start=2):  # start=2: row 1 is the header
        row_count += 1
        employee = (row.get("employee") or "Unknown").strip() or "Unknown"
        region = (row.get("region") or "Unknown").strip() or "Unknown"

        sale_value, sale_ok = to_float(row.get("sales_amount"))
        units_value, units_ok = to_int(row.get("units_sold"))

        if not sale_ok:
            reason = "missing sales_amount" if is_missing(row.get("sales_amount")) \
                else f"invalid sales_amount ({row.get('sales_amount')!r})"
            problem_rows.append((i, employee, reason))
        if not units_ok:
            reason = "missing units_sold" if is_missing(row.get("units_sold")) \
                else f"invalid units_sold ({row.get('units_sold')!r})"
            problem_rows.append((i, employee, reason))

        if sale_ok:
            total_sales += sale_value
            valid_sales_count += 1
            sales_by_employee[employee] = sales_by_employee.get(employee, 0.0) + sale_value
            sales_by_region[region] = sales_by_region.get(region, 0.0) + sale_value

            if highest_sale is None or sale_value > highest_sale:
                highest_sale = sale_value
                highest_sale_employee = employee

        if units_ok:
            total_units += units_value
            valid_units_count += 1

    average_sale = (total_sales / valid_sales_count) if valid_sales_count else 0.0
    average_units = (total_units / valid_units_count) if valid_units_count else 0.0

    top_employee = max(sales_by_employee, key=sales_by_employee.get) if sales_by_employee else None
    top_region = max(sales_by_region, key=sales_by_region.get) if sales_by_region else None

    return {
        "row_count": row_count,
        "valid_sales_count": valid_sales_count,
        "valid_units_count": valid_units_count,
        "skipped_count": len(problem_rows),
        "total_sales": total_sales,
        "average_sale": average_sale,
        "highest_sale": highest_sale,
        "highest_sale_employee": highest_sale_employee,
        "total_units": total_units,
        "average_units": average_units,
        "sales_by_employee": sales_by_employee,
        "sales_by_region": sales_by_region,
        "top_employee": top_employee,
        "top_region": top_region,
        "problem_rows": problem_rows,
    }


def read_csv(input_path):
    """Read the CSV file into a list of dict rows using csv.DictReader."""
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def format_report(stats, input_path):
    """Turn the stats dict into a human-readable report string."""
    lines = []
    lines.append("=" * 50)
    lines.append("CSV DATA PROCESSING SUMMARY REPORT")
    lines.append("=" * 50)
    lines.append(f"Source file: {input_path}")
    lines.append("")

    lines.append("-- Row Counts --")
    lines.append(f"Total data rows read:        {stats['row_count']}")
    lines.append(f"Rows with valid sales_amount: {stats['valid_sales_count']}")
    lines.append(f"Rows with valid units_sold:   {stats['valid_units_count']}")
    lines.append(f"Fields skipped (missing/invalid): {stats['skipped_count']}")
    lines.append("")

    lines.append("-- Sales Statistics --")
    lines.append(f"Total sales:   ${stats['total_sales']:,.2f}")
    lines.append(f"Average sale:  ${stats['average_sale']:,.2f}")
    if stats["highest_sale"] is not None:
        lines.append(
            f"Highest sale:  ${stats['highest_sale']:,.2f} "
            f"(by {stats['highest_sale_employee']})"
        )
    lines.append("")

    lines.append("-- Units Statistics --")
    lines.append(f"Total units sold:   {stats['total_units']}")
    lines.append(f"Average units sold: {stats['average_units']:.2f}")
    lines.append("")

    lines.append("-- Sales by Employee --")
    for employee, total in sorted(stats["sales_by_employee"].items(), key=lambda x: -x[1]):
        lines.append(f"  {employee:<20} ${total:,.2f}")
    if stats["top_employee"]:
        lines.append(f"Top performer: {stats['top_employee']}")
    lines.append("")

    lines.append("-- Sales by Region --")
    for region, total in sorted(stats["sales_by_region"].items(), key=lambda x: -x[1]):
        lines.append(f"  {region:<20} ${total:,.2f}")
    if stats["top_region"]:
        lines.append(f"Top region: {stats['top_region']}")
    lines.append("")

    if stats["problem_rows"]:
        lines.append("-- Data Quality Issues (skipped from calculations) --")
        for row_num, employee, reason in stats["problem_rows"]:
            lines.append(f"  Row {row_num} ({employee}): {reason}")
    else:
        lines.append("-- Data Quality --")
        lines.append("  No missing or invalid values found.")
    lines.append("")
    lines.append("=" * 50)

    return "\n".join(lines)


def write_report(report_text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)


def main():
    script_dir = Path(__file__).parent
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else script_dir / "sales_data.csv"
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else script_dir / "summary_report.txt"

    if not input_path.exists():
        print(f"Error: input file not found: {input_path}")
        sys.exit(1)

    rows = read_csv(input_path)
    stats = process_rows(rows)
    report = format_report(stats, input_path)

    write_report(report, output_path)
    print(report)
    print(f"\nReport written to: {output_path}")


if __name__ == "__main__":
    main()