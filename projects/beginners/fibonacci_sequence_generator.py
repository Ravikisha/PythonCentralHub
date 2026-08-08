"""Fibonacci sequence — seven implementations, timed against each other.

The sequence itself is a one-liner. What makes it worth a project is that it
has a genuinely wide range of correct implementations, from O(2^n) to O(log n),
and running them side by side turns "recursion is slow" into a number.

Run it with no arguments for the demo, or `python fibonacci_sequence_generator.py 20`.
"""

import itertools
import math
import sys
import time
from functools import lru_cache

PHI = (1 + math.sqrt(5)) / 2
PSI = (1 - math.sqrt(5)) / 2


def fib_iter(n: int) -> list[int]:
    """The first n terms as a list. O(n) time, O(n) space.

    This is what most real Fibonacci code looks like: one allocation, no
    recursion, and the whole sequence available afterwards.
    """
    if n <= 0:
        return []
    if n == 1:
        return [0]
    out = [0, 1]
    while len(out) < n:
        out.append(out[-1] + out[-2])
    return out


def fib(n: int) -> int:
    """Just F(n). O(n) time, O(1) space — nothing is stored along the way."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fib_rec(n: int) -> int:
    """Naive recursion. O(2^n) — correct, and unusable past about n=35."""
    if n < 2:
        return n
    return fib_rec(n - 1) + fib_rec(n - 2)


@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    """The same recursion with a cache. One decorator turns 2^n into n."""
    if n < 2:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)


def fib_gen():
    """An endless generator. O(1) extra memory however far you go."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def fib_binet(n: int) -> int:
    """Closed form. Constant time, and wrong past n ~ 70 in float64."""
    return round((PHI ** n - PSI ** n) / math.sqrt(5))


def fib_matrix(n: int) -> int:
    """Matrix exponentiation. O(log n) multiplications by squaring."""
    def multiply(a, b):
        return [
            [a[0][0] * b[0][0] + a[0][1] * b[1][0],
             a[0][0] * b[0][1] + a[0][1] * b[1][1]],
            [a[1][0] * b[0][0] + a[1][1] * b[1][0],
             a[1][0] * b[0][1] + a[1][1] * b[1][1]],
        ]

    result = [[1, 0], [0, 1]]
    base = [[1, 1], [1, 0]]
    power = n
    while power:
        if power & 1:
            result = multiply(result, base)
        base = multiply(base, base)
        power >>= 1
    return result[0][1]


def ask(prompt: str, default: int) -> int:
    """Read a count, falling back to `default` when nobody is there to type.

    A script that dies with EOFError the moment it is run without a terminal
    cannot be tested, scheduled or demonstrated. Handling that is three lines.
    """
    if len(sys.argv) > 1:
        return int(sys.argv[1])
    try:
        answer = input(prompt).strip()
    except EOFError:
        return default
    return int(answer) if answer.isdigit() else default


def check(count: int = 25) -> bool:
    """Every implementation must agree before any timing means anything."""
    expected = fib_iter(count)
    generated = list(itertools.islice(fib_gen(), count))
    checks = {
        "fib(n)": [fib(i) for i in range(count)],
        "fib_rec": [fib_rec(i) for i in range(count)],
        "fib_memo": [fib_memo(i) for i in range(count)],
        "fib_gen": generated,
        "fib_binet": [fib_binet(i) for i in range(count)],
        "fib_matrix": [fib_matrix(i) for i in range(count)],
    }
    print(f"agreement over the first {count} terms:")
    everything_matches = True
    for name, values in checks.items():
        matches = values == expected
        everything_matches &= matches
        print(f"  {name:11} {'matches' if matches else 'DIFFERS'}")
    return everything_matches


def timings(n: int = 28) -> None:
    print(f"\ntime to compute F({n}), lower is better:")
    fib_memo.cache_clear()
    methods = (("fib_rec (naive)", fib_rec), ("fib_memo", fib_memo),
               ("fib (loop)", fib), ("fib_binet", fib_binet),
               ("fib_matrix", fib_matrix))
    baseline = None
    for name, function in methods:
        started = time.perf_counter()
        function(n)
        elapsed = time.perf_counter() - started
        baseline = elapsed if baseline is None else baseline
        print(f"  {name:16} {elapsed * 1000:9.3f} ms   "
              f"{baseline / elapsed:>8,.0f}x faster than naive"
              if elapsed else f"  {name:16} {elapsed * 1000:9.3f} ms")


def precision_limit() -> None:
    print("\nwhere the closed form stops being exact:")
    for n in (10, 40, 70, 71, 75, 90):
        exact = fib(n)
        approximate = fib_binet(n)
        mark = "exact" if exact == approximate else f"off by {approximate - exact}"
        print(f"  F({n:2}) = {exact:<20} binet {mark}")


def main() -> None:
    count = ask("How many numbers to generate?: ", 12)
    print(f"Fibonacci sequence, first {count} terms:")
    print("  " + ", ".join(str(value) for value in fib_iter(count)))
    print()
    if not check():
        raise SystemExit("implementations disagree")
    timings()
    precision_limit()
    print("\nseven ways to compute the same numbers. The loop is what you")
    print("ship; the rest are here because the gaps between them are the")
    print("whole lesson.")


if __name__ == "__main__":
    main()
