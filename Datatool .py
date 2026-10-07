#!/usr/bin/env python3
"""datatool - a reusable command-line data analysis tool for CSV files.

Usage:  python datatool.py <csv_file> <command> [options]
Run `python datatool.py --help` or `python datatool.py <csv> <command> --help`.
"""
import argparse
import operator
import re
import sys
from pathlib import Path

import pandas as pd

OPS = {
    "==": operator.eq, "!=": operator.ne,
    ">=": operator.ge, "<=": operator.le,
    ">": operator.gt, "<": operator.lt,
}
AGGS = ["mean", "sum", "min", "max", "median", "count", "std"]


class ToolError(Exception):
    """User-facing error (bad file, bad column, bad option)."""


# ---------- validation / loading ----------
def load_csv(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.is_file():
        raise ToolError(f"File not found: {path}")
    try:
        df = pd.read_csv(p)
    except pd.errors.EmptyDataError:
        raise ToolError("The CSV file is empty.")
    except Exception as e:
        raise ToolError(f"Could not read CSV: {e}")
    if df.empty:
        raise ToolError("The CSV has headers but no rows.")
    return df


def require_columns(df: pd.DataFrame, cols) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ToolError(
            f"Column(s) not found: {', '.join(missing)}\n"
            f"Available columns: {', '.join(df.columns)}"
        )


def require_numeric(df: pd.DataFrame, col: str) -> None:
    if not pd.api.types.is_numeric_dtype(df[col]):
        raise ToolError(f"Column '{col}' is not numeric.")


# ---------- core logic (importable / testable) ----------
def apply_filters(df: pd.DataFrame, conditions) -> pd.DataFrame:
    for cond in conditions or []:
        m = re.match(r"^\s*(\w[\w ]*?)\s*(==|!=|>=|<=|>|<)\s*(.+?)\s*$", cond)
        if not m:
            raise ToolError(f"Bad filter '{cond}'. Use: \"column OP value\" e.g. \"age > 30\"")
        col, op, val = m.groups()
        require_columns(df, [col])
        if pd.api.types.is_numeric_dtype(df[col]):
            try:
                val = float(val)
            except ValueError:
                raise ToolError(f"Column '{col}' is numeric; '{val}' is not a number.")
        else:
            val = val.strip("'\"")
        df = df[OPS[op](df[col], val)]
    return df


def summarize(df: pd.DataFrame) -> str:
    lines = [f"Rows: {len(df)}   Columns: {len(df.columns)}", ""]
    info = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "missing": df.isna().sum(),
        "unique": df.nunique(),
    })
    lines.append(info.to_string())
    return "\n".join(lines)


def group_report(df, by, column, agg) -> pd.DataFrame:
    require_columns(df, [by] + ([column] if column else []))
    if agg == "count" and not column:
        return df.groupby(by).size().reset_index(name="count")
    if not column:
        raise ToolError(f"--agg {agg} needs --column.")
    if agg != "count":
        require_numeric(df, column)
    return df.groupby(by)[column].agg(agg).reset_index()


def stats_report(df, columns) -> pd.DataFrame:
    if columns:
        require_columns(df, columns)
        for c in columns:
            require_numeric(df, c)
        num = df[columns]
    else:
        num = df.select_dtypes("number")
    if num.empty:
        raise ToolError("No numeric columns to analyze.")
    d = num.describe().T
    d["median"] = num.median()
    d["missing"] = num.isna().sum()
    return d


# ---------- output ----------
def emit(result, output=None):
    text = result if isinstance(result, str) else result.to_string(index=False if "index" not in result.columns.names else True)
    print(text)
    if output and not isinstance(result, str):
        result.to_csv(output)
        print(f"\nSaved to {output}")


# ---------- CLI ----------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="datatool",
        description="Analyze any CSV file from the command line.",
        epilog="Examples:\n"
               "  datatool sales.csv summary\n"
               "  datatool sales.csv filter --where \"revenue > 500\" --where \"region == North\"\n"
               "  datatool sales.csv group --by region --column revenue --agg sum\n"
               "  datatool sales.csv stats --columns revenue units\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("csv", help="path to the CSV file")
    sub = p.add_subparsers(dest="command", required=True, metavar="command")

    sub.add_parser("columns", help="list column names")
    sub.add_parser("summary", help="rows, columns, dtypes, missing values, unique counts")

    h = sub.add_parser("head", help="show the first N rows")
    h.add_argument("-n", type=int, default=5, help="number of rows (default 5)")

    f = sub.add_parser("filter", help="filter rows with one or more conditions")
    f.add_argument("--where", action="append", required=True, metavar="COND",
                   help="condition like \"age > 30\" (repeatable; combined with AND)")
    f.add_argument("--select", nargs="+", metavar="COL", help="only show these columns")
    f.add_argument("--output", help="save result to this CSV")

    g = sub.add_parser("group", help="group rows and aggregate")
    g.add_argument("--by", required=True, help="column to group by")
    g.add_argument("--column", help="column to aggregate")
    g.add_argument("--agg", choices=AGGS, default="count", help="aggregation (default count)")
    g.add_argument("--where", action="append", metavar="COND", help="optional pre-filter")
    g.add_argument("--output", help="save result to this CSV")

    s = sub.add_parser("stats", help="statistical report for numeric columns")
    s.add_argument("--columns", nargs="+", metavar="COL", help="limit to these columns")
    s.add_argument("--corr", action="store_true", help="also print correlation matrix")
    s.add_argument("--where", action="append", metavar="COND", help="optional pre-filter")
    s.add_argument("--output", help="save result to this CSV")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        df = load_csv(args.csv)
        if args.command == "columns":
            print("\n".join(df.columns))
        elif args.command == "summary":
            print(summarize(df))
        elif args.command == "head":
            print(df.head(args.n).to_string(index=False))
        elif args.command == "filter":
            out = apply_filters(df, args.where)
            if args.select:
                require_columns(out, args.select)
                out = out[args.select]
            print(f"{len(out)} of {len(df)} rows match\n")
            emit(out, args.output)
        elif args.command == "group":
            out = group_report(apply_filters(df, args.where), args.by, args.column, args.agg)
            emit(out, args.output)
        elif args.command == "stats":
            sub_df = apply_filters(df, args.where)
            out = stats_report(sub_df, args.columns)
            print(out.round(2).to_string())
            if args.output:
                out.to_csv(args.output)
                print(f"\nSaved to {args.output}")
            if args.corr:
                num = sub_df[args.columns] if args.columns else sub_df.select_dtypes("number")
                print("\nCorrelation:\n" + num.corr().round(2).to_string())
        return 0
    except ToolError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())