"""Shared datasets for the Phase 11 (ML engineering) figures.

One synthetic classification problem, used by every page in the phase so that the
numbers on different pages can be compared with each other.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

FEATURES = 25
INFORMATIVE = 8


def tabular(n=4000, seed=0):
    """A moderately hard binary problem: 25 features, 8 informative, 5% label noise."""
    from sklearn.datasets import make_classification

    X, y = make_classification(n_samples=n, n_features=FEATURES,
                               n_informative=INFORMATIVE, n_redundant=4,
                               class_sep=0.9, flip_y=0.05, random_state=seed)
    columns = [f"f{i:02d}" for i in range(FEATURES)]
    return pd.DataFrame(X, columns=columns), y


CUTOFF = pd.Timestamp("2024-04-01")


def event_log(n_customers=4000, days=120, seed=21):
    """An event log plus a churn label, with a latent engagement driving both.

    Returns (events, churn, engagement). Events are timestamped, so features can
    be computed as of any moment — which is what makes point-in-time correctness
    demonstrable rather than theoretical.
    """
    rng = np.random.default_rng(seed)
    engagement = rng.normal(0, 1, n_customers)
    rate = np.exp(0.9 + 0.75 * engagement) / 30.0          # events per day

    rows = []
    for c in range(n_customers):
        n_events = rng.poisson(rate[c] * days)
        if n_events == 0:
            continue
        offsets = rng.uniform(0, days, n_events)
        amounts = np.exp(rng.normal(2.5 + 0.3 * engagement[c], 0.6, n_events))
        for offset, amount in zip(offsets, amounts):
            rows.append((c, CUTOFF - pd.Timedelta(days=float(offset)),
                         float(amount)))
    events = pd.DataFrame(rows, columns=["customer", "ts", "amount"])

    churn = (rng.random(n_customers)
             < 1 / (1 + np.exp(1.1 * engagement + 0.4))).astype(int)

    # what happens AFTER the cutoff: only the customers who stayed keep acting
    post = []
    for c in range(n_customers):
        if churn[c]:
            continue
        for _ in range(rng.poisson(rate[c] * 30)):
            post.append((c,
                         CUTOFF + pd.Timedelta(days=float(rng.uniform(0, 30))),
                         float(np.exp(rng.normal(2.5 + 0.3 * engagement[c],
                                                 0.6)))))
    future = pd.DataFrame(post, columns=["customer", "ts", "amount"])
    return events, future, churn


def window_features(events, window_days, asof, customer_ids):
    """Aggregate the log over (asof - window, asof]. One function, both paths."""
    lower = asof - pd.Timedelta(days=window_days)
    window = events[(events["ts"] > lower) & (events["ts"] <= asof)]
    grouped = window.groupby("customer").agg(events=("amount", "size"),
                                             mean_amount=("amount", "mean"),
                                             last=("ts", "max"))
    grouped["days_since"] = (asof - grouped["last"]).dt.days
    frame = grouped.drop(columns="last").reindex(customer_ids)
    frame["events"] = frame["events"].fillna(0)
    frame["mean_amount"] = frame["mean_amount"].fillna(0)
    frame["days_since"] = frame["days_since"].fillna(999)
    return frame


def serving_rows(X, n=500, seed=1, drift=0.0, drop_column=None,
                 rename_column=None, unit_change=None):
    """A batch of 'production' rows, optionally corrupted the way real ones are.

    Each keyword reproduces one failure that has shipped somewhere: a shifted
    feature, a column silently dropped, a column renamed upstream, or a unit
    change (cents for euros).
    """
    rng = np.random.default_rng(seed)
    rows = X.sample(n=n, random_state=seed).reset_index(drop=True).copy()

    if drift:
        rows["f00"] = rows["f00"] + drift
    if unit_change:
        rows[unit_change[0]] = rows[unit_change[0]] * unit_change[1]
    if drop_column:
        rows = rows.drop(columns=[drop_column])
    if rename_column:
        rows = rows.rename(columns={rename_column[0]: rename_column[1]})
    return rows
