"""
Student Records Program
------------------------
Stores student names and marks in synchronized lists and performs:
  - searching for a student's mark
  - sorting students by mark
  - finding the highest and lowest scores

Task 9 - Practice Python Lists With Student Records
"""


def add_student(names, marks, name, mark):
    """Add a new student and mark, keeping the two lists in sync."""
    names.append(name)
    marks.append(mark)


def search_student(names, marks, target_name):
    """
    Search for a student by name (case-insensitive).
    Returns the mark if found, otherwise None.
    """
    target_name = target_name.strip().lower()
    for name, mark in zip(names, marks):
        if name.lower() == target_name:
            return mark
    return None


def sort_students(names, marks, descending=True):
    """
    Return a new list of (name, mark) tuples sorted by mark.
    Does not modify the original lists.
    """
    combined = list(zip(names, marks))
    return sorted(combined, key=lambda pair: pair[1], reverse=descending)


def highest_score(names, marks):
    """Return (name, mark) for the student with the highest mark."""
    if not names:
        return None
    index = marks.index(max(marks))
    return names[index], marks[index]


def lowest_score(names, marks):
    """Return (name, mark) for the student with the lowest mark."""
    if not names:
        return None
    index = marks.index(min(marks))
    return names[index], marks[index]


def average_score(marks):
    """Return the class average, or 0 if there are no marks."""
    return sum(marks) / len(marks) if marks else 0


def print_all_students(names, marks):
    print("\n--- Student Records ---")
    for name, mark in zip(names, marks):
        print(f"{name:<15} {mark}")
    print("------------------------\n")


def main():
    names = []
    marks = []

    # Sample data
    sample_data = [
        ("Alice", 82),
        ("Brian", 67),
        ("Carla", 95),
        ("David", 58),
        ("Elena", 73),
    ]
    for name, mark in sample_data:
        add_student(names, marks, name, mark)

    while True:
        print("Student Record Menu")
        print("1. View all students")
        print("2. Add a student")
        print("3. Search for a student")
        print("4. Sort students by mark")
        print("5. Show highest and lowest score")
        print("6. Show class average")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            print_all_students(names, marks)

        elif choice == "2":
            name = input("Enter student name: ").strip()
            try:
                mark = float(input("Enter student mark: ").strip())
            except ValueError:
                print("Invalid mark. Please enter a number.\n")
                continue
            add_student(names, marks, name, mark)
            print(f"Added {name} with mark {mark}.\n")

        elif choice == "3":
            name = input("Enter student name to search: ").strip()
            result = search_student(names, marks, name)
            if result is None:
                print(f"No student named '{name}' found.\n")
            else:
                print(f"{name} scored {result}.\n")

        elif choice == "4":
            order = input("Sort descending? (y/n): ").strip().lower()
            descending = order != "n"
            ranked = sort_students(names, marks, descending)
            print("\n--- Sorted Students ---")
            for rank, (name, mark) in enumerate(ranked, start=1):
                print(f"{rank}. {name:<15} {mark}")
            print("-----------------------\n")

        elif choice == "5":
            if not names:
                print("No student records yet.\n")
            else:
                high_name, high_mark = highest_score(names, marks)
                low_name, low_mark = lowest_score(names, marks)
                print(f"Highest score: {high_name} ({high_mark})")
                print(f"Lowest score:  {low_name} ({low_mark})\n")

        elif choice == "6":
            print(f"Class average: {average_score(marks):.2f}\n")

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 7.\n")


if __name__ == "__main__":
    main()