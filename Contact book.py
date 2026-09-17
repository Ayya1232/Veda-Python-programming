"""
Contact Book Using Dictionaries
--------------------------------
A simple command-line contact book that lets users Add, Search,
Update, and Delete contacts. Contacts are stored in a dictionary
where the KEY is the phone number (unique identifier) and the
VALUE is another dictionary holding the contact's details.

Data structure example:
{
    "9133938857": {"name": "Ayyappa", "email": "ayyappa@example.com"},
    "9876543210": {"name": "Ravi", "email": "ravi@example.com"}
}
"""

import json
import os

DATA_FILE = "contacts.json"


def load_contacts():
    """Load contacts from the JSON file if it exists, else return sample data."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    # Sample seed data (used only the very first time the program runs)
    return {
        "9133938857": {"name": "Ayyappa Talasila", "email": "ayyappa.talasila@gmail.com"},
        "9876543210": {"name": "Ravi Kumar", "email": "ravi.kumar@example.com"},
        "9000011122": {"name": "Sneha Reddy", "email": "sneha.reddy@example.com"},
    }


def save_contacts(contacts):
    """Persist the contacts dictionary to disk."""
    with open(DATA_FILE, "w") as f:
        json.dump(contacts, f, indent=4)


def is_valid_phone(phone):
    """Basic validation: digits only, 7-15 characters long."""
    return phone.isdigit() and 7 <= len(phone) <= 15


def add_contact(contacts):
    print("\n-- Add Contact --")
    phone = input("Enter phone number (used as ID): ").strip()

    if not is_valid_phone(phone):
        print("Invalid phone number. Use digits only (7-15 digits).")
        return

    if phone in contacts:
        print("A contact with this phone number already exists.")
        return

    name = input("Enter name: ").strip()
    email = input("Enter email: ").strip()

    contacts[phone] = {"name": name, "email": email}
    save_contacts(contacts)
    print(f"Contact '{name}' added successfully.")


def search_contact(contacts):
    print("\n-- Search Contact --")
    phone = input("Enter phone number to search: ").strip()

    contact = contacts.get(phone)
    if contact:
        print(f"Phone: {phone}")
        print(f"Name : {contact['name']}")
        print(f"Email: {contact['email']}")
    else:
        print("No contact found with that phone number.")


def update_contact(contacts):
    print("\n-- Update Contact --")
    phone = input("Enter phone number of contact to update: ").strip()

    if phone not in contacts:
        print("No contact found with that phone number.")
        return

    print("Leave a field blank to keep it unchanged.")
    name = input(f"New name [{contacts[phone]['name']}]: ").strip()
    email = input(f"New email [{contacts[phone]['email']}]: ").strip()

    if name:
        contacts[phone]["name"] = name
    if email:
        contacts[phone]["email"] = email

    save_contacts(contacts)
    print("Contact updated successfully.")


def delete_contact(contacts):
    print("\n-- Delete Contact --")
    phone = input("Enter phone number of contact to delete: ").strip()

    if phone in contacts:
        removed = contacts.pop(phone)
        save_contacts(contacts)
        print(f"Deleted contact '{removed['name']}'.")
    else:
        print("No contact found with that phone number.")


def list_contacts(contacts):
    print("\n-- All Contacts --")
    if not contacts:
        print("No contacts saved yet.")
        return
    for phone, info in contacts.items():
        print(f"{phone} | {info['name']} | {info['email']}")


def print_menu():
    print("\n===== CONTACT BOOK =====")
    print("1. Add Contact")
    print("2. Search Contact")
    print("3. Update Contact")
    print("4. Delete Contact")
    print("5. List All Contacts")
    print("6. Exit")


def main():
    contacts = load_contacts()
    save_contacts(contacts)  # ensure contacts.json exists on first run

    actions = {
        "1": add_contact,
        "2": search_contact,
        "3": update_contact,
        "4": delete_contact,
        "5": list_contacts,
    }

    while True:
        print_menu()
        choice = input("Choose an option (1-6): ").strip()

        if choice == "6":
            print("Goodbye!")
            break

        action = actions.get(choice)
        if action:
            action(contacts)
        else:
            print("Invalid option. Please choose between 1 and 6.")


if __name__ == "__main__":
    main()