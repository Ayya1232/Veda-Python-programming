"""
Shopping Bill Generator
------------------------
Accepts product names, quantities, and prices, then generates a formatted
bill with an itemized list, subtotal, discount, tax, and final amount.
"""

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TAX_RATE = 0.08          # 8% sales tax
DISCOUNT_THRESHOLD = 100 # subtotal must exceed this to qualify for a discount
DISCOUNT_RATE = 0.10     # 10% discount if threshold is met


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------
def get_products():
    """
    Prompt the user for products and return them as a list of dicts.
    Each product is structured data: {name, quantity, price, line_total}.
    """
    products = []

    while True:
        name = input("Product name (or press Enter to finish): ").strip()
        if name == "":
            break

        quantity = get_valid_quantity()
        price = get_valid_price()

        products.append({
            "name": name,
            "quantity": quantity,
            "price": price,
            "line_total": quantity * price,
        })

    return products


def get_valid_quantity():
    """Keep asking until a valid positive integer quantity is entered."""
    while True:
        raw = input("  Quantity: ").strip()
        try:
            quantity = int(raw)
            if quantity <= 0:
                print("  Quantity must be greater than zero. Try again.")
                continue
            return quantity
        except ValueError:
            print("  Invalid quantity. Please enter a whole number.")


def get_valid_price():
    """Keep asking until a valid non-negative price is entered."""
    while True:
        raw = input("  Unit price: ").strip()
        try:
            price = float(raw)
            if price < 0:
                print("  Price cannot be negative. Try again.")
                continue
            return price
        except ValueError:
            print("  Invalid price. Please enter a number (e.g. 4.99).")


# ---------------------------------------------------------------------------
# Calculations (kept separate from data collection and display)
# ---------------------------------------------------------------------------
def calculate_subtotal(products):
    return sum(item["line_total"] for item in products)


def calculate_discount(subtotal):
    if subtotal > DISCOUNT_THRESHOLD:
        return subtotal * DISCOUNT_RATE
    return 0.0


def calculate_tax(amount):
    return amount * TAX_RATE


def calculate_final_amount(subtotal, discount, tax):
    return subtotal - discount + tax


# ---------------------------------------------------------------------------
# Formatting / display
# ---------------------------------------------------------------------------
def format_currency(value):
    return f"${value:,.2f}"


def print_bill(products, subtotal, discount, tax, final_amount):
    width = 50
    print("\n" + "=" * width)
    print("SHOPPING BILL".center(width))
    print("=" * width)
    print(f"{'Item':<20}{'Qty':>6}{'Price':>10}{'Total':>14}")
    print("-" * width)

    for item in products:
        print(
            f"{item['name']:<20}"
            f"{item['quantity']:>6}"
            f"{format_currency(item['price']):>10}"
            f"{format_currency(item['line_total']):>14}"
        )

    print("-" * width)
    print(f"{'Subtotal:':<36}{format_currency(subtotal):>14}")
    print(f"{'Discount:':<36}{'-' + format_currency(discount):>14}")
    print(f"{'Tax (' + str(int(TAX_RATE * 100)) + '%):':<36}{format_currency(tax):>14}")
    print("-" * width)
    print(f"{'TOTAL DUE:':<36}{format_currency(final_amount):>14}")
    print("=" * width)


# ---------------------------------------------------------------------------
# Main program flow
# ---------------------------------------------------------------------------
def main():
    print("=== Shopping Bill Generator ===\n")

    products = get_products()

    if not products:
        print("No products entered. Exiting.")
        return

    subtotal = calculate_subtotal(products)
    discount = calculate_discount(subtotal)
    tax = calculate_tax(subtotal - discount)
    final_amount = calculate_final_amount(subtotal, discount, tax)

    print_bill(products, subtotal, discount, tax, final_amount)


if __name__ == "__main__":
    main()