"""Shared helpers for the Phase 08 (MLOps) figures.

Phase 08 is engineering rather than mathematics, so its figures measure
engineering properties: artefact size, throughput, dependency footprint and
detection delay. Wall-clock latency is deliberately avoided — it varies far too
much with machine load to quote honestly — but *ratios* and *sizes* are stable.
"""

from __future__ import annotations

import numpy as np


def breast_cancer_split(seed=0):
    from sklearn.datasets import load_breast_cancer
    from sklearn.model_selection import train_test_split

    X, y = load_breast_cancer(return_X_y=True)
    return train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)


def psi(reference, current, bins=10):
    """Population Stability Index between a reference and a current sample.

    Bins are the reference deciles, so a perfectly stable feature scores ~0.
    The conventional read is < 0.1 stable, 0.1-0.25 moderate, > 0.25 large.
    """
    edges = np.quantile(reference, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    ref = np.clip(np.histogram(reference, edges)[0] / len(reference), 1e-6, None)
    cur = np.clip(np.histogram(current, edges)[0] / len(current), 1e-6, None)
    return float(((cur - ref) * np.log(cur / ref)).sum())


TRAIN_ANGLE = 45.0
"""The boundary the model is trained on. Both drift types are defined relative
to it, so the three scenarios are directly comparable."""


def stream(n, angle_deg=TRAIN_ANGLE, shift=0.0, seed=1):
    """Two features, a linear boundary, and two independent ways to drift.

    ``shift`` moves the mean of X and leaves the labelling rule alone, so
    P(X) changes and P(y | X) does not — **covariate drift**.

    ``angle_deg`` rotates the labelling rule and leaves X alone, so P(X) is
    unchanged and P(y | X) is not — **concept drift**.

    Keeping those two strictly separate is the whole point of the monitoring
    page: one of them is visible to input monitoring and harmless, the other is
    invisible and expensive.
    """
    rng = np.random.default_rng(seed)
    X = rng.normal(shift, 1, (n, 2))
    a = np.radians(angle_deg)
    w = np.array([np.cos(a), np.sin(a)])
    return X, (X @ w > 0).astype(int)
