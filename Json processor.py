"""JSON Data Processor - Task 21
Reads employee data from a JSON file, then searches, filters and summarizes it.
"""
import json

INPUT_FILE = "employees.json"
OUTPUT_FILE = "results.json"
REQUIRED_KEYS = {"id", "name", "department", "salary", "skills"}


def load_data(path):
    """Read JSON from a file, with basic error handling."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"Error: '{path}' not found.")
    except json.JSONDecodeError as e:
        raise SystemExit(f"Error: '{path}' is not valid JSON ({e}).")


def validate(data):
    """Check the top-level key exists and split records into valid/invalid."""
    if "employees" not in data or not isinstance(data["employees"], list):
        raise SystemExit("Error: expected a list under the 'employees' key.")
    valid, invalid = [], []
    for emp in data["employees"]:
        missing = REQUIRED_KEYS - emp.keys()
        if missing:
            invalid.append({"record": emp.get("name", "?"), "missing": sorted(missing)})
        else:
            valid.append(emp)
    return valid, invalid


def search_by_name(employees, text):
    """Case-insensitive partial name search."""
    return [e for e in employees if text.lower() in e["name"].lower()]


def filter_by_department(employees, dept):
    return [e for e in employees if e["department"].lower() == dept.lower()]


def filter_by_min_salary(employees, minimum):
    return [e for e in employees if e["salary"] >= minimum]


def filter_by_skill(employees, skill):
    return [e for e in employees if skill.lower() in (s.lower() for s in e["skills"])]


def summarize(employees):
    """Count, average salary, and headcount per department."""
    salaries = [e["salary"] for e in employees]
    by_dept = {}
    for e in employees:
        d = by_dept.setdefault(e["department"], {"count": 0, "total_salary": 0})
        d["count"] += 1
        d["total_salary"] += e["salary"]
    for d in by_dept.values():
        d["average_salary"] = round(d["total_salary"] / d["count"], 2)
        del d["total_salary"]
    top = max(employees, key=lambda e: e["salary"])
    return {
        "total_employees": len(employees),
        "average_salary": round(sum(salaries) / len(salaries), 2),
        "highest_paid": {"name": top["name"], "salary": top["salary"]},
        "by_department": by_dept,
    }


def names(employees):
    return [e["name"] for e in employees]


def main():
    data = load_data(INPUT_FILE)
    employees, invalid = validate(data)

    results = {
        "company": data.get("company", "Unknown"),
        "search_name_'an'": names(search_by_name(employees, "an")),
        "filter_department_Engineering": names(filter_by_department(employees, "Engineering")),
        "filter_salary_at_least_4500": names(filter_by_min_salary(employees, 4500)),
        "filter_skill_Python": names(filter_by_skill(employees, "Python")),
        "summary": summarize(employees),
        "invalid_records": invalid,
    }

    # Nested access: use .get() because 'address' is optional
    results["cities"] = {
        e["name"]: e.get("address", {}).get("city", "N/A") for e in employees
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(json.dumps(results, indent=2))
    print(f"\nResults saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()