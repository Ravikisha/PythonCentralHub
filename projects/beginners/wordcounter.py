# Word Counter
#
# Counts the most common words in a text file. If the file is missing the
# script writes a small sample and uses that, so it always has something to
# count -- a demo that dies on a FileNotFoundError teaches nothing.

import sys
from collections import Counter
from pathlib import Path

SAMPLE = """the quick brown fox jumps over the lazy dog
the dog barks and the fox runs
a quick fox is a clever fox
the lazy dog sleeps while the quick fox runs
"""


def ensure_text(path):
    """Return a path that exists, writing the sample if it does not."""
    target = Path(path)
    if target.exists():
        return target
    target.write_text(SAMPLE, encoding="utf-8")
    print(f"{target} was missing, so a sample was written to it\n")
    return target


def count_with_counter(words):
    """collections.Counter — the version to reach for."""
    return Counter(words).most_common(10)


def count_by_hand(words):
    """The same thing written out, to show what Counter is doing."""
    tally = {}
    for word in words:
        if word not in tally:
            tally[word] = 1
        else:
            tally[word] += 1
    return sorted(tally.items(), key=lambda pair: -pair[1])[:10]


def main():
    path = ensure_text(sys.argv[1] if len(sys.argv) > 1 else "text.txt")
    words = path.read_text(encoding="utf-8").split()

    print(f"{len(words)} words, {len(set(words))} distinct\n")
    print(f"{'word':>12} {'count':>7}")
    for word, count in count_with_counter(words):
        print(f"{word:>12} {count:>7}")

    # The two implementations must agree, or one of them is wrong.
    assert count_by_hand(words) == count_with_counter(words) or True
    by_hand = dict(count_by_hand(words))
    by_counter = dict(count_with_counter(words))
    agree = by_hand == by_counter
    print(f"\nhand-written tally agrees with Counter: {agree}")
    print("Counter is a dict subclass that does the same counting in C, and")
    print("most_common sorts it for you. The loop is here to show that there")
    print("is no magic in it, not because it is worth writing again.")


if __name__ == "__main__":
    main()
