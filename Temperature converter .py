"""
Task 14 - Temperature Converter
Converts temperatures between Celsius, Fahrenheit, and Kelvin.

Conversion formulas
-------------------
Celsius    -> Fahrenheit : F = C * 9/5 + 32
Celsius    -> Kelvin     : K = C + 273.15
Fahrenheit -> Celsius    : C = (F - 32) * 5/9
Fahrenheit -> Kelvin     : K = (F - 32) * 5/9 + 273.15
Kelvin     -> Celsius    : C = K - 273.15
Kelvin     -> Fahrenheit : F = (K - 273.15) * 9/5 + 32

Absolute zero (lowest physically possible temperature):
0 K = -273.15 C = -459.67 F
"""

# ---------- Constants ----------
ABSOLUTE_ZERO = {
    "C": -273.15,
    "F": -459.67,
    "K": 0.0,
}

UNIT_NAMES = {
    "C": "Celsius",
    "F": "Fahrenheit",
    "K": "Kelvin",
}


# ---------- Conversion functions ----------
def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32


def celsius_to_kelvin(c):
    return c + 273.15


def fahrenheit_to_celsius(f):
    return (f - 32) * 5 / 9


def fahrenheit_to_kelvin(f):
    return celsius_to_kelvin(fahrenheit_to_celsius(f))


def kelvin_to_celsius(k):
    return k - 273.15


def kelvin_to_fahrenheit(k):
    return celsius_to_fahrenheit(kelvin_to_celsius(k))


# Lookup table: (from_unit, to_unit) -> function
CONVERTERS = {
    ("C", "F"): celsius_to_fahrenheit,
    ("C", "K"): celsius_to_kelvin,
    ("F", "C"): fahrenheit_to_celsius,
    ("F", "K"): fahrenheit_to_kelvin,
    ("K", "C"): kelvin_to_celsius,
    ("K", "F"): kelvin_to_fahrenheit,
}


def convert(value, from_unit, to_unit):
    """Convert `value` from one unit to another. Returns the converted number."""
    if from_unit == to_unit:
        return value
    return CONVERTERS[(from_unit, to_unit)](value)


def symbol(unit):
    """Kelvin is written 'K' (no degree sign); the others use '°'."""
    return "K" if unit == "K" else f"°{unit}"


# ---------- Input helpers / validation ----------
def is_physically_valid(value, unit):
    """A temperature can't be below absolute zero."""
    return value >= ABSOLUTE_ZERO[unit]


def ask_unit(prompt):
    """Keep asking until the user enters C, F, or K."""
    while True:
        unit = input(prompt).strip().upper()
        if unit in UNIT_NAMES:
            return unit
        print("  Invalid unit. Please enter C, F, or K.")


def ask_temperature(unit):
    """Keep asking until the user enters a valid number above absolute zero."""
    while True:
        raw = input(f"Enter temperature in {UNIT_NAMES[unit]} ({symbol(unit)}): ").strip()
        try:
            value = float(raw)
        except ValueError:
            print("  That's not a number. Try again (e.g. 36.6).")
            continue

        if not is_physically_valid(value, unit):
            print(
                f"  Below absolute zero! Minimum for {UNIT_NAMES[unit]} "
                f"is {ABSOLUTE_ZERO[unit]:.2f}."
            )
            continue
        return value


# ---------- Main program ----------
def main():
    print("=== Temperature Converter ===")
    print("Units: C = Celsius, F = Fahrenheit, K = Kelvin\n")

    while True:
        from_unit = ask_unit("Convert FROM (C/F/K): ")
        to_unit = ask_unit("Convert TO   (C/F/K): ")
        value = ask_temperature(from_unit)

        result = convert(value, from_unit, to_unit)
        print(
            f"\n  {value:.2f} {symbol(from_unit)} = {result:.2f} {symbol(to_unit)}\n"
        )

        again = input("Convert another? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break
        print()


if __name__ == "__main__":
    main()