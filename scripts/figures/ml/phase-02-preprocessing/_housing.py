"""Shared loader for the California housing CSV used across Phase 02.

This is Aurelien Geron's version of the dataset, not scikit-learn's: it keeps the
`ocean_proximity` text column and the 207 missing `total_bedrooms` values, which
are exactly the two problems this phase teaches. scikit-learn's
`fetch_california_housing` has neither.

Downloaded once and cached beside this file. The cache is build-time only — the
site ships the rendered SVGs, so nothing here runs during an Astro build.
"""

from __future__ import annotations

import os

import pandas as pd

URL = (
    "https://raw.githubusercontent.com/ageron/handson-ml2/master/"
    "datasets/housing/housing.csv"
)
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_cache_housing.csv")


def load() -> pd.DataFrame:
    if not os.path.exists(CACHE):
        pd.read_csv(URL).to_csv(CACHE, index=False)
    return pd.read_csv(CACHE)


def with_income_cat(df: pd.DataFrame) -> pd.DataFrame:
    """Add the five-bucket income category used for stratified sampling."""
    out = df.copy()
    out["income_cat"] = pd.cut(
        out["median_income"],
        bins=[0.0, 1.5, 3.0, 4.5, 6.0, float("inf")],
        labels=[1, 2, 3, 4, 5],
    )
    return out
