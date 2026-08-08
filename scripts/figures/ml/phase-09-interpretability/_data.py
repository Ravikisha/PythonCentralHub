"""Shared datasets for the Phase 09 (interpretability) figures.

Every generator is seeded and every quantity the pages quote is computed from
these, so the prose and the figures cannot drift apart.

Note that no page in this phase imports `shap` or `fairlearn`. Shapley values
here are computed **exactly**, by brute force over all feature orderings, and
the fairness metrics are a few lines of numpy each. That keeps the figures
reproducible with the repo's existing environment and — more usefully — means
the reader sees the definitions rather than a library call.
"""

from __future__ import annotations

import itertools
import math

import numpy as np
import pandas as pd


def noisy_signal(n=1200, noise_rate=0.10, seed=0):
    """Three informative low-cardinality features plus two useless ones.

    ``random_continuous`` is pure Gaussian noise, but being continuous it offers
    a tree an enormous number of candidate split points — which is exactly what
    impurity-based importance rewards. ``noise_rate`` label noise leaves the
    forest room to overfit, without which the trap does not appear at all.
    """
    rng = np.random.default_rng(seed)
    x1 = rng.integers(0, 2, n)
    x2 = rng.integers(0, 2, n)
    x3 = rng.integers(0, 3, n)
    clean = ((x1 + x2 + (x3 > 1)) >= 2).astype(int)
    y = np.where(rng.random(n) < noise_rate, 1 - clean, clean)
    X = pd.DataFrame({
        "informative_1": x1,
        "informative_2": x2,
        "informative_3": x3,
        "random_continuous": rng.normal(0, 1, n),
        "random_binary": rng.integers(0, 2, n),
    })
    return X, y


def duplicated_feature(n=1500, seed=1):
    """One real driver, a near-duplicate of it, and one weak independent feature."""
    rng = np.random.default_rng(seed)
    income = rng.normal(0, 1, n)
    tenure = rng.normal(0, 1, n)
    X = pd.DataFrame({
        "income": income,
        "income_copy": income + rng.normal(0, 0.01, n),
        "tenure": tenure,
    })
    y = (income * 2 + tenure * 0.5 + rng.normal(0, 0.5, n) > 0).astype(int)
    return X, y


def sign_flip_interaction(n=2000, seed=3):
    """``group`` flips the sign of x's effect, so averaging over it cancels out."""
    rng = np.random.default_rng(seed)
    x = rng.uniform(-2, 2, n)
    g = rng.integers(0, 2, n)
    y = np.where(g == 1, 2.5 * x, -2.5 * x) + rng.normal(0, 0.4, n)
    return pd.DataFrame({"x": x, "group": g}), y


LINEAR_NAMES = ["f0_strong", "f1_negative", "f2_weak", "f3_useless"]
LINEAR_COEFS = np.array([3.0, -2.0, 1.0, 0.0])


def known_linear(n=800, seed=2):
    """A linear model whose true coefficients are known, so SHAP can be checked."""
    rng = np.random.default_rng(seed)
    X = rng.normal(0, 1, (n, len(LINEAR_COEFS)))
    y = X @ LINEAR_COEFS + rng.normal(0, 0.3, n)
    return X, y


def exact_shapley(predict, x, background):
    """Exact Shapley values, straight from the definition.

    Averages the marginal contribution of each feature over **every** subset of
    the others, weighted by the Shapley kernel. Cost is O(2^p), which is why
    real libraries approximate — but with p = 4 it is 16 subsets per feature and
    the result is exact rather than estimated.
    """
    p = len(x)
    phi = np.zeros(p)

    def value(subset):
        z = background.copy()
        for j in subset:
            z[j] = x[j]
        return float(predict(z.reshape(1, -1))[0])

    for j in range(p):
        rest = [k for k in range(p) if k != j]
        for size in range(len(rest) + 1):
            weight = (math.factorial(size) * math.factorial(p - size - 1)
                      / math.factorial(p))
            for subset in itertools.combinations(rest, size):
                phi[j] += weight * (value(list(subset) + [j]) - value(list(subset)))
    return phi


def two_sites(n=4000, seed=11):
    """The same disease at two hospitals; only the first one has a shortcut.

    ``marker`` is an honest clinical signal, identical at both sites. At the
    training site the sick were almost all scanned on machine 1, so
    ``scanner_id`` predicts the label without carrying any medical information.
    At the new site the scanners were assigned at random, and the shortcut is
    worth exactly nothing.
    """
    rng = np.random.default_rng(seed)

    def block(leak_strength):
        sick = rng.integers(0, 2, n)
        marker = rng.normal(sick * 1.0, 1.0, n)
        follows_leak = rng.random(n) < leak_strength
        scanner = np.where(follows_leak, sick, rng.integers(0, 2, n))
        return pd.DataFrame({"marker": marker, "scanner_id": scanner}), sick

    X_train_site, y_train_site = block(0.95)
    X_new_site, y_new_site = block(0.00)
    return X_train_site, y_train_site, X_new_site, y_new_site


def unequal_base_rates(n=8000, seed=7):
    """Two groups with sharply different base rates and one honest feature.

    The feature is equally predictive in both groups — there is no measurement
    bias here at all. The difference in base rates alone is enough to make the
    three fairness criteria mutually unsatisfiable.
    """
    rng = np.random.default_rng(seed)
    group = rng.integers(0, 2, n)
    q = rng.normal(np.where(group == 1, -1.1, 1.1), 1.0, n)
    y = (rng.random(n) < 1 / (1 + np.exp(-1.6 * q))).astype(int)
    X = pd.DataFrame({"q": q, "noise": rng.normal(0, 1, n)})
    return X, y, group


def group_metrics(proba, y_true, group, thresholds):
    """Selection rate, TPR, FPR and precision per group at given thresholds."""
    rows = []
    for g in sorted(set(group)):
        mask = group == g
        pred = (proba[mask] >= thresholds[g]).astype(int)
        yy = y_true[mask]
        rows.append({
            "group": g,
            "threshold": thresholds[g],
            "base_rate": float(yy.mean()),
            "selection": float(pred.mean()),
            "tpr": float(pred[yy == 1].mean()) if (yy == 1).any() else float("nan"),
            "fpr": float(pred[yy == 0].mean()) if (yy == 0).any() else float("nan"),
            "precision": float(yy[pred == 1].mean()) if pred.any() else float("nan"),
        })
    return rows


def solve_threshold(proba, y_true, group, g, target, metric="selection"):
    """Bisect for the threshold that makes `metric` equal `target` for group g."""
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        mask = group == g
        pred = proba[mask] >= mid
        if metric == "selection":
            value = pred.mean()
        else:                                    # tpr
            value = pred[y_true[mask] == 1].mean()
        if value > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
