"""
Simple Command-Line To-Do List
--------------------------------
Learning goals: lists, loops, conditions, menu-driven programs.

Tasks are stored in a list of dictionaries, e.g.:
    {"id": 1, "title": "Buy milk", "done": False}
"""

tasks = []          # our "database": a list of task dicts
next_id = 1          # simple auto-incrementing id


def add_task():
    """Add a new task to the list."""
    global next_id
    title = input("Enter task description: ").strip()

    if not title:
        print("⚠️  Task cannot be empty. Nothing added.\n")
        return

    task = {"id": next_id, "title": title, "done": False}
    tasks.append(task)
    next_id += 1
    print(f"✅ Added task #{task['id']}: {title}\n")


def view_tasks():
    """Display all tasks with their status."""
    if not tasks:
        print("📭 No tasks yet. Add one!\n")
        return

    print("\n--- YOUR TASKS ---")
    for task in tasks:
        status = "✔ Done" if task["done"] else "◻ Pending"
        print(f"[{task['id']}] {task['title']}  —  {status}")
    print()


def update_task():
    """Update a task's title or mark it as done/undone."""
    view_tasks()
    if not tasks:
        return

    task_id = get_valid_id("Enter the task number to update: ")
    if task_id is None:
        return

    task = find_task(task_id)
    if task is None:
        print("⚠️  No task found with that number.\n")
        return

    print(f"Editing task #{task['id']}: {task['title']}")
    print("1. Edit title")
    print("2. Toggle done/undone")
    choice = input("Choose an option (1 or 2): ").strip()

    if choice == "1":
        new_title = input("Enter new title: ").strip()
        if new_title:
            task["title"] = new_title
            print("✅ Title updated.\n")
        else:
            print("⚠️  Title unchanged (empty input).\n")
    elif choice == "2":
        task["done"] = not task["done"]
        state = "done" if task["done"] else "pending"
        print(f"✅ Task marked as {state}.\n")
    else:
        print("⚠️  Invalid choice. No changes made.\n")


def delete_task():
    """Remove a task from the list."""
    view_tasks()
    if not tasks:
        return

    task_id = get_valid_id("Enter the task number to delete: ")
    if task_id is None:
        return

    task = find_task(task_id)
    if task is None:
        print("⚠️  No task found with that number.\n")
        return

    tasks.remove(task)
    print(f"🗑️  Deleted task #{task_id}.\n")


def find_task(task_id):
    """Return the task dict with the given id, or None."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


def get_valid_id(prompt):
    """Prompt for a task id and validate it's a number."""
    raw = input(prompt).strip()
    if not raw.isdigit():
        print("⚠️  Please enter a valid number.\n")
        return None
    return int(raw)


def print_menu():
    print("===== TO-DO LIST MENU =====")
    print("1. Add task")
    print("2. View tasks")
    print("3. Update task")
    print("4. Delete task")
    print("5. Exit")


def main():
    print("Welcome to your Command-Line To-Do List!\n")

    while True:
        print_menu()
        choice = input("Choose an option (1-5): ").strip()
        print()

        if choice == "1":
            add_task()
        elif choice == "2":
            view_tasks()
        elif choice == "3":
            update_task()
        elif choice == "4":
            delete_task()
        elif choice == "5":
            print("👋 Goodbye! Your tasks were not saved to disk.")
            break
        else:
            print("⚠️  Invalid choice. Please enter a number from 1 to 5.\n")


if __name__ == "__main__":
    main()