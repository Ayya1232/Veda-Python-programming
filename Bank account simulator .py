"""Task 17: Menu-Driven Bank Account Simulator

Features: balance inquiry, deposit, withdrawal, transaction history.
State is kept in a single dict (`account`) that is passed to each function,
so there are no global variables.
"""

from datetime import datetime


def create_account(opening_balance=0.0):
    """Create the account state: a balance and a list of transactions."""
    account = {"balance": 0.0, "transactions": []}
    if opening_balance > 0:
        deposit(account, opening_balance, note="Opening balance")
    return account


def record(account, kind, amount, note=""):
    """Append a transaction (a dict) to the history list."""
    account["transactions"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": kind,
        "amount": amount,
        "balance_after": account["balance"],
        "note": note,
    })


def get_amount(prompt):
    """Keep asking until the user enters a valid positive number."""
    while True:
        raw = input(prompt).strip()
        try:
            amount = float(raw)
        except ValueError:
            print("  Invalid input: please enter a number (e.g. 50 or 25.75).")
            continue
        if amount != amount or amount in (float("inf"), float("-inf")):
            print("  Invalid input: please enter a real number.")
        elif amount <= 0:
            print("  Amount must be greater than zero.")
        else:
            return round(amount, 2)


def check_balance(account):
    print(f"\n  Current balance: ${account['balance']:,.2f}")


def deposit(account, amount, note=""):
    account["balance"] = round(account["balance"] + amount, 2)
    record(account, "DEPOSIT", amount, note)
    return True


def withdraw(account, amount):
    """Reject withdrawals that exceed the available balance."""
    if amount > account["balance"]:
        print(f"  Insufficient funds. Available balance: ${account['balance']:,.2f}")
        return False
    account["balance"] = round(account["balance"] - amount, 2)
    record(account, "WITHDRAWAL", amount)
    return True


def show_history(account):
    print("\n  --- Transaction History ---")
    if not account["transactions"]:
        print("  No transactions yet.")
        return
    print(f"  {'#':<3} {'Time':<20} {'Type':<11} {'Amount':>12} {'Balance':>12}")
    for i, t in enumerate(account["transactions"], start=1):
        print(f"  {i:<3} {t['time']:<20} {t['type']:<11} "
              f"{t['amount']:>12,.2f} {t['balance_after']:>12,.2f}")


def show_menu():
    print("\n==== Bank Account Simulator ====")
    print("1. Check balance")
    print("2. Deposit")
    print("3. Withdraw")
    print("4. Transaction history")
    print("5. Exit")


def main():
    account = create_account()
    while True:
        show_menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            check_balance(account)
        elif choice == "2":
            amount = get_amount("Deposit amount: $")
            deposit(account, amount)
            print(f"  Deposited ${amount:,.2f}. New balance: ${account['balance']:,.2f}")
        elif choice == "3":
            amount = get_amount("Withdrawal amount: $")
            if withdraw(account, amount):
                print(f"  Withdrew ${amount:,.2f}. New balance: ${account['balance']:,.2f}")
        elif choice == "4":
            show_history(account)
        elif choice == "5":
            print("Thank you for banking with us. Goodbye!")
            break
        else:
            print("  Invalid choice. Please enter a number from 1 to 5.")


if __name__ == "__main__":
    main()