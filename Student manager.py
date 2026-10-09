"""Student management: add, update, delete, search, view, and save/load."""
import json
import os

from Grade__calculator import calculate_result

DATA_FILE = "students.json"


# ---------- storage ----------
def load_students(path=DATA_FILE):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def save_students(students, path=DATA_FILE):
    with open(path, "w") as f:
        json.dump(students, f, indent=2)


# ---------- CRUD ----------
def add_student(students, roll_no, name, marks):
    if roll_no in students:
        return False
    students[roll_no] = {"name": name, "marks": marks}
    return True


def update_marks(students, roll_no, subject, mark):
    if roll_no not in students:
        return False
    students[roll_no]["marks"][subject] = mark
    return True


def update_name(students, roll_no, new_name):
    if roll_no not in students:
        return False
    students[roll_no]["name"] = new_name
    return True


def delete_student(students, roll_no):
    return students.pop(roll_no, None) is not None


# ---------- search ----------
def find_by_roll(students, roll_no):
    return students.get(roll_no)


def search_by_name(students, keyword):
    """Case-insensitive partial match. Returns list of (roll_no, record)."""
    keyword = keyword.lower()
    return [(r, s) for r, s in students.items() if keyword in s["name"].lower()]


# ---------- display ----------
def format_student(roll_no, record):
    result = calculate_result(record["marks"])
    lines = [
        f"Roll No : {roll_no}",
        f"Name    : {record['name']}",
        "Marks   :",
    ]
    for subject, mark in record["marks"].items():
        lines.append(f"   {subject:<15} {mark:>6.1f}")
    lines.append(
        f"Total: {result['total']:.1f} | Percentage: {result['percentage']}% "
        f"| Grade: {result['grade']} | {result['status']}"
    )
    return "\n".join(lines)


# ---------- performance summary ----------
def performance_summary(students):
    """Class-level statistics, or None if there are no students."""
    if not students:
        return None

    results = {r: calculate_result(s["marks"]) for r, s in students.items()}
    percentages = {r: res["percentage"] for r, res in results.items()}

    topper = max(percentages, key=percentages.get)
    lowest = min(percentages, key=percentages.get)
    passed = sum(1 for res in results.values() if res["status"] == "PASS")

    grade_counts = {}
    for res in results.values():
        grade_counts[res["grade"]] = grade_counts.get(res["grade"], 0) + 1

    # subject-wise averages
    subject_totals, subject_counts = {}, {}
    for s in students.values():
        for subject, mark in s["marks"].items():
            subject_totals[subject] = subject_totals.get(subject, 0) + mark
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
    subject_avg = {sub: subject_totals[sub] / subject_counts[sub] for sub in subject_totals}

    return {
        "count": len(students),
        "class_average": round(sum(percentages.values()) / len(percentages), 2),
        "topper": (students[topper]["name"], percentages[topper]),
        "lowest": (students[lowest]["name"], percentages[lowest]),
        "passed": passed,
        "failed": len(students) - passed,
        "pass_rate": round(passed / len(students) * 100, 1),
        "grade_counts": dict(sorted(grade_counts.items())),
        "subject_avg": {k: round(v, 2) for k, v in subject_avg.items()},
    }


def print_summary(summary):
    if summary is None:
        print("No student records available.")
        return
    print("\n===== PERFORMANCE SUMMARY =====")
    print(f"Total students : {summary['count']}")
    print(f"Class average  : {summary['class_average']}%")
    print(f"Topper         : {summary['topper'][0]} ({summary['topper'][1]}%)")
    print(f"Lowest         : {summary['lowest'][0]} ({summary['lowest'][1]}%)")
    print(f"Passed / Failed: {summary['passed']} / {summary['failed']} ({summary['pass_rate']}% pass rate)")
    print("Grade distribution:")
    for grade, n in summary["grade_counts"].items():
        print(f"   {grade:<3} {'#' * n} ({n})")
    print("Subject averages:")
    for subject, avg in summary["subject_avg"].items():
        print(f"   {subject:<15} {avg}")