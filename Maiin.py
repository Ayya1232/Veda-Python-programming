"""Student Result & Grade Management System - menu-driven CLI."""
import grade_calculator as gc
import student_manager as sm

MENU = """
========= STUDENT RESULT & GRADE MANAGEMENT =========
 1. Add student
 2. View all students
 3. Search student (roll no / name)
 4. Update student (name / marks)
 5. Delete student
 6. Performance summary
 7. Exit
"""


def ask_mark(subject):
    while True:
        mark = gc.parse_mark(input(f"  Marks for {subject} (0-{gc.MAX_MARKS}): ").strip())
        if mark is not None:
            return mark
        print(f"  Invalid! Enter a number between 0 and {gc.MAX_MARKS}.")


def ask_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  This field cannot be empty.")


def add_student_flow(students):
    roll_no = ask_nonempty("Roll number: ")
    if roll_no in students:
        print("A student with this roll number already exists.")
        return
    name = ask_nonempty("Name: ")
    while True:
        count = input("Number of subjects: ").strip()
        if count.isdigit() and int(count) > 0:
            count = int(count)
            break
        print("  Enter a positive whole number.")
    marks = {}
    for i in range(1, count + 1):
        subject = ask_nonempty(f"Subject {i} name: ")
        marks[subject] = ask_mark(subject)
    sm.add_student(students, roll_no, name, marks)
    print("Student added successfully!")


def view_all_flow(students):
    if not students:
        print("No records found.")
        return
    for roll_no, record in students.items():
        print("\n" + "-" * 45)
        print(sm.format_student(roll_no, record))


def search_flow(students):
    choice = input("Search by (1) Roll No or (2) Name? ").strip()
    if choice == "1":
        roll_no = input("Roll number: ").strip()
        record = sm.find_by_roll(students, roll_no)
        print("\n" + sm.format_student(roll_no, record) if record else "Student not found.")
    elif choice == "2":
        matches = sm.search_by_name(students, input("Name (or part of it): ").strip())
        if not matches:
            print("No matching students.")
        for roll_no, record in matches:
            print("\n" + "-" * 45)
            print(sm.format_student(roll_no, record))
    else:
        print("Invalid choice.")


def update_flow(students):
    roll_no = input("Roll number to update: ").strip()
    if roll_no not in students:
        print("Student not found.")
        return
    choice = input("Update (1) Name or (2) Marks? ").strip()
    if choice == "1":
        sm.update_name(students, roll_no, ask_nonempty("New name: "))
        print("Name updated.")
    elif choice == "2":
        subject = ask_nonempty("Subject (existing or new): ")
        sm.update_marks(students, roll_no, subject, ask_mark(subject))
        print("Marks updated.")
    else:
        print("Invalid choice.")


def delete_flow(students):
    roll_no = input("Roll number to delete: ").strip()
    if roll_no in students and input("Are you sure? (y/n): ").lower() == "y":
        sm.delete_student(students, roll_no)
        print("Student deleted.")
    else:
        print("Nothing deleted.")


def main():
    students = sm.load_students()
    actions = {
        "1": add_student_flow,
        "2": view_all_flow,
        "3": search_flow,
        "4": update_flow,
        "5": delete_flow,
        "6": lambda s: sm.print_summary(sm.performance_summary(s)),
    }
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "7":
            sm.save_students(students)
            print("Data saved. Goodbye!")
            break
        action = actions.get(choice)
        if action:
            action(students)
            sm.save_students(students)
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()