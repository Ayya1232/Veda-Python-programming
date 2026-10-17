import csv
import json
from datetime import datetime
from pathlib import Path

# Personal Expense & Budget Tracker
# JSON is the primary data source; CSV is kept updated as an Excel-friendly export.

BASE_DIR = Path(__file__).resolve().parent
JSON_FILE = BASE_DIR / "expenses.json"
CSV_FILE = BASE_DIR / "expenses.csv"
BUDGET_FILE = BASE_DIR / "budget.json"

FIELDS = ["id", "date", "amount", "category", "description"]

def load_expenses():
    """Load expenses from JSON first, or import CSV if JSON does not exist."""
    if JSON_FILE.exists():
        try:
            with JSON_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, list):
                return data
            print("Warning: expenses.json has an unexpected format. Starting with an empty list.")
        except (json.JSONDecodeError, OSError) as error:
            print(f"Could not read expenses.json: {error}")

    if CSV_FILE.exists():
        try:
            with CSV_FILE.open("r", newline="", encoding="utf-8-sig") as file:
                rows = list(csv.DictReader(file))
            expenses = []
            for row in rows:
                expenses.append({
                    "id": int(row["id"]),
                    "date": row["date"],
                    "amount": float(row["amount"]),
                    "category": row["category"],
                    "description": row.get("description", "")
                })
            return expenses
        except (OSError, ValueError, KeyError) as error:
            print(f"Could not import expenses.csv: {error}")
    return []

