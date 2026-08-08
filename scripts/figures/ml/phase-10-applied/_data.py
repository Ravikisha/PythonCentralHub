"""Shared datasets for the Phase 10 (applied problems) figures.

Every generator is seeded, and every number the pages quote is computed from
these — so the prose, the figures and the exercises cannot drift apart.

No new dependencies. `imblearn` is not installed and is not needed: SMOTE is
about fifteen lines of numpy and the reader learns more from seeing it than
from calling it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

FRAUD_NAMES = ["amount_z", "hour_z", "device_age", "velocity", "geo_mismatch",
               "noise"]
FRAUD_WEIGHTS = np.array([1.4, 0.9, -1.1, 1.6, 2.0, 0.0])


def fraud(n=20000, rate=0.005, seed=0):
    """A rare-event dataset with a well-specified model and real overlap.

    The label comes from a logistic model on five informative features, with the
    intercept solved so the positive rate lands on `rate`. Nothing is separable:
    the Bayes-optimal classifier still makes mistakes, which is what makes the
    threshold questions on this page meaningful.
    """
    rng = np.random.default_rng(seed)
    X = rng.normal(0, 1, (n, len(FRAUD_WEIGHTS)))
    score = X @ FRAUD_WEIGHTS

    # Bisect the intercept so E[P(y=1)] equals the requested base rate.
    lo, hi = -30.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if _sigmoid(score + mid).mean() > rate:
            hi = mid
        else:
            lo = mid
    intercept = (lo + hi) / 2

    p = _sigmoid(score + intercept)
    y = (rng.random(n) < p).astype(int)
    return pd.DataFrame(X, columns=FRAUD_NAMES), y, p


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def amounts_for(X, seed=5):
    """Euro amounts, lognormal and correlated with the `amount_z` feature.

    The correlation is the point: the rows most likely to be fraud are also the
    expensive ones, so a single global threshold cannot be optimal.
    """
    rng = np.random.default_rng(seed)
    z = np.asarray(X["amount_z"])
    return np.exp(3.2 + 0.85 * z + rng.normal(0, 0.45, len(z)))


COMMON = """the a to and of i my it is was for in that this you have on with not
but be at me they we so as my order please can could would just do does did
hello hi thanks thank regards team hey there any all get got no yes very still
about after again also because before been being from had has her him his how
into more most now only other our out over said same she should some than then
these those through too under until up use used using want way were what when
where which while who why will your""".split()

#: Topic vocabularies that deliberately OVERLAP — "refund" belongs to billing and
#: to shipping, "charge" to billing and technical (charging a device). Overlap is
#: what makes text classification hard, and what a bag of words cannot resolve.
TOPICS = {
    "billing": """invoice charged charge refund refunded payment card credit debit
        subscription renewal plan price overcharged billed receipt statement vat
        discount coupon duplicate late lost error""".split(),
    "shipping": """parcel package delivery delivered courier tracking shipment
        dispatched address postcode warehouse late delayed lost damaged box return
        refund label pickup driver missing""".split(),
    "technical": """login password reset error crash bug freeze loading screen app
        browser cache version update install restart offline sync timeout
        connection charge missing""".split(),
}


def support_tickets(n=6000, seed=6, leak_rate=0.30, mean_len=22,
                    topic_rate=0.09, noise_rate=0.06, n_identifiers=4000):
    """Synthetic support tickets: short, overlapping, noisily labelled.

    Each document is mostly filler and identifier tokens with a handful of topical
    words, the topic vocabularies overlap, and `noise_rate` of the labels are
    wrong — so the achievable accuracy is well below 1.0 and model comparisons
    mean something. `leak_rate` of the billing tickets carry the token
    ``ref_bill``, a template artefact that identifies the class without carrying
    any meaning.
    """
    rng = np.random.default_rng(seed)
    names = list(TOPICS)
    # Zipf-ish pool of ticket numbers, SKUs and case ids: the long tail that
    # makes a text feature matrix wide and sparse.
    identifiers = [f"case{i:05d}" for i in range(n_identifiers)]
    zipf_p = 1.0 / (np.arange(1, n_identifiers + 1) ** 1.1)
    zipf_p /= zipf_p.sum()

    docs, labels = [], []
    for _ in range(n):
        k = int(rng.integers(0, len(names)))
        length = max(6, int(rng.poisson(mean_len)))
        n_topic = rng.binomial(length, topic_rate)
        n_ident = rng.binomial(length - n_topic, 0.22)
        n_common = length - n_topic - n_ident

        words = list(rng.choice(TOPICS[names[k]], n_topic))
        words += list(rng.choice(identifiers, n_ident, p=zipf_p))
        words += list(rng.choice(COMMON, n_common))
        if names[k] == "billing" and rng.random() < leak_rate:
            words.append("ref_bill")
        rng.shuffle(words)

        docs.append(" ".join(words))
        # a fraction of tickets are filed under the wrong queue
        labels.append(int(rng.integers(0, len(names))) if rng.random() < noise_rate
                      else k)

    return docs, np.array(labels), names


DENSE_CENTRE = np.array([-3.0, -3.0])
DIFFUSE_CENTRE = np.array([3.0, 2.4])


def anomalies(n_dense=1900, n_diffuse=1000, n_global=45, n_local=20,
              n_noise=0, seed=13):
    """Two clusters of very different density, plus two kinds of anomaly.

    ``global`` anomalies sit far from everything, so any method finds them.
    ``local`` anomalies ring the TIGHT cluster at a radius that would be
    unremarkable inside the diffuse one — globally ordinary, locally impossible.
    That distinction is the whole reason LOF exists, and it is measurable here.
    ``n_noise`` appends uninformative dimensions.
    """
    rng = np.random.default_rng(seed)

    dense = rng.normal(DENSE_CENTRE, 0.28, (n_dense, 2))
    diffuse = rng.normal(DIFFUSE_CENTRE, 1.35, (n_diffuse, 2))

    far = rng.uniform(-13, 13, (n_global, 2))
    far += np.sign(far) * 3.5                       # push clear of both clusters

    angle = rng.uniform(0, 2 * np.pi, n_local)
    radius = rng.uniform(0.9, 1.4, n_local)         # 3-5 sd of the dense cluster
    local = np.column_stack([DENSE_CENTRE[0] + radius * np.cos(angle),
                             DENSE_CENTRE[1] + radius * np.sin(angle)])

    X = np.vstack([dense, diffuse, far, local])
    y = np.concatenate([np.zeros(n_dense + n_diffuse, dtype=int),
                        np.ones(n_global, dtype=int),
                        np.full(n_local, 2)])

    if n_noise:
        X = np.hstack([X, rng.normal(0, 1.6, (len(X), n_noise))])
    return X, y


def interactions(n_users=1200, n_items=600, n_factors=6, seed=11,
                 popularity_alpha=0.9, target_density=0.02):
    """Implicit feedback (a click, a purchase) generated from latent factors.

    Users and items each get a factor vector; the probability of an interaction
    is a logistic function of their dot product plus an item popularity term with
    a Zipf-like spread. The result is a sparse binary matrix whose *reason* for
    being non-zero is known, which is what lets the page separate "the model
    learned taste" from "the model learned popularity".
    """
    rng = np.random.default_rng(seed)
    U = rng.normal(0, 1, (n_users, n_factors))
    V = rng.normal(0, 1, (n_items, n_factors))
    popularity = -popularity_alpha * np.log1p(np.arange(n_items))
    rng.shuffle(popularity)

    logits = U @ V.T * 0.9 + popularity
    # bisect one global offset so the matrix lands near the target density
    lo, hi = -30.0, 30.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if _sigmoid(logits + mid).mean() > target_density:
            hi = mid
        else:
            lo = mid
    p = _sigmoid(logits + (lo + hi) / 2)
    R = (rng.random(p.shape) < p).astype(np.int8)
    return R, U, V, popularity


def daily_series(n_days=1096, seed=4):
    """Three years of daily demand: trend, weekly and yearly season, AR(1) noise.

    Every component is known, so the page can say exactly how much of the
    variance any given model is entitled to explain.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_days)

    trend = 120 + 0.06 * t
    weekly = 18 * np.sin(2 * np.pi * (t % 7) / 7 + 0.6)
    yearly = 30 * np.sin(2 * np.pi * t / 365.25 - 1.1)

    noise = np.zeros(n_days)                    # AR(1), so errors are correlated
    for i in range(1, n_days):
        noise[i] = 0.55 * noise[i - 1] + rng.normal(0, 7)

    y = trend + weekly + yearly + noise
    index = pd.date_range("2021-01-01", periods=n_days, freq="D")
    parts = pd.DataFrame({"trend": trend, "weekly": weekly, "yearly": yearly,
                          "noise": noise}, index=index)
    return pd.Series(y, index=index, name="demand"), parts


