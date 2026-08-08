"""Figures for *ML vs Traditional Programming*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import SPAM_WORDS, keyword_rule, spam_corpus  # noqa: E402
from _style import Palette, figure  # noqa: E402


def _split():
    from sklearn.model_selection import train_test_split

    docs, y = spam_corpus(2000, seed=0)
    return train_test_split(docs, y, test_size=0.3, random_state=0, stratify=y)


def rules_vs_one_fit(fig, axes, p: Palette) -> None:
    """Thirty hand-tuned rule variants against one fitted model."""
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics import accuracy_score
    from sklearn.naive_bayes import MultinomialNB

    Xtr, Xte, ytr, yte = _split()

    ks = range(1, 11)
    curves = {}
    for thr in (1, 2, 3):
        curves[thr] = [accuracy_score(yte, keyword_rule(Xte, SPAM_WORDS[:k], thr))
                       for k in ks]

    vec = CountVectorizer()
    model = MultinomialNB().fit(vec.fit_transform(Xtr), ytr)
    learned = accuracy_score(yte, model.predict(vec.transform(Xte)))
    best_rule = max(max(v) for v in curves.values())

    colors = {1: p.blue, 2: p.green, 3: p.purple}
    for thr, ys in curves.items():
        axes.plot(list(ks), ys, "o-", color=colors[thr],
                  label=f"rule: flag if ≥ {thr} keyword(s)")
    axes.axhline(learned, color=p.amber, ls="--", lw=2,
                 label=f"one fitted model, no tuning: {learned:.4f}")
    axes.annotate(f"best of all 30 rules: {best_rule:.4f}",
                  (10, best_rule + 0.012), color=p.purple, fontsize=9,
                  ha="right")
    axes.set_xlabel("number of keywords in the rule list")
    axes.set_ylabel("test accuracy")
    axes.set_xticks(list(ks))
    axes.set_ylim(0.48, 0.92)
    axes.set_title("Thirty hand-tuned rule variants, none of them enough")
    axes.legend(loc="upper left", fontsize=8.5, ncol=2)


def more_data_only_helps_one(fig, axes, p: Palette) -> None:
    """The rule is frozen at write-time; the model keeps improving."""
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics import accuracy_score
    from sklearn.naive_bayes import MultinomialNB

    Xtr, Xte, ytr, yte = _split()
    sizes = [20, 50, 100, 200, 500, 1000, 1400]

    learned = []
    for n in sizes:
        vec = CountVectorizer()
        m = MultinomialNB().fit(vec.fit_transform(Xtr[:n]), ytr[:n])
        learned.append(accuracy_score(yte, m.predict(vec.transform(Xte))))

    rule = accuracy_score(yte, keyword_rule(Xte, SPAM_WORDS, 3))

    axes.plot(sizes, learned, "o-", color=p.amber, label="learned model")
    axes.axhline(rule, color=p.blue, ls="--", lw=2,
                 label=f"best hand-written rule ({rule:.4f})")
    cross = next((s for s, a in zip(sizes, learned) if a > rule), None)
    if cross:
        axes.axvline(cross, color=p.muted, ls=":", lw=1.2)
        axes.annotate(f"model overtakes the rule\nat about {cross} examples",
                      (cross * 1.15, rule - 0.09), color=p.muted, fontsize=9)
    axes.set_xscale("log")
    axes.set_xlabel("labelled training examples")
    axes.set_ylabel("test accuracy")
    axes.set_title("Only one of these two lines responds to more data")
    axes.legend(loc="lower right")


def precision_recall_tradeoff(fig, axes, p: Palette) -> None:
    """Every rule variant is a single fixed point; the model gives a curve."""
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics import precision_recall_curve, precision_score, recall_score
    from sklearn.naive_bayes import MultinomialNB

    Xtr, Xte, ytr, yte = _split()

    for thr, marker in ((1, "o"), (2, "s"), (3, "^")):
        pr, rc = [], []
        for k in range(1, 11):
            pred = keyword_rule(Xte, SPAM_WORDS[:k], thr)
            pr.append(precision_score(yte, pred, zero_division=0))
            rc.append(recall_score(yte, pred))
        axes.scatter(rc, pr, s=32, marker=marker, color=p.blue, alpha=0.75,
                     label=f"rules, threshold {thr}" if thr == 1 else None)

    vec = CountVectorizer()
    m = MultinomialNB().fit(vec.fit_transform(Xtr), ytr)
    scores = m.predict_proba(vec.transform(Xte))[:, 1]
    precision, recall, _ = precision_recall_curve(yte, scores)
    axes.plot(recall, precision, color=p.amber, lw=2.4,
              label="one fitted model, all thresholds")

    axes.set_xlabel("recall")
    axes.set_ylabel("precision")
    axes.set_ylim(0.4, 1.02)
    axes.set_title("Thirty rules give thirty points; one model gives the "
                   "whole curve")
    axes.legend(loc="lower left")


FIGURES = [
    figure("rules-vs-one-fit", rules_vs_one_fit, size=(7.8, 4.2)),
    figure("more-data-only-helps-one", more_data_only_helps_one, size=(7.6, 4.0)),
    figure("precision-recall-tradeoff", precision_recall_tradeoff, size=(7.4, 4.2)),
]
