"""Shared datasets for the Phase 01 (foundation) figures.

Phase 01 is conceptual, so its figures exist to turn slogans into
measurements: "rules do not scale", "deep learning needs data", "no algorithm
wins everywhere". Every generator here is seeded so the numbers quoted in the
prose stay true across rebuilds.
"""

from __future__ import annotations

import numpy as np


SPAM_WORDS = ["free", "winner", "prize", "click", "urgent", "offer", "cash",
              "limited", "guarantee", "bonus"]
HAM_WORDS = ["meeting", "report", "attached", "schedule", "review", "project",
             "invoice", "team", "deadline", "notes"]


NEUTRAL_WORDS = [
    "the", "and", "you", "for", "with", "this", "that", "have", "from",
    "your", "will", "please", "today", "about", "would", "there", "which",
    "time", "back", "make", "know", "just", "send", "also", "need", "week",
    "call", "here", "work", "good", "next", "want", "look", "take", "some",
]


def spam_corpus(n=2000, seed=0, signal=0.22, crossover=0.35):
    """Synthetic two-class text with a deliberately weak, overlapping signal.

    Most tokens in every message are neutral filler. Only ``signal`` of them
    carry class information, and ``crossover`` of *those* come from the wrong
    vocabulary — so spam messages genuinely contain business words and vice
    versa. That overlap is what defeats a hand-written keyword rule while a
    learned model, which weighs evidence rather than triggering on it, still
    does well. That contrast is the point of the first two pages.
    """
    rng = np.random.default_rng(seed)
    docs, labels = [], []
    for i in range(n):
        is_spam = i % 2 == 0
        main = SPAM_WORDS if is_spam else HAM_WORDS
        other = HAM_WORDS if is_spam else SPAM_WORDS
        length = int(rng.integers(14, 30))
        words = []
        for _ in range(length):
            if rng.random() < signal:
                pool = other if rng.random() < crossover else main
            else:
                pool = NEUTRAL_WORDS
            words.append(str(rng.choice(pool)))
        docs.append(" ".join(words))
        labels.append(int(is_spam))
    return docs, np.array(labels)


def keyword_rule(docs, keywords, threshold=1):
    """The hand-written spam filter: flag anything with >= threshold keywords."""
    kw = set(keywords)
    return np.array([int(sum(w in kw for w in d.split()) >= threshold)
                     for d in docs])


def linear_with_noise(n=60, seed=1, slope=0.75, noise=0.9):
    rng = np.random.default_rng(seed)
    x = rng.uniform(-2.6, 2.6, n)
    return x, slope * x + rng.uniform(-noise, noise, n)


def tabular_task(n=1500, seed=3):
    """Small structured dataset — the regime where gradient boosting wins."""
    from sklearn.datasets import make_classification

    return make_classification(
        n_samples=n, n_features=20, n_informative=8, n_redundant=4,
        class_sep=1.1, random_state=seed,
    )