def lag_frame(series, lags=(1, 2, 3, 7, 14), roll=(7, 28)):
    """Supervised frame from a series: lags plus rolling means of PAST values only.

    Every column is shifted before it is used, so no row can see its own target.
    """
    df = pd.DataFrame({"y": series})
    for L in lags:
        df[f"lag_{L}"] = series.shift(L)
    for w in roll:
        df[f"roll_{w}"] = series.shift(1).rolling(w).mean()
    df["dow"] = series.index.dayofweek
    df["t"] = np.arange(len(series))
    return df.dropna()


def smote(X, y, k=5, target_ratio=1.0, seed=0):
    """SMOTE from the definition: interpolate between a minority point and one
    of its k minority neighbours.

    Returns the resampled (X, y). `target_ratio` is minority-to-majority after
    resampling, so 1.0 means fully balanced.
    """
    rng = np.random.default_rng(seed)
    X = np.asarray(X, dtype=float)
    minority = X[y == 1]
    n_majority = int((y == 0).sum())
    n_needed = int(round(target_ratio * n_majority)) - len(minority)
    if n_needed <= 0 or len(minority) < 2:
        return X, np.asarray(y)

    # pairwise distances within the minority class, then the k nearest
    d = np.linalg.norm(minority[:, None, :] - minority[None, :, :], axis=2)
    np.fill_diagonal(d, np.inf)
    neighbours = np.argsort(d, axis=1)[:, :min(k, len(minority) - 1)]

    seeds = rng.integers(0, len(minority), n_needed)
    picks = neighbours[seeds, rng.integers(0, neighbours.shape[1], n_needed)]
    gaps = rng.random((n_needed, 1))
    synthetic = minority[seeds] + gaps * (minority[picks] - minority[seeds])

    return (np.vstack([X, synthetic]),
            np.concatenate([np.asarray(y), np.ones(n_needed, dtype=int)]))


def undersample(X, y, seed=0):
    """Randomly drop majority rows until the classes are equal in size."""
    rng = np.random.default_rng(seed)
    X = np.asarray(X, dtype=float)
    pos = np.flatnonzero(y == 1)
    neg = rng.choice(np.flatnonzero(y == 0), size=len(pos), replace=False)
    keep = np.concatenate([pos, neg])
    rng.shuffle(keep)
    return X[keep], np.asarray(y)[keep]
