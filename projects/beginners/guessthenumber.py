"""Guess the number -- and a measurement of whether six guesses is enough.

The game gives the player 6 attempts at a number from 1 to 20. Whether that
is generous or stingy is not a matter of opinion: binary search needs at most
ceil(log2(20)) = 5 guesses, so a player who halves the range every time
cannot lose. The demo at the bottom plays both strategies 20,000 times and
prints the win rates.

    python guessthenumber.py           # play; unattended it runs the demo
    python guessthenumber.py --demo    # strategy comparison
    python guessthenumber.py --test    # unit tests
"""

import math
import random
import statistics
import sys

LOW, HIGH = 1, 20
MAX_GUESSES = 6


def ask(prompt="", default=""):
    """Read a line, or fall back to `default` when nobody is there to type."""
    try:
        return input(prompt).strip() or default
    except EOFError:
        print(f"{default}   (no input available, using the default)")
        return default


def ask_number(prompt="", default=1, low=LOW, high=HIGH):
    """Keep asking until the answer is a number inside the range.

    `int(input())` raises ValueError on "ten" and happily accepts 500 for a
    game about 1 to 20. Both are the same bug -- trusting the string -- and
    both cost the player a turn they did not use.
    """
    while True:
        raw = ask(prompt, str(default))
        try:
            value = int(raw)
        except ValueError:
            print(f"'{raw}' is not a whole number.")
            continue
        if not low <= value <= high:
            print(f"Pick something between {low} and {high}.")
            continue
        return value


def play(secret=None, name=None):
    """One game. Returns the number of guesses used, or None on a loss."""
    secret = random.randint(LOW, HIGH) if secret is None else secret
    if name is None:
        print("Hello, what is your name?")
        name = ask("", "Player")
    print(f"Well, {name}, I am thinking of a number between "
          f"{LOW} and {HIGH}.")

    for taken in range(1, MAX_GUESSES + 1):
        print(f"Take a guess. You have {MAX_GUESSES - taken + 1} left.")
        guess = ask_number("", (LOW + HIGH) // 2)
        if guess < secret:
            print("Your guess is too low.")
        elif guess > secret:
            print("Your guess is too high.")
        else:
            print(f"Good job, {name}! You guessed my number in "
                  f"{taken} guesses.")
            return taken
    print(f"Nope. The number I was thinking of was {secret}.")
    return None


def play_binary(secret):
    """Halve the range each time. Returns the guess count."""
    low, high = LOW, HIGH
    for taken in range(1, MAX_GUESSES + 1):
        guess = (low + high) // 2
        if guess == secret:
            return taken
        if guess < secret:
            low = guess + 1
        else:
            high = guess - 1
    return None


def play_random(secret):
    """Guess at random from the numbers not yet tried, ignoring the hints."""
    remaining = list(range(LOW, HIGH + 1))
    random.shuffle(remaining)
    for taken, guess in enumerate(remaining[:MAX_GUESSES], start=1):
        if guess == secret:
            return taken
    return None


def play_linear(secret):
    """Count up from 1. Correct, and hopeless past the sixth number."""
    for taken, guess in enumerate(range(LOW, HIGH + 1), start=1):
        if taken > MAX_GUESSES:
            return None
        if guess == secret:
            return taken
    return None


def measure(strategy, trials=20_000):
    random.seed(20260809)
    results = [strategy(random.randint(LOW, HIGH)) for _ in range(trials)]
    wins = [r for r in results if r is not None]
    return {
        "win_rate": len(wins) / trials,
        "mean_guesses": statistics.mean(wins) if wins else float("nan"),
        "worst": max(wins) if wins else None,
    }


def demo():
    bound = math.ceil(math.log2(HIGH - LOW + 1))
    print(f"{HIGH - LOW + 1} numbers, {MAX_GUESSES} guesses. "
          f"Binary search needs at most {bound}.\n")
    print(f"{'strategy':22} {'wins':>7} {'mean guesses':>14} {'worst':>7}")
    print("-" * 54)
    for label, strategy in (("binary search", play_binary),
                            ("random, no repeats", play_random),
                            ("count up from 1", play_linear)):
        stats = measure(strategy)
        print(f"{label:22} {stats['win_rate']:6.1%} "
              f"{stats['mean_guesses']:14.2f} {stats['worst']:>7}")
    print("\nBinary search never loses, because 6 guesses is one more than it")
    print("needs. The hints -- higher, lower -- are the entire game: a player")
    print("who ignores them is left drawing from 20 numbers with 6 tickets.")


if __name__ == "__main__":
    if "--test" in sys.argv:
        import unittest

        class TestGame(unittest.TestCase):
            def test_binary_search_always_wins(self):
                for secret in range(LOW, HIGH + 1):
                    self.assertIsNotNone(play_binary(secret))

            def test_binary_search_within_bound(self):
                bound = math.ceil(math.log2(HIGH - LOW + 1))
                worst = max(play_binary(s) for s in range(LOW, HIGH + 1))
                self.assertLessEqual(worst, bound)

            def test_linear_loses_past_the_limit(self):
                self.assertIsNone(play_linear(HIGH))
                self.assertEqual(play_linear(LOW), 1)

        unittest.main(argv=sys.argv[:1], exit=False)
    elif "--demo" in sys.argv:
        demo()
    else:
        play()
        print()
        demo()
