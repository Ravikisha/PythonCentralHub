"""Temperature Converter — six conversions behind one dispatch table.

The program runs three ways:

    python tempconverter.py           # menu; unattended it plays DEMO_ANSWERS
    python tempconverter.py --test    # the unit tests
    python tempconverter.py --gui     # the tkinter window, needs a display

Everything the docs page teaches lives here, so a reader who copies a snippet
out of the page finds the same function in the file.
"""

import sys
import unittest

# What the menu answers when nobody is at the keyboard. Scripting the demo,
# rather than letting every prompt fall back to the same default, is the only
# way an unattended run exercises more than one branch — with a single default
# the loop either repeats one conversion forever or quits on the first prompt.
DEMO_ANSWERS = iter(["1", "100", "3", "0", "5", "212", "q"])


def ask(prompt, default=""):
    """Read a line, or take the next scripted answer when nobody is there.

    Without this the script raises EOFError as soon as it runs unattended --
    in a test, a scheduled job, or the documentation build that captures this
    output. The substituted answer is printed, never silent, so the captured
    transcript cannot be mistaken for something a person typed.
    """
    try:
        answer = input(prompt)
    except EOFError:
        # `input` has already written the prompt to stdout by the time it
        # raises, so printing it again here would double every line.
        answer = next(DEMO_ANSWERS, default)
        print(f"{answer}   (scripted demo answer)")
        return answer
    return answer.strip() or default


# --- the two conversions everyone starts with -------------------------------

def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32


def fahrenheit_to_celsius(f):
    return (f - 32) * 5 / 9


# --- and the short names the dispatch table uses ----------------------------

def c_to_f(c):
    return c * 9 / 5 + 32


def f_to_c(f):
    return (f - 32) * 5 / 9


def c_to_k(c):
    return c + 273.15


def k_to_c(k):
    return k - 273.15


def f_to_k(f):
    return c_to_k(f_to_c(f))


def k_to_f(k):
    return c_to_f(k_to_c(k))


def celsius_to_kelvin(c):
    """Kelvin, but refusing the temperatures that cannot exist.

    ``c_to_k`` will happily return a negative Kelvin. This one will not: below
    -273.15 degC there is no colder, so an input under it is a bad reading
    rather than a cold day, and failing loudly beats propagating it.
    """
    if c < -273.15:
        raise ValueError("Temperature below absolute zero is impossible.")
    return c + 273.15


def ask_number(prompt, default="0"):
    """Keep asking until the answer parses as a number."""
    while True:
        raw = ask(prompt, default)
        try:
            return float(raw)
        except ValueError:
            print(f"'{raw}' is not a valid number. Try again.")


CONVERSIONS = {
    "1": ("Celsius to Fahrenheit", c_to_f, "degC", "degF"),
    "2": ("Fahrenheit to Celsius", f_to_c, "degF", "degC"),
    "3": ("Celsius to Kelvin", c_to_k, "degC", "K"),
    "4": ("Kelvin to Celsius", k_to_c, "K", "degC"),
    "5": ("Fahrenheit to Kelvin", f_to_k, "degF", "K"),
    "6": ("Kelvin to Fahrenheit", k_to_f, "K", "degF"),
}


def main():
    """The menu loop. Six conversions, one table, no `elif` ladder."""
    while True:
        print("\nTemperature Converter")
        for key, (label, _, _, _) in CONVERSIONS.items():
            print(f"  {key}. {label}")
        print("  Q. Quit")
        choice = ask("Choice: ", "q").strip()
        if choice.lower() == "q":
            print("Bye.")
            break
        if choice not in CONVERSIONS:
            print("Invalid choice.")
            continue
        label, func, in_unit, out_unit = CONVERSIONS[choice]
        value = ask_number(f"Enter temperature ({in_unit}): ", "0")
        print(f"{value} {in_unit} = {func(value):.2f} {out_unit}")


def gui():
    """The same conversion behind a tkinter window.

    Imported inside the function on purpose: tkinter needs a display, and a
    module-level import would break every headless run of this file for the
    sake of a mode most readers never use.
    """
    import tkinter as tk

    root = tk.Tk()
    root.title("Temperature Converter")
    entry = tk.Entry(root)
    entry.pack()
    result = tk.Label(root)
    result.pack()

    def convert():
        try:
            c = float(entry.get())
        except ValueError:
            result.config(text="Enter a number.")
            return
        result.config(text=f"{c_to_f(c):.2f} degF")

    tk.Button(root, text="Convert", command=convert).pack()
    root.mainloop()


class TestConv(unittest.TestCase):
    """The two temperatures whose conversions everyone already knows."""

    def test_freezing(self):
        self.assertEqual(c_to_f(0), 32)

    def test_boiling(self):
        self.assertEqual(c_to_f(100), 212)

    def test_absolute_zero_rejected(self):
        with self.assertRaises(ValueError):
            celsius_to_kelvin(-300)

    def test_round_trip(self):
        for c in (-40, 0, 37, 100):
            self.assertAlmostEqual(f_to_c(c_to_f(c)), c)


if __name__ == "__main__":
    if "--test" in sys.argv:
        unittest.main(argv=sys.argv[:1], exit=False)
    elif "--gui" in sys.argv:
        gui()
    else:
        main()
