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


def mat_mul(a, b):
    """Multiply two 2x2 matrices, written out rather than looped.

    Four multiplications and two additions. A general matmul would loop, but
    at this size the loop overhead is larger than the arithmetic it saves.
    """
    return [
        [a[0][0] * b[0][0] + a[0][1] * b[1][0],
         a[0][0] * b[0][1] + a[0][1] * b[1][1]],
        [a[1][0] * b[0][0] + a[1][1] * b[1][0],
         a[1][0] * b[0][1] + a[1][1] * b[1][1]],
    ]


def mat_pow(matrix, power):
    """Exponentiation by squaring: O(log n) multiplications, not O(n).

    Reading `power` in binary, each 1 bit contributes the current square. So
    the 1,000,000th power costs 20 multiplications rather than a million.
    """
    result = [[1, 0], [0, 1]]                   # identity
    while power:
        if power & 1:
            result = mat_mul(result, matrix)
        matrix = mat_mul(matrix, matrix)
        power >>= 1
    return result


def fib_matrix(n: int) -> int:
    """Matrix exponentiation. O(log n) multiplications by squaring."""
    return mat_pow([[1, 1], [1, 0]], n)[0][1]


def fib_sum(n: int) -> int:
    """Sum of the first n Fibonacci numbers -- without adding them up.

    The identity is F(0)+...+F(n-1) = F(n+1) - 1, so the whole sum costs one
    more Fibonacci call. Worth knowing because it turns an O(n) loop into
    whatever the underlying F() costs.
    """
    return fib(n + 1) - 1


def get_n(prompt: str = "How many numbers? ", default: int = 12) -> int:
    """Ask until the answer is a positive integer.

    `int(input())` raises on "twelve" and accepts "-5", and neither is a
    count. Validation is the difference between a script that scolds the user
    and one that crashes at them.
    """
    while True:
        raw = ask_line(prompt, str(default))
        try:
            value = int(raw)
        except ValueError:
            print(f"'{raw}' is not a whole number.")
            continue
        if value < 0:
            print("A count cannot be negative.")
            continue
        if value > 100_000:
            print("That will take a while -- pick something under 100,000.")
            continue
        return value


def ask_line(prompt: str, default: str) -> str:
    """One line of input, or `default` when nobody is there to type."""
    try:
        return input(prompt).strip() or default
    except EOFError:
        print(f"{default}   (no input available, using the default)")
        return default


def ask(prompt: str, default: int) -> int:
    """Read a count, falling back to `default` when nobody is there to type.

    A script that dies with EOFError the moment it is run without a terminal
    cannot be tested, scheduled or demonstrated. Handling that is three lines.
    """
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
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


def digit_count(n: int) -> int:
    """How many decimal digits `n` has, without building the string.

    `len(str(n))` is the obvious version and it raises on anything past 4,300
    digits: CPython 3.11 capped int-to-str conversion, because the algorithm
    is quadratic and a single `str(huge)` was a denial-of-service vector. The
    bit length times log10(2) sidesteps the whole conversion.
    """
    if n == 0:
        return 1
    return int(n.bit_length() * math.log10(2)) + 1


def big_n(n: int = 100_000) -> None:
    """The O(log n) method against the O(n) one, where the gap shows."""
    print(f"\ncomputing F({n:,}) two ways:")
    started = time.perf_counter()
    by_matrix = fib_matrix(n)
    matrix_time = time.perf_counter() - started

    started = time.perf_counter()
    by_loop = fib(n)
    loop_time = time.perf_counter() - started

    print(f"  fib_matrix  {matrix_time * 1000:8.1f} ms")
    print(f"  fib (loop)  {loop_time * 1000:8.1f} ms   "
          f"{loop_time / matrix_time:.1f}x slower")
    print(f"  same answer: {by_matrix == by_loop}, "
          f"{digit_count(by_matrix):,} digits long")


def main() -> None:
    count = ask("How many numbers to generate?: ", 12)
    print(f"Fibonacci sequence, first {count} terms:")
    print("  " + ", ".join(str(value) for value in fib_iter(count)))
    print()
    if not check():
        raise SystemExit("implementations disagree")
    timings()
    precision_limit()
    print(f"\nsum of the first {count} terms: {fib_sum(count)} "
          f"(checked against adding them up: {sum(fib_iter(count))})")
    big_n()
    print("\nseven ways to compute the same numbers. The loop is what you")
    print("ship; the rest are here because the gaps between them are the")
    print("whole lesson.")


if __name__ == "__main__":
    main()
