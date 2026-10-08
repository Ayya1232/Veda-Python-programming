"""Student Result & Grade Management System - menu-driven CLI."""

import json
import os

import Grades 

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.json")

# students = { "101": {"name": "Asha", "class": "10-A", "marks": {"Maths": 90, ...}} }


# ---------- storage ----------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            print("Could not read saved data. Starting empty.")
    return {}


def save_data(students):
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=2)


# ---------- input helpers ----------
def ask(prompt):
    return input(prompt).strip()


def ask_marks(subject):
    while True:
        try:
            return Grades.validate_marks(ask(f"  Marks for {subject} (0-{Grades.MAX_MARKS}): "))
        except ValueError as e:
            print("  Invalid:", e)


def ask_existing_id(students):
    sid = ask("Enter student ID: ")
    if sid not in students:
        print("Student not found.")
        return None
    return sid


# ---------- features ----------
def add_student(students):
    sid = ask("Student ID: ")
    if not sid:
        print("ID cannot be empty.")
        return
    if sid in students:
        print("A student with this ID already exists.")
        return
    name = ask("Name: ")
    if not name:
        print("Name cannot be empty.")
        return
    cls = ask("Class/Section: ")
    marks = {}
    print("Enter subjects and marks (press Enter on subject name to finish).")
    while True:
        subject = ask("Subject name: ").title()
        if not subject:
            break
        if subject in marks:
            print("  Subject already added. Use 'Update marks' later to change it.")
            continue
        marks[subject] = ask_marks(subject)
    students[sid] = {"name": name, "class": cls, "marks": marks}
    save_data(students)
    print(f"Student {name} added.")


def update_student(students):
    sid = ask_existing_id(students)
    if not sid:
        return
    s = students[sid]
    print("1. Update name/class   2. Add or update a subject's marks   3. Remove a subject")
    choice = ask("Choice: ")
    if choice == "1":
        name = ask(f"New name [{s['name']}]: ")
        cls = ask(f"New class [{s['class']}]: ")
        if name:
            s["name"] = name
        if cls:
            s["class"] = cls
    elif choice == "2":
        subject = ask("Subject: ").title()
        if not subject:
            print("Subject cannot be empty.")
            return
        s["marks"][subject] = ask_marks(subject)
    elif choice == "3":
        subject = ask("Subject to remove: ").title()
        if s["marks"].pop(subject, None) is None:
            print("Subject not found.")
            return
    else:
        print("Invalid choice.")
        return
    save_data(students)
    print("Record updated.")


def delete_student(students):
    sid = ask_existing_id(students)
    if sid and ask(f"Delete {students[sid]['name']}? (y/n): ").lower() == "y":
        del students[sid]
        save_data(students)
        print("Student deleted.")


def print_report(sid, s):
    result = Grades.summarize(s["marks"])
    print("\n" + "=" * 44)
    print(f"ID: {sid}   Name: {s['name']}   Class: {s['class']}")
    print("-" * 44)
    if s["marks"]:
        for subject, m in s["marks"].items():
            print(f"  {subject:<20}{m:>6.1f} / {Grades.MAX_MARKS}")
    else:
        print("  No marks recorded.")
    print("-" * 44)
    max_total = len(s["marks"]) * Grades.MAX_MARKS
    print(f"  Total: {result['total']:.1f} / {max_total}")
    print(f"  Percentage: {result['percentage']}%")
    print(f"  Grade: {result['grade']}   Result: {result['result']}")
    print("=" * 44)


def view_student(students):
    sid = ask_existing_id(students)
    if sid:
        print_report(sid, students[sid])


def view_all(students):
    if not students:
        print("No students yet.")
        return
    print(f"\n{'ID':<8}{'Name':<20}{'Class':<10}{'Total':>8}{'%':>8}{'Grade':>7}{'Result':>8}")
    print("-" * 69)
    for sid, s in students.items():
        r = Grades.summarize(s["marks"])
        print(f"{sid:<8}{s['name']:<20}{s['class']:<10}{r['total']:>8.1f}"
              f"{r['percentage']:>8.2f}{r['grade']:>7}{r['result']:>8}")


def search_students(students):
    print("Search by: 1. ID   2. Name (partial)   3. Grade")
    choice = ask("Choice: ")
    found = []
    if choice == "1":
        sid = ask("ID: ")
        if sid in students:
            found.append(sid)
    elif choice == "2":
        term = ask("Name contains: ").lower()
        found = [sid for sid, s in students.items() if term in s["name"].lower()]
    elif choice == "3":
        g = ask("Grade (A+, A, B, C, D, E, F): ").upper()
        found = [sid for sid, s in students.items()
                 if Grades.summarize(s["marks"])["grade"] == g]
    else:
        print("Invalid choice.")
        return
    if not found:
        print("No matching students.")
        return
    for sid in found:
        print_report(sid, students[sid])


def performance_summary(students):
    # Only students with at least one mark count towards the summary.
    scored = {sid: s for sid, s in students.items() if s["marks"]}
    if not scored:
        print("No marks available for a summary.")
        return
    summaries = {sid: Grades.summarize(s["marks"]) for sid, s in scored.items()}
    pcts = [r["percentage"] for r in summaries.values()]
    passed = sum(1 for r in summaries.values() if r["result"] == "PASS")

    top = max(summaries, key=lambda k: summaries[k]["percentage"])
    low = min(summaries, key=lambda k: summaries[k]["percentage"])

    print("\n===== PERFORMANCE SUMMARY =====")
    print(f"Students with marks : {len(scored)}")
    print(f"Class average       : {sum(pcts) / len(pcts):.2f}%")
    print(f"Highest             : {scored[top]['name']} ({summaries[top]['percentage']}%)")
    print(f"Lowest              : {scored[low]['name']} ({summaries[low]['percentage']}%)")
    print(f"Pass percentage     : {passed / len(scored) * 100:.1f}% ({passed}/{len(scored)})")

    dist = {}
    for r in summaries.values():
        dist[r["grade"]] = dist.get(r["grade"], 0) + 1
    print("Grade distribution  :", ", ".join(f"{g}: {c}" for g, c in sorted(dist.items())))

    subj = {}
    for s in scored.values():
        for sub, m in s["marks"].items():
            subj.setdefault(sub, []).append(m)
    print("Subject averages    :")
    for sub, vals in sorted(subj.items()):
        print(f"  {sub:<20}{sum(vals) / len(vals):>6.2f}")

    print("\nRanking:")
    ranked = sorted(summaries, key=lambda k: summaries[k]["percentage"], reverse=True)
    for i, sid in enumerate(ranked, 1):
        print(f"  {i}. {scored[sid]['name']:<20}{summaries[sid]['percentage']:>6}%  "
              f"{summaries[sid]['grade']}")


# ---------- menu ----------
MENU = """
===== STUDENT RESULT & GRADE MANAGEMENT =====
1. Add student
2. Update student / marks
3. Delete student
4. View student report
5. View all students
6. Search students
7. Performance summary
0. Exit
"""

ACTIONS = {
    "1": add_student,
    "2": update_student,
    "3": delete_student,
    "4": view_student,
    "5": view_all,
    "6": search_students,
    "7": performance_summary,
}


def main():
    students = load_data()
    while True:
        print(MENU)
        choice = ask("Enter choice: ")
        if choice == "0":
            print("Goodbye!")
            break
        action = ACTIONS.get(choice)
        if action:
            action(students)
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()