def save_expenses(expenses):
    """Save the same expense records to JSON and CSV."""
    with JSON_FILE.open("w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=4, ensure_ascii=False)

    with CSV_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for expense in expenses:
            writer.writerow({field: expense.get(field, "") for field in FIELDS})


def load_budgets():
    if not BUDGET_FILE.exists():
        return {}
    try:
        with BUDGET_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read budget.json. Budgets will start empty.")
        return {}

def save_budgets(budgets):
    with BUDGET_FILE.open("w", encoding="utf-8") as file:
        json.dump(budgets, file, indent=4)


def next_id(expenses):
    return max((int(item.get("id", 0)) for item in expenses), default=0) + 1


def ask_date(prompt="Date (YYYY-MM-DD; press Enter for today): "):
    while True:
        value = input(prompt).strip()
        if not value:
            return datetime.today().strftime("%Y-%m-%d")
        try:
            return datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            print("Invalid date. Please use YYYY-MM-DD, for example 2026-10-17.")

def ask_amount(prompt="Amount (₹): "):
    while True:
        value = input(prompt).strip().replace(",", "")
        try:
            amount = float(value)
            if amount <= 0:
                print("Amount must be greater than zero.")
                continue
            return round(amount, 2)
        except ValueError:
            print("Enter a valid number, for example 250 or 250.50.")


def show_expenses(expenses):
    if not expenses:
        print("\nNo expenses found.")
        return
    print("\n" + "-" * 86)
    print(f"{'ID':<5} {'Date':<12} {'Amount (₹)':>13}  {'Category':<18} Description")
    print("-" * 86)
    for item in sorted(expenses, key=lambda x: (x["date"], int(x["id"])), reverse=True):
        print(f"{item['id']:<5} {item['date']:<12} {item['amount']:>13.2f}  "
              f"{item['category'][:18]:<18} {item['description']}")
    print("-" * 86)
    print(f"Total shown: ₹{sum(float(x['amount']) for x in expenses):.2f}")

def add_expense(expenses):
    print("\n--- Add Expense ---")
    date = ask_date()
    amount = ask_amount()
    category = input("Category (e.g., Food, Travel, Bills): ").strip()
    while not category:
        print("Category cannot be empty.")
        category = input("Category: ").strip()
    description = input("Description: ").strip()
    expenses.append({
        "id": next_id(expenses),
        "date": date,
        "amount": amount,
        "category": category.title(),
        "description": description
    })
    save_expenses(expenses)
    print("Expense added and saved to expenses.json and expenses.csv.")


def find_expense(expenses, expense_id):
    return next((item for item in expenses if int(item["id"]) == expense_id), None)

def edit_expense(expenses):
    if not expenses:
        print("No expenses to edit.")
        return
    show_expenses(expenses)
    try:
        expense_id = int(input("Enter the ID to edit: ").strip())
    except ValueError:
        print("Please enter a valid numeric ID.")
        return
    item = find_expense(expenses, expense_id)
    if not item:
        print("Expense ID not found.")
        return

    print("Press Enter to keep the current value.")
    new_date = input(f"Date [{item['date']}]: ").strip()
    if new_date:
        try:
            item["date"] = datetime.strptime(new_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            print("Invalid date. Date was not changed.")
    new_amount = input(f"Amount [{item['amount']:.2f}]: ").strip()
    if new_amount:
        try:
            value = float(new_amount.replace(",", ""))
            if value > 0:
                 item["amount"] = round(value, 2)
            else:
                print("Amount must be positive. Amount was not changed.")
        except ValueError:
            print("Invalid amount. Amount was not changed.")
    new_category = input(f"Category [{item['category']}]: ").strip()
    if new_category:
        item["category"] = new_category.title()
    new_description = input(f"Description [{item['description']}]: ").strip()
    if new_description:
        item["description"] = new_description
    save_expenses(expenses)
    print("Expense updated.")

def delete_expense(expenses):
    if not expenses:
        print("No expenses to delete.")
        return
    show_expenses(expenses)
    try:
        expense_id = int(input("Enter the ID to delete: ").strip())
    except ValueError:
        print("Please enter a valid numeric ID.")
        return
    item = find_expense(expenses, expense_id)
    if not item:
        print("Expense ID not found.")
        return
    confirm = input(f"Delete '{item['category']} - ₹{item['amount']:.2f}'? (y/n): ").strip().lower()
    if confirm == "y":
        expenses.remove(item)
        save_expenses(expenses)
        print("Expense deleted.")
    else:
        print("Deletion cancelled.")

def spending_summary(expenses):
    print("\n--- Spending Summary ---")
    month = input("Month (YYYY-MM; press Enter for current month): ").strip()
    if not month:
        month = datetime.today().strftime("%Y-%m")
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid month. Use YYYY-MM, for example 2026-10.")
        return

    monthly = [x for x in expenses if x["date"].startswith(month)]
    print(f"\nSummary for {month}")
    print(f"Number of expenses: {len(monthly)}")
    print(f"Total spent: ₹{sum(float(x['amount']) for x in monthly):.2f}")

    by_category = {}
    by_day = {}
    for item in monthly:
        by_category[item["category"]] = by_category.get(item["category"], 0) + float(item["amount"])
        by_day[item["date"]] = by_day.get(item["date"], 0) + float(item["amount"])

        print("\nCategory-wise totals:")
    if by_category:
        for category, total in sorted(by_category.items(), key=lambda pair: pair[1], reverse=True):
            print(f"  {category:<20} ₹{total:.2f}")
    else:
        print("  No expenses for this month.")

    print("\nDaily totals:")
    if by_day:
        for day, total in sorted(by_day.items()):
            print(f"  {day}: ₹{total:.2f}")
    else:
        print("  No expenses for this month.")

def set_monthly_budget(budgets):
    month = input("Budget month (YYYY-MM; press Enter for current month): ").strip()
    if not month:
        month = datetime.today().strftime("%Y-%m")
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid month. Use YYYY-MM.")
        return
    amount = ask_amount("Monthly budget (₹): ")
    budgets[month] = amount
    save_budgets(budgets)
    print(f"Budget for {month} set to ₹{amount:.2f}.")


def check_budget(expenses, budgets):
    month = input("Month to check (YYYY-MM; press Enter for current month): ").strip()
    if not month:
        month = datetime.today().strftime("%Y-%m")
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        print("Invalid month. Use YYYY-MM.")
        return
    spent = sum(float(x["amount"]) for x in expenses if x["date"].startswith(month))
    budget = budgets.get(month)
    print(f"\nBudget report for {month}")
    print(f"Spent: ₹{spent:.2f}")
    if budget is None:
        print("No budget set for this month. Choose option 7 to set one.")
        return
    remaining = float(budget) - spent
    print(f"Budget: ₹{float(budget):.2f}")
    print(f"Remaining: ₹{remaining:.2f}")
    if remaining < 0:
        print(f"Warning: You are over budget by ₹{abs(remaining):.2f}!")
    else:
        print("You are within your budget.")


def search_expenses(expenses):
    term = input("Search text (category or description): ").strip().lower()
    matches = [
        x for x in expenses
        if term in x["category"].lower() or term in x["description"].lower()
    ]
    show_expenses(matches)


def main():
    expenses = load_expenses()
    budgets = load_budgets()
    print("=" * 46)
    print(" PERSONAL EXPENSE & BUDGET TRACKER")
    print("=" * 46)
    print(f"Loaded {len(expenses)} expense record(s).")

    while True:
        print("""
Choose an option:
1. Add expense
2. View all expenses
3. Edit expense
4. Delete expense
5. Monthly spending summary
6. Search expenses
7. Set monthly budget
8. Check monthly budget
9. Exit
""")
        choice = input("Enter choice (1-9): ").strip()
        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            show_expenses(expenses)
        elif choice == "3":
            edit_expense(expenses)
        elif choice == "4":
            delete_expense(expenses)
        elif choice == "5":
            spending_summary(expenses)
        elif choice == "6":
            search_expenses(expenses)
        elif choice == "7":
            set_monthly_budget(budgets)
        elif choice == "8":
            check_budget(expenses, budgets)
        elif choice == "9":
            save_expenses(expenses)
            save_budgets(budgets)
            print("Data saved. Thank you for using the tracker!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 9.")


if __name__ == "__main__":
    main()
