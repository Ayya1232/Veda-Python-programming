"""
Student Grade Calculator
=========================
Track   : Python Programming
Task    : Level 1, Day 4 - Create a Student Grade Calculator

Description
-----------
Accepts marks for multiple subjects, calculates the total marks,
percentage, and assigns a grade based on predefined conditions.

Grade Criteria (out of 100 per subject)
----------------------------------------
    Percentage        Grade
    ----------------------------
    90 and above    ->  A+
    80 - 89.99      ->  A
    70 - 79.99      ->  B
    60 - 69.99      ->  C
    50 - 59.99      ->  D
    Below 50        ->  F (Fail)

Validation Rules
-----------------
- Marks for each subject must be a number.
- Marks must fall within the allowed range 0-100 (inclusive).
- Invalid entries are rejected and the user is re-prompted.
"""

MAX_MARK = 100
MIN_MARK = 0

# Grade boundaries defined once, used everywhere (avoids repeating
# the same if/elif chain in multiple places).
GRADE_BOUNDARIES = [
    (90, "A+"),
    (80, "A"),
    (70, "B"),
    (60, "C"),
    (50, "D"),
    (0,  "F"),
]


def get_valid_mark(subject: str) -> float:
    """Prompt the user until a valid mark (0-100) is entered for a subject."""
    while True:
        raw_value = input(f"Enter marks for {subject} (0-{MAX_MARK}): ").strip()
        try:
            mark = float(raw_value)
        except ValueError:
            print("  Invalid input. Please enter a numeric value.")
            continue

        if mark < MIN_MARK or mark > MAX_MARK:
            print(f"  Marks must be between {MIN_MARK} and {MAX_MARK}. Try again.")
            continue

        return mark


def calculate_grade(percentage: float) -> str:
    """Return the letter grade for a given percentage using the
    predefined grade boundaries (evaluated highest to lowest)."""
    for boundary, grade in GRADE_BOUNDARIES:
        if percentage >= boundary:
            return grade
    return "F"  # fallback, should not normally be reached


def calculate_results(marks: dict) -> dict:
    """Compute total, percentage, and grade once from the marks dict,
    so the same calculation isn't repeated by callers."""
    total = sum(marks.values())
    percentage = total / (len(marks) * MAX_MARK) * 100
    grade = calculate_grade(percentage)
    return {
        "marks": marks,
        "total": total,
        "percentage": round(percentage, 2),
        "grade": grade,
    }


def print_report(student_name: str, results: dict) -> None:
    """Nicely print a student's grade report."""
    print("\n" + "=" * 40)
    print(f"Grade Report for: {student_name}")
    print("=" * 40)
    for subject, mark in results["marks"].items():
        print(f"  {subject:<15}: {mark}")
    print("-" * 40)
    print(f"  {'Total Marks':<15}: {results['total']} / {len(results['marks']) * MAX_MARK}")
    print(f"  {'Percentage':<15}: {results['percentage']}%")
    print(f"  {'Grade':<15}: {results['grade']}")
    print("=" * 40)


def run_calculator():
    """Interactive entry point: collects subjects/marks for one student
    and displays their result."""
    print("=== Student Grade Calculator ===\n")

    student_name = input("Enter student name: ").strip() or "Student"

    try:
        num_subjects = int(input("How many subjects? ").strip())
        if num_subjects <= 0:
            raise ValueError
    except ValueError:
        print("Invalid number of subjects. Exiting.")
        return

    marks = {}
    for i in range(1, num_subjects + 1):
        subject = input(f"Enter name of subject {i}: ").strip() or f"Subject {i}"
        marks[subject] = get_valid_mark(subject)

    results = calculate_results(marks)
    print_report(student_name, results)


def run_sample_demo():
    """Runs the calculator on a few hard-coded sample students,
    useful as a deliverable / demo without manual input."""
    sample_students = {
        "Aisha Khan": {"Math": 92, "Science": 88, "English": 79},
        "Ravi Kumar": {"Math": 55, "Science": 61, "English": 48},
        "Sam Lee":    {"Math": 100, "Science": 95, "English": 97},
        "Priya Nair": {"Math": 40, "Science": 35, "English": 50},
    }

    print("=== Sample Student Results (Demo) ===")
    for name, marks in sample_students.items():
        results = calculate_results(marks)
        print_report(name, results)


if __name__ == "__main__":
    print("1. Run interactive calculator")
    print("2. Run sample demo (pre-loaded students)")
    choice = input("Choose an option (1/2): ").strip()

    if choice == "2":
        run_sample_demo()
    else:
        run_calculator()