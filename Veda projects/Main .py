"""Veda Technology Business & Service Management System - CLI entry point."""
from Base import RecordNotFound
from Modules import ServiceManager, ProgramManager, CustomerManager, InquiryManager
from Reports import summary_report
from Seed import seed

services, programs = ServiceManager(), ProgramManager()
customers, inquiries = CustomerManager(), InquiryManager()
seed(services, programs, customers, inquiries)


def show(rows):
    if not rows:
        print("  No records found.")
    for r in rows:
        print("  " + " | ".join(f"{k}: {v}" for k, v in r.items()))


def ask(prompt):
    return input(prompt).strip()


def safe(action):
    """Run an action, turning expected errors into friendly messages."""
    try:
        action()
    except (ValueError, RecordNotFound) as e:
        print(f"  Error: {e}")


def generic_menu(title, mgr, add_fields, filter_fields):
    while True:
        print(f"\n--- {title} ---\n1 List  2 Add  3 Search/Filter  4 Update status  5 Delete  0 Back")
        c = ask("Choose: ")
        if c == "0":
            return
        if c == "1":
            show(mgr.items)
        elif c == "2":
            safe(lambda: print("  Added:", mgr.add(**{f: _id(f, ask(f"{f}: ")) for f in add_fields})))
        elif c == "3":
            text = ask("Search text (blank for none): ")
            filters = {f: ask(f"Filter by {f} (blank to skip): ") for f in filter_fields}
            show(mgr.search(text, **filters))
        elif c == "4":
            safe(lambda: print("  Updated:", mgr.update(int(ask("id: ")), status=ask("new status: "))))
        elif c == "5":
            safe(lambda: (mgr.delete(int(ask("id: "))), print("  Deleted.")))
        else:
            print("  Invalid choice.")


def _id(field, value):
    if field == "customer_id":
        if not value.isdigit():
            raise ValueError("customer_id must be a number.")
        customers.get(int(value))          # must exist
        return int(value)
    return value


def enroll():
    safe(lambda: print("  Enrolled:", programs.enroll(int(ask("Program id: ")))))


def main():
    while True:
        print("\n=== Veda Technology Management System ===")
        print("1 Services  2 Programs  3 Customers  4 Inquiries/Requests  5 Enroll in program  6 Reports  0 Exit")
        c = ask("Choose: ")
        if c == "0":
            print("Goodbye!")
            break
        elif c == "1":
            generic_menu("Services", services, ["name", "category", "price"], ["category", "status"])
        elif c == "2":
            generic_menu("Programs", programs, ["name", "type", "seats"], ["type", "status"])
        elif c == "3":
            generic_menu("Customers", customers, ["name", "email"], [])
        elif c == "4":
            generic_menu("Inquiries", inquiries, ["customer_id", "subject", "kind"], ["kind", "status"])
        elif c == "5":
            enroll()
        elif c == "6":
            print(summary_report(services, programs, customers, inquiries))
        else:
            print("  Invalid choice.")


if __name__ == "__main__":
    main()