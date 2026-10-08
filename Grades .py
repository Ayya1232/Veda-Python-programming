"""Grade calculation module for the Student Result & Grade Management System."""

MAX_MARKS = 100
PASS_PERCENTAGE = 40


def validate_marks(marks, max_marks=MAX_MARKS):
    """Return the marks as a float if valid (0 to max_marks), else raise ValueError."""
    try:
        value = float(marks)
    except (TypeError, ValueError):
        raise ValueError("Marks must be a number.")
    if value < 0 or value > max_marks:
        raise ValueError(f"Marks must be between 0 and {max_marks}.")
    return value


def calculate_total(marks_dict):
    """Sum of all subject marks."""
    return sum(marks_dict.values())


def calculate_percentage(marks_dict, max_marks=MAX_MARKS):
    """Percentage across all subjects."""
    if not marks_dict:
        return 0.0
    return calculate_total(marks_dict) / (len(marks_dict) * max_marks) * 100


def calculate_grade(percentage):
    """Convert a percentage to a letter grade."""
    if percentage >= 90:
        return "A+"
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B"
    if percentage >= 60:
        return "C"
    if percentage >= 50:
        return "D"
    if percentage >= PASS_PERCENTAGE:
        return "E"
    return "F"


def get_result(percentage):
    """PASS / FAIL based on the overall percentage."""
    return "PASS" if percentage >= PASS_PERCENTAGE else "FAIL"


def summarize(marks_dict):
    """Return total, percentage, grade and result for one student's marks."""
    pct = calculate_percentage(marks_dict)
    return {
        "total": calculate_total(marks_dict),
        "percentage": round(pct, 2),
        "grade": calculate_grade(pct),
        "result": get_result(pct),
    }