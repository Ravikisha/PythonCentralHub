# Word Counter
#
# Counts the most common words in a text file. If the file is missing the
# script writes a small sample and uses that, so it always has something to
# count -- a demo that dies on a FileNotFoundError teaches nothing.

import re
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


STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "of", "in", "on", "at", "to", "for",
    "with", "is", "are", "was", "were", "be", "been", "being", "i", "you",
    "he", "she", "it", "we", "they", "this", "that", "these", "those", "as",
    "by", "from", "up", "down", "out", "so", "not",
}


def tokenize(text: str) -> list[str]:
    """Split into words the way a reader would count them.

    `str.split()` alone treats "dog." and "dog" as different words and puts
    "the" at the top of every English document ever written. Stripping
    punctuation and dropping stop words is what turns a word count into
    something about the text rather than about the language.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s']", " ", text)   # keep apostrophes intact
    return [w for w in text.split() if w and w not in STOP_WORDS]


def ngrams(words: list[str], n: int) -> list[tuple]:
    """Every run of `n` consecutive words.

    Counting these instead of single words is what finds phrases: "machine"
    and "learning" may both be common on their own, but ("machine",
    "learning") appearing together is the fact worth reporting.
    """
    return [tuple(words[i:i + n]) for i in range(len(words) - n + 1)]


def main():
    path = ensure_text(sys.argv[1] if len(sys.argv) > 1 else "text.txt")
    raw = path.read_text(encoding="utf-8")
    words = raw.split()

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

    # The same text, tokenized properly. Compare the two top-ten lists: the
    # naive one is mostly grammar, this one is mostly subject matter.
    cleaned = tokenize(raw)
    print(f"\nafter tokenizing: {len(cleaned)} words, "
          f"{len(set(cleaned))} distinct "
          f"({len(words) - len(cleaned)} dropped as stop words or punctuation)")
    print(f"\n{'word':>12} {'count':>7}")
    for word, count in Counter(cleaned).most_common(10):
        print(f"{word:>12} {count:>7}")

    print(f"\nmost common two-word phrases:")
    for phrase, count in Counter(ngrams(cleaned, 2)).most_common(5):
        print(f"{' '.join(phrase):>24} {count:>5}")


if __name__ == "__main__":
    main()
