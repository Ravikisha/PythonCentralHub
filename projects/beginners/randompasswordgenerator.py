"""Random password generator — with `secrets`, not `random`.

`random` is seeded from the clock and its state can be reconstructed from a
handful of outputs. That is fine for a dice game and disqualifying for a
password. `secrets` draws from the operating system's CSPRNG, and switching
between them is a one-word edit, so there is no reason to get this wrong.

    python randompasswordgenerator.py            # a few passwords and their entropy
    python randompasswordgenerator.py --gui      # tkinter window, needs a display
    python randompasswordgenerator.py --test     # unit tests
"""

import math
import secrets
import string
import sys

ALPHABET = (string.ascii_lowercase + string.ascii_uppercase
            + string.digits + string.punctuation)

# The characters that look like each other in most fonts. Excluding them
# costs about 0.4 bits per character and saves the reader typing 1 for l.
AMBIGUOUS = "0Oo1lI"

POOLS = [
    string.ascii_lowercase,
    string.ascii_uppercase,
    string.digits,
    string.punctuation,
]


def generate(length: int = 16, no_ambig: bool = False,
             every_class: bool = True) -> str:
    """A password of `length` characters.

    With `every_class` the result is guaranteed to contain one character from
    each of the four pools -- which is what most password *rules* demand, and
    which very slightly *reduces* entropy by removing the all-lowercase
    outcomes from the sample space. The rules win anyway, because a password
    the site rejects has zero bits of useful strength.
    """
    pools = POOLS
    if no_ambig:
        pools = ["".join(c for c in pool if c not in AMBIGUOUS)
                 for pool in pools]
    alphabet = "".join(pools)

    if not every_class:
        return "".join(secrets.choice(alphabet) for _ in range(length))

    if length < len(pools):
        raise ValueError(
            f"length must be >= {len(pools)} to satisfy character-class rules")
    password = [secrets.choice(pool) for pool in pools]
    password += [secrets.choice(alphabet)
                 for _ in range(length - len(pools))]
    # Without the shuffle the first four characters are always
    # lower, upper, digit, symbol -- a pattern an attacker can exploit.
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


def entropy_bits(password: str) -> float:
    """Guessing cost in bits, assuming the attacker knows the pool sizes."""
    pool = 0
    if any(c.islower() for c in password):
        pool += 26
    if any(c.isupper() for c in password):
        pool += 26
    if any(c.isdigit() for c in password):
        pool += 10
    if any(c in string.punctuation for c in password):
        pool += len(string.punctuation)
    return len(password) * math.log2(max(pool, 1))


# A short stand-in for the EFF long list. The real one has 7,776 words (5 dice
# rolls' worth, 12.9 bits each); this has enough to demonstrate the method
# and the printed entropy is computed from whichever list is actually loaded.
WORDS = """
acorn amber anchor apron atlas bacon badge bagel banjo barge beacon beetle
bishop blazer bonus bounty branch bridle bronze bucket bugle cactus camera
candle canvas carbon cargo carrot cedar cello chapel cherry chisel cider
cinder clover cobalt cocoa comet copper coral cotton cougar cradle crayon
crest crimson crystal cyclone dagger dahlia daisy dapper dazzle decoy denim
dingo dolphin domino donkey dragon drifter dynamo eagle ember emerald engine
falcon fable fennel ferret fiddle finch flamingo flannel flint fossil galaxy
gadget garnet gazelle geyser ginger glacier glider granite gravel grotto
guitar gumbo hammock harbor hazel helmet heron hickory hollow hornet husky
igloo indigo ingot ivory jacket jaguar jasmine jersey jigsaw jubilee juniper
kayak kettle keystone kimono kitten koala lagoon lantern lattice lemon lever
lichen lilac linen lobster locket lumber lyric magnet mango maple marble
marlin meadow mellow meteor mimosa mineral minnow mitten monsoon mosaic
""".split()


def passphrase(n: int = 5, words: list[str] | None = None) -> str:
    """Diceware: n words joined by hyphens.

    Each word contributes log2(len(words)) bits, so the strength depends on
    the list, not on the punctuation. Five words from the real EFF list is
    64.6 bits; five from the short list below is less, and the program says
    which it used rather than quoting the number it wishes were true.
    """
    words = words or WORDS
    return "-".join(secrets.choice(words) for _ in range(n))


def passphrase_bits(n: int = 5, words: list[str] | None = None) -> float:
    words = words or WORDS
    return n * math.log2(len(set(words)))


def clear_later(seconds: int = 30) -> None:
    """Wipe the clipboard after a delay, so the password does not linger.

    A password sitting in the clipboard survives every later paste, every
    clipboard manager, and often a screenshot tool. `pyperclip` is optional
    here: the point stands with or without it installed.
    """
    import threading

    def wipe():
        try:
            import pyperclip
            pyperclip.copy("")
            print("clipboard cleared")
        except ImportError:
            pass

    timer = threading.Timer(seconds, wipe)
    timer.daemon = True                # never hold the process open
    timer.start()
    return timer


def gui():
    """The generator behind a tkinter window."""
    import tkinter as tk

    root = tk.Tk()
    root.title("Password Generator")
    length_var = tk.StringVar(value="16")
    out_var = tk.StringVar()

    def gen():
        try:
            out_var.set(generate(int(length_var.get())))
        except ValueError as exc:
            out_var.set(str(exc))

    tk.Entry(root, textvariable=length_var).pack()
    tk.Button(root, text="Generate", command=gen).pack()
    tk.Entry(root, textvariable=out_var, width=40).pack()
    root.mainloop()


def main():
    print(f"alphabet: {len(ALPHABET)} characters "
          f"({len(ALPHABET) - len(AMBIGUOUS)} without the ambiguous ones)\n")
    print(f"{'password':40} {'bits':>6}")
    print("-" * 48)
    for length in (8, 12, 16, 24):
        password = generate(length)
        print(f"{password:40} {entropy_bits(password):6.1f}")
    readable = generate(16, no_ambig=True)
    print(f"{readable:40} {entropy_bits(readable):6.1f}   no ambiguous chars")

    phrase = passphrase(5)
    print(f"\npassphrase from a {len(set(WORDS))}-word list:")
    print(f"  {phrase}")
    print(f"  {passphrase_bits(5):.1f} bits "
          f"(the full 7,776-word EFF list would give "
          f"{5 * math.log2(7776):.1f})")


if __name__ == "__main__":
    if "--test" in sys.argv:
        import unittest

        class TestGenerator(unittest.TestCase):
            def test_length_is_respected(self):
                for length in (4, 16, 64):
                    self.assertEqual(len(generate(length)), length)

            def test_every_class_present(self):
                for _ in range(200):
                    p = generate(8)
                    self.assertTrue(any(c.islower() for c in p))
                    self.assertTrue(any(c.isupper() for c in p))
                    self.assertTrue(any(c.isdigit() for c in p))
                    self.assertTrue(any(c in string.punctuation for c in p))

            def test_too_short_rejected(self):
                with self.assertRaises(ValueError):
                    generate(3)

            def test_no_ambiguous(self):
                for _ in range(200):
                    p = generate(16, no_ambig=True)
                    self.assertFalse(set(p) & set(AMBIGUOUS))

            def test_not_predictable_ordering(self):
                # If the shuffle were missing, position 0 would always be
                # lowercase. Over 200 draws that is worth catching.
                firsts = [generate(8)[0] for _ in range(200)]
                self.assertTrue(any(not c.islower() for c in firsts))

        unittest.main(argv=sys.argv[:1], exit=False)
    elif "--gui" in sys.argv:
        gui()
    else:
        main()
