"""Grade calculation module: validation, totals, percentage and grade."""

MAX_MARKS = 100

GRADE_SCALE = [  # (minimum percentage, grade)
    (90, "A+"),
    (80, "A"),
    (70, "B"),
    (60, "C"),
    (50, "D"),
    (40, "E"),
    (0, "F"),
]


def is_valid_mark(mark):
    """Return True if mark is a number between 0 and MAX_MARKS."""
    return isinstance(mark, (int, float)) and 0 <= mark <= MAX_MARKS


def parse_mark(text):
    """Convert user input to a float mark. Return None if invalid."""
    try:
        mark = float(text)
    except ValueError:
        return None
    return mark if is_valid_mark(mark) else None


def calculate_total(marks):
    """Sum of all subject marks. `marks` is a dict {subject: mark}."""
    return sum(marks.values())


def calculate_percentage(marks):
    if not marks:
        return 0.0
    return calculate_total(marks) / (len(marks) * MAX_MARKS) * 100


def get_grade(percentage):
    for minimum, grade in GRADE_SCALE:
        if percentage >= minimum:
            return grade
    return "F"


def is_pass(marks, pass_mark=40):
    """A student passes only if every subject is at or above pass_mark."""
    return bool(marks) and all(m >= pass_mark for m in marks.values())


def calculate_result(marks):
    """Return a dict with total, percentage, grade and pass/fail status."""
    percentage = calculate_percentage(marks)
    return {
        "total": calculate_total(marks),
        "percentage": round(percentage, 2),
        "grade": get_grade(percentage),
        "status": "PASS" if is_pass(marks) else "FAIL",
    }