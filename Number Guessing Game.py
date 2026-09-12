"""
Number Guessing Game
Level 1 - Day 5 - Task 5

The program picks a random number between 1 and 100.
The user keeps guessing until they find it, and gets a
high/low hint after each guess plus a final attempt count.
"""

import random


def play_game(lower=1, upper=100, max_attempts=None):
    """
    Runs one round of the guessing game.

    lower, upper   -> range the secret number is picked from
    max_attempts   -> optional cap on number of guesses (None = unlimited)
    """
    secret_number = random.randint(lower, upper)
    attempts = 0

    print(f"I'm thinking of a number between {lower} and {upper}.")
    if max_attempts:
        print(f"You have {max_attempts} attempts. Good luck!\n")
    else:
        print("Keep guessing until you get it. Good luck!\n")

    while True:
        # Stop early if we've used up all allowed attempts
        if max_attempts and attempts >= max_attempts:
            print(f"\nOut of attempts! The number was {secret_number}.")
            return attempts

        guess_input = input("Enter your guess: ").strip()

        if not guess_input.isdigit():
            print("Please enter a valid whole number.\n")
            continue

        guess = int(guess_input)
        attempts += 1

        if guess < secret_number:
            print("Too low! Try again.\n")
        elif guess > secret_number:
            print("Too high! Try again.\n")
        else:
            print(f"\n🎉 Correct! The number was {secret_number}.")
            print(f"It took you {attempts} attempt(s).")
            return attempts


if __name__ == "__main__":
    # Set max_attempts=10 (or any number) to limit attempts,
    # or leave it as None for unlimited guesses.
    play_game(lower=1, upper=100, max_attempts=10)