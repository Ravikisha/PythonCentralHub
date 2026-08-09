"""Dice roller — one die, many dice, and D&D notation like `3d6+2`.

The interesting part is not the rolling, it is the shape of the results.
One d6 is flat: every face equally likely. Three d6 is not, and the histogram
printed at the end shows why -- there is one way to make 3 and twenty-seven
ways to make 10.

    python dicerolling.py           # rolls, notation, and a measured histogram
    python dicerolling.py --test    # unit tests
"""

import collections
import random
import re
import sys


def roll(sides: int = 6) -> int:
    """One die with any number of faces."""
    return random.randint(1, sides)


def roll_dice(count: int, sides: int = 6) -> list[int]:
    """`count` dice at once, returned individually so the caller can total."""
    return [random.randint(1, sides) for _ in range(count)]


def parse_and_roll(notation: str) -> tuple[list[int], int]:
    """Roll standard dice notation: `3d6`, `1d20+5`, `2d10-1`.

    Returning the individual rolls alongside the total is deliberate. A
    player who is told only "13" cannot see whether that was three average
    rolls or one critical and two disasters, and at a table that matters.
    """
    match = re.fullmatch(r"(\d+)d(\d+)([+-]\d+)?", notation.replace(" ", ""))
    if not match:
        raise ValueError(f"Bad notation: {notation}")
    count, sides, modifier = match.groups()
    if int(count) == 0 or int(sides) < 2:
        raise ValueError(f"Bad notation: {notation}")
    rolls = [random.randint(1, int(sides)) for _ in range(int(count))]
    total = sum(rolls) + (int(modifier) if modifier else 0)
    return rolls, total


def histogram(notation: str = "3d6", trials: int = 60_000) -> dict:
    """Roll `notation` many times and print how often each total came up."""
    counts = collections.Counter(parse_and_roll(notation)[1]
                                 for _ in range(trials))
    peak = max(counts.values())
    print(f"\n{notation}, {trials:,} rolls:\n")
    for total in sorted(counts):
        share = counts[total] / trials
        bar = "#" * round(share / (peak / trials) * 40)
        print(f"{total:>4} {share * 100:5.2f}%  {bar}")
    return dict(counts)


def main():
    random.seed(20260809)          # so the printed numbers are reproducible
    print(f"one d6:   {roll()}")
    print(f"one d20:  {roll(20)}")
    print(f"one d100: {roll(100)}")

    results = roll_dice(3)
    print(f"\nthree d6: {results}  total: {sum(results)}")

    for notation in ("3d6+2", "1d20+5", "2d10-1"):
        rolls, total = parse_and_roll(notation)
        print(f"{notation:>8} -> {rolls} = {total}")

    counts = histogram("3d6")
    trials = sum(counts.values())
    print(f"\n3 came up {counts.get(3, 0)} times, "
          f"10 came up {counts.get(10, 0)} times "
          f"-- {counts.get(10, 0) / max(counts.get(3, 1), 1):.0f}x more often, "
          f"against the {27 / 1:.0f}x the combinatorics predict "
          f"(27 ways to make 10, 1 way to make 3, out of 216).")
    print(f"mean {sum(k * v for k, v in counts.items()) / trials:.3f} "
          f"(exactly 10.5 in the limit)")


if __name__ == "__main__":
    if "--test" in sys.argv:
        import unittest

        class TestDice(unittest.TestCase):
            def test_roll_in_range(self):
                for sides in (2, 6, 20, 100):
                    for _ in range(500):
                        self.assertIn(roll(sides), range(1, sides + 1))

            def test_roll_dice_count(self):
                self.assertEqual(len(roll_dice(7)), 7)

            def test_notation(self):
                rolls, total = parse_and_roll("3d6+2")
                self.assertEqual(len(rolls), 3)
                self.assertEqual(total, sum(rolls) + 2)

            def test_negative_modifier(self):
                rolls, total = parse_and_roll("2d10-1")
                self.assertEqual(total, sum(rolls) - 1)

            def test_bad_notation_rejected(self):
                for bad in ("d6", "3x6", "3d", "0d6", "3d1", ""):
                    with self.assertRaises(ValueError):
                        parse_and_roll(bad)

        unittest.main(argv=sys.argv[:1], exit=False)
    else:
        main()
