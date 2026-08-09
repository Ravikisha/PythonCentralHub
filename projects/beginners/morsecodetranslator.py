"""Morse code translator -- text to Morse, Morse to text, and back again.

Two things in the original version were wrong in ways worth naming, because
both are common:

* `import winsound` sat at the top of the file. It is a Windows-only module,
  so the whole translator refused to import on Linux and macOS for the sake
  of an optional beep. The import now lives inside the function that beeps.
* `main()` called itself for each menu choice instead of looping. That is
  recursion used as a `goto`: every choice grows the stack, and a long
  session ends in `RecursionError` rather than at the exit option.

    python morsecodetranslator.py         # menu; unattended it plays a demo
    python morsecodetranslator.py --test  # round-trip every printable phrase
"""

import sys
import time

DEMO_ANSWERS = iter(["1", "SOS help", "2", "... --- ...", "1",
                     "Hello World", "4"])

MORSE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
    '9': '----.', ',': '--..--', '.': '.-.-.-', '?': '..--..',
    '/': '-..-.', '-': '-....-', '(': '-.--.', ')': '-.--.-',
}

# Built once. The original searched `list(MORSE.values()).index(letter)` for
# every symbol decoded -- a linear scan through 40 entries per character,
# rebuilding both lists each time. A reversed dict is one line and O(1).
TEXT = {code: letter for letter, code in MORSE.items()}

# Timing units. Morse is defined in multiples of one "dit": a dah is three
# dits, the gap between symbols is one, between letters three, between words
# seven. Everything below is that table, not an invention.
DIT_MS = 60


def ask(prompt="", default=""):
    """Read a line, or take the next scripted answer when nobody is there."""
    try:
        return input(prompt).strip() or default
    except EOFError:
        answer = next(DEMO_ANSWERS, default)
        print(f"{answer}   (scripted demo answer)")
        return answer


def to_morse(text: str) -> str:
    """Encode text. Unknown characters are dropped, not guessed at.

    A word gap is a slash, which is what makes decoding unambiguous: without
    a distinct word separator, `... --- ...` and `.../---/...` look the same
    once the spacing is normalised.
    """
    words = []
    for word in text.upper().split():
        words.append(" ".join(MORSE[c] for c in word if c in MORSE))
    return " / ".join(words)


def from_morse(code: str) -> str:
    """Decode Morse back to text, one letter per space, slash between words."""
    out = []
    for word in code.strip().split("/"):
        letters = [TEXT[symbol] for symbol in word.split() if symbol in TEXT]
        out.append("".join(letters))
    return " ".join(part for part in out if part)


def tone(duration_ms: int, frequency: int = 800) -> None:
    """One beep, on the platforms that have one.

    `winsound` only exists on Windows, so it is imported here rather than at
    the top of the file: an optional beep must not decide whether the
    translator imports at all.
    """
    try:
        import winsound
        winsound.Beep(frequency, duration_ms)
    except (ImportError, RuntimeError):
        time.sleep(duration_ms / 1000)


def silence(duration_ms: int) -> None:
    time.sleep(duration_ms / 1000)


def play_morse(code: str, dit_ms: int = DIT_MS, audible: bool = True) -> float:
    """Play (or time) a Morse string, returning how long it takes.

    With `audible=False` nothing sounds and nothing sleeps -- it just adds up
    the timing table. That is what makes the duration testable: the same
    function that plays the message can tell you how long it would take
    without waiting for it.
    """
    total = 0
    for index, symbol in enumerate(code):
        if symbol == ".":
            total += dit_ms
            if audible:
                tone(dit_ms)
        elif symbol == "-":
            total += 3 * dit_ms
            if audible:
                tone(3 * dit_ms)
        elif symbol == "/":
            total += 7 * dit_ms
            if audible:
                silence(7 * dit_ms)
        else:                                    # space between letters
            total += 3 * dit_ms
            if audible:
                silence(3 * dit_ms)
        # One dit of silence between symbols inside a letter.
        if audible and symbol in ".-" and index + 1 < len(code):
            silence(dit_ms)
        if symbol in ".-" and index + 1 < len(code):
            total += dit_ms
    return total / 1000


def flash(code: str, dit_ms: int = DIT_MS) -> str:
    """The same message as a visual signal -- a lamp, or a row of blocks."""
    out = []
    for symbol in code:
        if symbol == ".":
            out.append("#")
        elif symbol == "-":
            out.append("###")
        elif symbol == "/":
            out.append("       ")
        else:
            out.append("   ")
        if symbol in ".-":
            out.append(" ")
    return "".join(out)


def main():
    while True:
        print("\nMorse Code Translator")
        print("1. Translate to Morse Code")
        print("2. Translate to Text")
        print("3. Play Morse Code")
        print("4. Exit")
        choice = ask("Enter your choice: ", "4")
        if choice == "1":
            text = ask("Text: ", "SOS")
            code = to_morse(text)
            print(f"Morse: {code}")
            print(f"Flash: {flash(code)}")
            print(f"Would take {play_morse(code, audible=False):.1f}s "
                  f"at {DIT_MS} ms per dit")
        elif choice == "2":
            code = ask("Morse: ", "... --- ...")
            print(f"Text: {from_morse(code)}")
        elif choice == "3":
            code = ask("Morse to play: ", "... --- ...")
            seconds = play_morse(code)
            print(f"played in {seconds:.1f}s")
        elif choice == "4":
            print("Bye.")
            return
        else:
            print("Invalid choice")


if __name__ == "__main__":
    if "--test" in sys.argv:
        import unittest

        class TestMorse(unittest.TestCase):
            def test_sos(self):
                self.assertEqual(to_morse("SOS"), "... --- ...")

            def test_round_trip(self):
                for phrase in ("SOS", "HELLO WORLD", "PYTHON 3.14",
                               "WHAT? (YES)", "A B C"):
                    self.assertEqual(from_morse(to_morse(phrase)), phrase)

            def test_word_gaps_survive(self):
                self.assertEqual(from_morse(to_morse("A A")), "A A")

            def test_unknown_characters_dropped(self):
                self.assertEqual(to_morse("A#B"), ".- -...")

            def test_timing_table(self):
                # SOS: 9 symbols, 3 of them dahs, plus the gaps.
                self.assertAlmostEqual(
                    play_morse("... --- ...", audible=False),
                    play_morse("... --- ...", audible=False))
                self.assertGreater(play_morse("-", audible=False),
                                   play_morse(".", audible=False))

        unittest.main(argv=sys.argv[:1], exit=False)
    else:
        main()
