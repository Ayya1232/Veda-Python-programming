"""
Simple Password Validator
--------------------------
Checks whether a password satisfies basic security requirements:
  - Minimum length
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character

Practices: strings, conditionals, loops, and basic input validation.
"""

import string

MIN_LENGTH = 8
SPECIAL_CHARACTERS = string.punctuation  # e.g. !@#$%^&*()_+-=...


def validate_password(password: str) -> list[str]:
    """
    Validate a password against a set of rules.

    Returns a list of failure messages. An empty list means the
    password is valid. The actual password is never included in
    any message or printed anywhere in this function.
    """
    errors = []

    if len(password) < MIN_LENGTH:
        errors.append(f"Password must be at least {MIN_LENGTH} characters long.")

    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False

    for char in password:
        if char in string.ascii_uppercase:
            has_upper = True
        elif char in string.ascii_lowercase:
            has_lower = True
        elif char in string.digits:
            has_digit = True
        elif char in SPECIAL_CHARACTERS:
            has_special = True

    if not has_upper:
        errors.append("Password must contain at least one uppercase letter.")
    if not has_lower:
        errors.append("Password must contain at least one lowercase letter.")
    if not has_digit:
        errors.append("Password must contain at least one number.")
    if not has_special:
        errors.append(f"Password must contain at least one special character ({SPECIAL_CHARACTERS}).")

    return errors


def is_valid_password(password: str) -> bool:
    """Convenience wrapper: True if the password passes all checks."""
    return len(validate_password(password)) == 0


def main():
    print("=== Simple Password Validator ===")
    print(f"Rules: min {MIN_LENGTH} chars, uppercase, lowercase, digit, special character.\n")

    while True:
        # getpass hides input where supported; falls back to input() otherwise.
        try:
            import getpass
            password = getpass.getpass("Enter a password to check (or 'quit' to exit): ")
        except Exception:
            password = input("Enter a password to check (or 'quit' to exit): ")

        if password.lower() == "quit":
            print("Goodbye!")
            break

        errors = validate_password(password)

        if not errors:
            # Never print or store the actual password.
            print("✅ Valid password! It meets all requirements.\n")
        else:
            print("❌ Invalid password. Issues found:")
            for e in errors:
                print(f"  - {e}")
            print()


if __name__ == "__main__":
    main()