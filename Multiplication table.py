"""
Multiplication Table Generator
--------------------------------
Accepts a number from the user and generates its multiplication table
up to a limit that the user specifies.

Practices:
- for loops
- range()
- formatted output (f-strings, alignment)
"""


def generate_multiplication_table(number, limit):
    """
    Print a formatted multiplication table for `number`
    from 1 up to and including `limit`.
    """
    print(f"\nMultiplication Table for {number} (up to {limit})")
    print("-" * 30)

    # range(1, limit + 1) so the table INCLUDES the limit itself
    for i in range(1, limit + 1):
        result = number * i
        # :>3 and :>4 right-align the numbers for a clean, column-like look
        print(f"{number:>3} x {i:<3} = {result:>4}")

    print("-" * 30)


def get_positive_int(prompt):
    """
    Keep asking the user until they enter a valid positive integer.
    Basic input validation so the program doesn't crash on bad input.
    """
    while True:
        value = input(prompt).strip()
        try:
            value = int(value)
            if value <= 0:
                print("Please enter a positive whole number.")
                continue
            return value
        except ValueError:
            print("That's not a valid whole number. Try again.")


def main():
    print("=== Multiplication Table Generator ===")

    while True:
        number = get_positive_int("Enter a number to generate its table for: ")
        limit = get_positive_int("Enter how far the table should go (e.g. 10): ")

        generate_multiplication_table(number, limit)

        again = input("\nGenerate another table? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()