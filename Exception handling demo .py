"""
Practice Exception Handling
============================
Task 18 - Python Programming Track

Demonstrates safe handling of:
  1. Invalid numeric input        -> ValueError
  2. Division by zero             -> ZeroDivisionError
  3. Missing values (dict/list)   -> KeyError / IndexError
  4. File not found                -> FileNotFoundError
  5. Invalid type operations       -> TypeError

Each case uses try / except / else / finally, catches SPECIFIC
exceptions (no bare `except:`), and prints a meaningful, user-facing
error message plus a short explanation of what went wrong.
"""


def divider(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------------------------------------------------------------
# Case 1: Invalid numeric input
# ---------------------------------------------------------------
def get_number(prompt, value):
    """Safely convert user input to an integer."""
    divider("Case 1: Invalid numeric input (ValueError)")
    try:
        print(f"{prompt}: '{value}'")
        number = int(value)
    except ValueError:
        print("Error: That is not a valid whole number.")
        print("Explanation: int() raises ValueError when the string "
              "cannot be parsed as an integer (e.g. letters, symbols, "
              "or an empty string).")
        return None
    else:
        print(f"Success: parsed number = {number}")
        return number
    finally:
        print("Finished attempt to read numeric input.")


# ---------------------------------------------------------------
# Case 2: Division by zero
# ---------------------------------------------------------------
def safe_divide(numerator, denominator):
    divider("Case 2: Division by zero (ZeroDivisionError)")
    try:
        print(f"Dividing {numerator} by {denominator}")
        result = numerator / denominator
    except ZeroDivisionError:
        print("Error: Cannot divide by zero.")
        print("Explanation: ZeroDivisionError is raised when the "
              "denominator of a division is 0. We catch it instead of "
              "letting the program crash.")
        return None
    else:
        print(f"Success: result = {result}")
        return result
    finally:
        print("Finished division attempt.")


# ---------------------------------------------------------------
# Case 3: Missing dictionary key
# ---------------------------------------------------------------
def get_user_email(users, username):
    divider("Case 3: Missing value in dictionary (KeyError)")
    try:
        print(f"Looking up email for user '{username}'")
        email = users[username]
    except KeyError:
        print(f"Error: No user named '{username}' was found.")
        print("Explanation: KeyError is raised when a dictionary key "
              "doesn't exist. Using .get() or a try/except avoids a "
              "hard crash and lets us respond gracefully.")
        return None
    else:
        print(f"Success: email = {email}")
        return email
    finally:
        print("Finished user lookup.")


# ---------------------------------------------------------------
# Case 4: Missing list index
# ---------------------------------------------------------------
def get_item_at(items, index):
    divider("Case 4: Missing value in list (IndexError)")
    try:
        print(f"Accessing index {index} of {items}")
        value = items[index]
    except IndexError:
        print(f"Error: Index {index} is out of range for this list.")
        print("Explanation: IndexError is raised when you try to "
              "access a list position that doesn't exist (e.g. index "
              "5 in a 3-item list).")
        return None
    else:
        print(f"Success: value = {value}")
        return value
    finally:
        print("Finished list access attempt.")


# ---------------------------------------------------------------
# Case 5: File not found
# ---------------------------------------------------------------
def read_config_file(path):
    divider("Case 5: Missing file (FileNotFoundError)")
    try:
        print(f"Opening file '{path}'")
        with open(path, "r") as f:
            contents = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{path}' does not exist.")
        print("Explanation: FileNotFoundError is raised when trying "
              "to open a file that isn't at the given path. Catching "
              "it lets the program suggest a fix instead of crashing.")
        return None
    else:
        print("Success: file read.")
        return contents
    finally:
        print("Finished file read attempt.")


# ---------------------------------------------------------------
# Case 6 (bonus): Invalid type operation
# ---------------------------------------------------------------
def add_values(a, b):
    divider("Case 6 (bonus): Invalid type combination (TypeError)")
    try:
        print(f"Adding {a!r} + {b!r}")
        result = a + b
    except TypeError:
        print(f"Error: Cannot add {type(a).__name__} and {type(b).__name__}.")
        print("Explanation: TypeError is raised when an operation "
              "(like +) is used on incompatible types, e.g. a string "
              "and an integer.")
        return None
    else:
        print(f"Success: result = {result}")
        return result
    finally:
        print("Finished add attempt.")


def main():
    # Case 1
    get_number("Enter your age", "twenty-five")
    get_number("Enter your age", "25")

    # Case 2
    safe_divide(10, 0)
    safe_divide(10, 2)

    # Case 3
    users = {"alice": "[email protected]", "bob": "[email protected]"}
    get_user_email(users, "charlie")
    get_user_email(users, "alice")

    # Case 4
    items = ["pen", "notebook", "eraser"]
    get_item_at(items, 10)
    get_item_at(items, 1)

    # Case 5
    read_config_file("does_not_exist.txt")

    # Case 6 (bonus)
    add_values("5", 3)
    add_values(5, 3)

    divider("All demonstrations complete")


if __name__ == "__main__":
    main()