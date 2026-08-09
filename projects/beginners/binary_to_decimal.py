"""Binary <-> decimal, then any base from 2 to 36, then two's complement.

`int(s, 2)` and `bin(n)` already do the first job in one call. The hand-written
versions are here because the point of the project is the algorithm: Horner's
method going one way, repeated division going the other. The built-ins stay in
the tests, as the oracle the hand-written code is checked against.

    python binary_to_decimal.py          # menu; unattended it plays DEMO_ANSWERS
    python binary_to_decimal.py --test   # check both directions against int()/bin()
"""

import sys
import unittest

DEMO_ANSWERS = iter(["1", "1011", "2", "11", "4", "255", "16", "3"])


def ask(prompt, default=""):
    """Read a line, or take the next scripted answer when nobody is there."""
    try:
        answer = input(prompt)
    except EOFError:
        answer = next(DEMO_ANSWERS, default)
        print(f"{answer}   (scripted demo answer)")
        return answer
    return answer.strip() or default


def bin_to_dec(s: str) -> int:
    """Horner's method: one multiply-add per digit, left to right.

    Reading `1011` gives 0 -> 1 -> 2 -> 5 -> 11. No powers, no exponent table;
    each step just doubles what came before and adds the new bit.
    """
    total = 0
    for digit in s:
        total = total * 2 + int(digit)
    return total


def dec_to_bin(n: int) -> str:
    """Repeated division, which produces the digits backwards."""
    if n == 0:
        return "0"
    if n < 0:
        return "-" + dec_to_bin(-n)
    out = []
    while n:
        out.append(str(n & 1))                # last bit
        n >>= 1                               # shift right
    return "".join(reversed(out))


DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def to_base(n: int, base: int) -> str:
    if not 2 <= base <= 36:
        raise ValueError("base must be 2..36")
    if n == 0:
        return "0"
    sign = "-" if n < 0 else ""
    n = abs(n)
    out = []
    while n:
        out.append(DIGITS[n % base])
        n //= base
    return sign + "".join(reversed(out))


def from_base(s: str, base: int) -> int:
    """The inverse of `to_base`, rejecting digits the base does not have.

    The validation loop is not decoration: without it `from_base("19", 8)`
    quietly returns 9, because `DIGITS.index("9")` is a perfectly good number
    -- it is just not a legal octal digit.
    """
    s = s.lower().strip()
    sign = 1
    if s.startswith("-"):
        sign, s = -1, s[1:]
    if not s:
        raise ValueError("empty string is not a number")
    for ch in s:
        if ch not in DIGITS or DIGITS.index(ch) >= base:
            raise ValueError(f"'{ch}' is not valid in base {base}")
    return sign * sum(DIGITS.index(c) * (base ** i)
                      for i, c in enumerate(reversed(s)))


def to_twos_complement(n: int, bits: int = 8) -> str:
    """How the machine actually stores a negative number.

    There is no sign bit to set; -5 is stored as the 8-bit number that, added
    to 5, wraps back to zero. That is why the conversion is an addition.
    """
    if not -(1 << (bits - 1)) <= n < (1 << (bits - 1)):
        raise ValueError(f"{n} does not fit in {bits} signed bits")
    if n < 0:
        n = (1 << bits) + n               # wrap into range
    return format(n, f"0{bits}b")


def from_twos_complement(s: str) -> int:
    bits = len(s)
    n = int(s, 2)
    return n - (1 << bits) if s[0] == "1" else n


def main():
    while True:
        print("\n1. Binary to decimal   2. Decimal to binary")
        print("3. Exit                4. Any base (2-36)")
        choice = ask("> ", "3").strip()
        if choice == "1":
            raw = ask("Binary: ", "1011").strip()
            if not raw or not all(c in "01" for c in raw):
                print("Use only 0s and 1s.")
                continue
            print(f"{raw} base 2 = {bin_to_dec(raw)} base 10")
        elif choice == "2":
            raw = ask("Decimal: ", "11").strip()
            try:
                n = int(raw)
            except ValueError:
                print("Not an integer.")
                continue
            print(f"{n} base 10 = {dec_to_bin(n)} base 2")
            print(f"  as 8-bit two's complement: {to_twos_complement(n)}")
        elif choice == "3":
            print("Bye.")
            break
        elif choice == "4":
            raw = ask("Decimal: ", "255").strip()
            base = ask("Target base (2-36): ", "16").strip()
            try:
                print(f"{int(raw)} base 10 = {to_base(int(raw), int(base))} "
                      f"base {base}")
            except ValueError as exc:
                print(f"Cannot convert: {exc}")
        else:
            print("Invalid choice.")


class TestConversions(unittest.TestCase):
    """The built-ins are the oracle; the hand-written code has to match them."""

    def test_bin_to_dec_matches_int(self):
        for n in range(256):
            self.assertEqual(bin_to_dec(format(n, "b")), n)

    def test_dec_to_bin_matches_bin(self):
        for n in range(256):
            self.assertEqual(dec_to_bin(n), bin(n)[2:])

    def test_base_round_trip(self):
        for base in range(2, 37):
            for n in (0, 1, 7, 255, 4095):
                self.assertEqual(from_base(to_base(n, base), base), n)

    def test_rejects_digit_outside_base(self):
        with self.assertRaises(ValueError):
            from_base("19", 8)

    def test_twos_complement(self):
        self.assertEqual(to_twos_complement(-5, 8), "11111011")
        self.assertEqual(from_twos_complement("11111011"), -5)
        for n in range(-128, 128):
            self.assertEqual(from_twos_complement(to_twos_complement(n)), n)


if __name__ == "__main__":
    if "--test" in sys.argv:
        unittest.main(argv=sys.argv[:1], exit=False)
    else:
        main()
