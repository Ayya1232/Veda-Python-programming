"""
Employee Salary Calculator
--------------------------
Calculates gross salary, deductions and net salary from configurable rules.

Structure:
    1. SALARY_RULES      - all business rules (change these, not the code)
    2. EMPLOYEES         - sample employee records
    3. Validation        - numeric input checks
    4. Calculation funcs - one small function per business rule
    5. Reporting         - prints a salary breakdown
"""

# ---------------------------------------------------------------------------
# 1. CONFIGURABLE SALARY RULES
# ---------------------------------------------------------------------------
SALARY_RULES = {
    "currency": "$",
    # Allowances (added to basic salary)
    "hra_percent": 20,             # housing allowance, % of basic
    "transport_allowance": 150,    # fixed monthly amount
    "overtime_rate_multiplier": 1.5,  # x normal hourly rate
    "working_hours_per_month": 160,
    # Deductions
    "pension_percent": 5,          # % of basic
    "health_insurance": 100,       # fixed monthly amount
    # Progressive income-tax slabs on gross: (upper_limit, rate %)
    # Each rate applies only to the portion of income inside that slab.
    "tax_slabs": [
        (1000, 0),
        (3000, 10),
        (6000, 20),
        (float("inf"), 30),
    ],
}

# ---------------------------------------------------------------------------
# 2. SAMPLE EMPLOYEE RECORDS
# ---------------------------------------------------------------------------
EMPLOYEES = [
    {"id": 101, "name": "Alice Johnson", "department": "Engineering",
     "basic_salary": 5000, "overtime_hours": 10, "bonus": 500},
    {"id": 102, "name": "Brian Smith", "department": "Marketing",
     "basic_salary": 3200, "overtime_hours": 0, "bonus": 0},
    {"id": 103, "name": "Carla Gomez", "department": "Finance",
     "basic_salary": 800, "overtime_hours": 5, "bonus": 100},
    {"id": 104, "name": "Dev Patel", "department": "Support",
     "basic_salary": "abc", "overtime_hours": 2, "bonus": 0},  # invalid on purpose
]


# ---------------------------------------------------------------------------
# 3. VALIDATION
# ---------------------------------------------------------------------------
def validate_number(value, field_name, allow_zero=True):
    """Return value as a float, or raise ValueError with a clear message."""
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a number, got {value!r}")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a number, got {value!r}")
    if number < 0 or (number == 0 and not allow_zero):
        raise ValueError(f"{field_name} must be "
                         f"{'zero or more' if allow_zero else 'greater than zero'}, got {number}")
    return number


def validate_employee(employee):
    """Validate the numeric fields of an employee record."""
    return {
        "basic_salary": validate_number(employee.get("basic_salary"), "basic_salary", allow_zero=False),
        "overtime_hours": validate_number(employee.get("overtime_hours", 0), "overtime_hours"),
        "bonus": validate_number(employee.get("bonus", 0), "bonus"),
    }


# ---------------------------------------------------------------------------
# 4. CALCULATION FUNCTIONS (pure business logic, no input/printing)
# ---------------------------------------------------------------------------
def calculate_hra(basic, rules):
    return basic * rules["hra_percent"] / 100


def calculate_overtime(basic, overtime_hours, rules):
    hourly_rate = basic / rules["working_hours_per_month"]
    return hourly_rate * rules["overtime_rate_multiplier"] * overtime_hours


def calculate_gross(basic, overtime_hours, bonus, rules):
    """Return gross salary and its component breakdown."""
    components = {
        "Basic salary": basic,
        "Housing allowance": calculate_hra(basic, rules),
        "Transport allowance": rules["transport_allowance"],
        "Overtime pay": calculate_overtime(basic, overtime_hours, rules),
        "Bonus": bonus,
    }
    return sum(components.values()), components


def calculate_tax(gross, slabs):
    """Progressive tax: each slab's rate applies only to income inside it."""
    tax, lower = 0.0, 0.0
    for upper, rate in slabs:
        if gross <= lower:
            break
        taxable_in_slab = min(gross, upper) - lower
        tax += taxable_in_slab * rate / 100
        lower = upper
    return tax


def calculate_deductions(basic, gross, rules):
    """Return total deductions and their component breakdown."""
    components = {
        "Income tax": calculate_tax(gross, rules["tax_slabs"]),
        "Pension": basic * rules["pension_percent"] / 100,
        "Health insurance": rules["health_insurance"],
    }
    return sum(components.values()), components


def calculate_salary(employee, rules=SALARY_RULES):
    """Full calculation for one employee. Returns a result dictionary."""
    data = validate_employee(employee)
    gross, earnings = calculate_gross(data["basic_salary"], data["overtime_hours"],
                                      data["bonus"], rules)
    total_deductions, deductions = calculate_deductions(data["basic_salary"], gross, rules)
    return {
        "earnings": earnings,
        "gross": gross,
        "deductions": deductions,
        "total_deductions": total_deductions,
        "net": max(gross - total_deductions, 0),
    }


# ---------------------------------------------------------------------------
# 5. REPORTING
# ---------------------------------------------------------------------------
def print_breakdown(employee, result, rules=SALARY_RULES):
    cur = rules["currency"]
    line = "=" * 44
    print(line)
    print(f"{employee['name']} (ID {employee['id']}) - {employee['department']}")
    print(line)
    print("EARNINGS")
    for label, amount in result["earnings"].items():
        print(f"  {label:<24}{cur}{amount:>12,.2f}")
    print(f"  {'GROSS SALARY':<24}{cur}{result['gross']:>12,.2f}")
    print("DEDUCTIONS")
    for label, amount in result["deductions"].items():
        print(f"  {label:<24}{cur}{amount:>12,.2f}")
    print(f"  {'TOTAL DEDUCTIONS':<24}{cur}{result['total_deductions']:>12,.2f}")
    print("-" * 44)
    print(f"  {'NET SALARY':<24}{cur}{result['net']:>12,.2f}")
    print()


def main():
    for employee in EMPLOYEES:
        try:
            result = calculate_salary(employee)
            print_breakdown(employee, result)
        except ValueError as error:
            print(f"Skipped {employee['name']} (ID {employee['id']}): {error}\n")


if __name__ == "__main__":
    main()