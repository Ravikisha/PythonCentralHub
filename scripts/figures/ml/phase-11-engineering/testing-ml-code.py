"""Figures for *Testing ML Code*: which test catches which injected bug."""

import functools
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import tabular  # noqa: E402
from _style import Palette, figure  # noqa: E402


@functools.lru_cache(maxsize=1)
def data():
    """The Phase 11 table, with two columns put on realistic units."""
    from sklearn.model_selection import train_test_split

    X, y = tabular()
    X = X.copy()
    X["f00"] = X["f00"] * 1000 + 50000        # an amount in cents
    X["f01"] = X["f01"] * 0.001               # a rate
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3,
                                              random_state=0, stratify=y)
    return X, X_tr, X_te, y_tr, y_te


def _correct(X_tr, y_tr):
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    return make_pipeline(StandardScaler(),
                         LogisticRegression(max_iter=2000)).fit(X_tr, y_tr)


def _leaky_scaler(X_tr, y_tr):
    """The scaler is fitted on every row, training and test alike."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    X = data()[0]
    scaler = StandardScaler().fit(X)
    inner = LogisticRegression(max_iter=2000).fit(
        pd.DataFrame(scaler.transform(X_tr), columns=X_tr.columns,
                     index=X_tr.index), y_tr)

    class Wrapped:
        def _t(self, df):
            return pd.DataFrame(scaler.transform(df), columns=df.columns,
                                index=df.index)

        def predict(self, df):
            return inner.predict(self._t(df))

        def predict_proba(self, df):
            return inner.predict_proba(self._t(df))
    return Wrapped()


def _no_scaler_at_serving(X_tr, y_tr):
    """Trained on scaled features, served raw ones, positionally."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler().fit(X_tr)
    inner = LogisticRegression(max_iter=2000).fit(scaler.transform(X_tr), y_tr)

    class Wrapped:
        def predict(self, df):
            return inner.predict(df.to_numpy())

        def predict_proba(self, df):
            return inner.predict_proba(df.to_numpy())
    return Wrapped()


def _shuffled_labels(X_tr, y_tr):
    return _correct(X_tr, np.random.default_rng(3).permutation(y_tr))


def _rows_permuted(X_tr, y_tr):
    order = np.random.default_rng(5).permutation(len(X_tr))
    return _correct(X_tr.iloc[order], y_tr)


def _one_class(X_tr, y_tr):
    keep = y_tr == 0
    try:
        return _correct(X_tr[keep], y_tr[keep])
    except Exception:                            # noqa: BLE001
        class Always:
            def predict(self, df):
                return np.zeros(len(df), dtype=int)

            def predict_proba(self, df):
                out = np.zeros((len(df), 2))
                out[:, 0] = 1.0
                return out
        return Always()


def _leaked_target(X_tr, y_tr):
    """A helper column that is the label plus noise, absent at serving time."""
    rng = np.random.default_rng(4)
    inner = _correct(X_tr.assign(helper=y_tr + rng.normal(0, 0.3, len(y_tr))),
                     y_tr)

    class Wrapped:
        def predict(self, df):
            return inner.predict(df.assign(helper=0.0))

        def predict_proba(self, df):
            return inner.predict_proba(df.assign(helper=0.0))
    return Wrapped()


PIPELINES = {
    "correct": _correct,
    "scaler fitted on all data": _leaky_scaler,
    "labels shuffled": _shuffled_labels,
    "target leaked as a feature": _leaked_target,
    "scaler missing at serving": _no_scaler_at_serving,
    "one class in training": _one_class,
    "feature rows permuted": _rows_permuted,
}


# --------------------------------------------------------------------------- #
# Tests. Each returns True when it passes.
# --------------------------------------------------------------------------- #
def t_contract(fit):
    _, X_tr, X_te, y_tr, _ = data()
    proba = fit(X_tr, y_tr).predict_proba(X_te)
    return (proba.shape == (len(X_te), 2) and np.all((proba >= 0) & (proba <= 1))
            and np.allclose(proba.sum(axis=1), 1.0))


def t_row_order(fit):
    _, X_tr, X_te, y_tr, _ = data()
    model = fit(X_tr, y_tr)
    base = model.predict_proba(X_te)[:, 1]
    order = np.random.default_rng(7).permutation(len(X_te))
    return np.allclose(base[order], model.predict_proba(X_te.iloc[order])[:, 1],
                       atol=1e-12)


def t_column_order(fit):
    """Reordering columns must either raise or give identical predictions."""
    _, X_tr, X_te, y_tr, _ = data()
    model = fit(X_tr, y_tr)
    base = model.predict_proba(X_te)[:, 1]
    columns = list(X_te.columns)
    columns[0], columns[7] = columns[7], columns[0]
    try:
        other = model.predict_proba(X_te[columns])[:, 1]
    except Exception:                            # noqa: BLE001 - raising is correct
        return True
    return np.allclose(base, other, atol=1e-12)


def t_metric_floor(fit, floor=0.75):
    from sklearn.metrics import accuracy_score
    _, X_tr, X_te, y_tr, y_te = data()
    return accuracy_score(y_te, fit(X_tr, y_tr).predict(X_te)) >= floor


def t_memorise(fit, n=24):
    from sklearn.metrics import accuracy_score
    _, X_tr, _, y_tr, _ = data()
    small_X, small_y = X_tr.iloc[:n], y_tr[:n]
    if len(np.unique(small_y)) < 2:
        small_X, small_y = X_tr.iloc[:n * 4], y_tr[:n * 4]
    return accuracy_score(small_y, fit(small_X, small_y).predict(small_X)) >= 0.95


def t_direction(fit):
    _, X_tr, X_te, y_tr, _ = data()
    model = fit(X_tr, y_tr)
    base = model.predict_proba(X_te)[:, 1]
    strongest = max(X_tr.columns,
                    key=lambda c: abs(np.corrcoef(X_tr[c], y_tr)[0, 1]))
    sign = np.sign(np.corrcoef(X_tr[strongest], y_tr)[0, 1])
    nudged = X_te.copy()
    nudged[strongest] = nudged[strongest] + sign * 2 * X_tr[strongest].std()
    return float(np.median(model.predict_proba(nudged)[:, 1] - base)) > 0.01


def t_is_pipeline(fit):
    from sklearn.pipeline import Pipeline
    _, X_tr, _, y_tr, _ = data()
    return isinstance(fit(X_tr, y_tr), Pipeline)


TESTS = {
    "output\ncontract": t_contract,
    "row-order\ninvariance": t_row_order,
    "column-order\nsafety": t_column_order,
    "metric floor\n(0.75)": t_metric_floor,
    "memorise\n24 rows": t_memorise,
    "directional\nexpectation": t_direction,
    "everything in\na Pipeline": t_is_pipeline,
}


@functools.lru_cache(maxsize=1)
def matrix():
    from sklearn.metrics import accuracy_score

    _, X_tr, X_te, y_tr, y_te = data()
    grid, accuracies = [], []
    for fit in PIPELINES.values():
        accuracies.append(accuracy_score(y_te, fit(X_tr, y_tr).predict(X_te)))
        row = []
        for test in TESTS.values():
            try:
                row.append(0.0 if test(fit) else 1.0)
            except Exception:                    # noqa: BLE001 - a raise is a fail
                row.append(1.0)
        grid.append(row)
    return np.array(grid), np.array(accuracies)


def bug_test_matrix(fig, axes, p: Palette) -> None:
    """Seven bugs, seven tests, and which combinations actually fire."""
    grid, accuracies = matrix()
    names = list(PIPELINES)

    axes.imshow(grid, cmap="Reds", vmin=0, vmax=1.9, aspect="auto")
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            caught = grid[i, j] > 0
            axes.annotate("CAUGHT" if caught else "pass", (j, i), ha="center",
                          va="center", fontsize=8,
                          color="black" if caught else p.muted)
    axes.set_xticks(range(len(TESTS)))
    axes.set_xticklabels(list(TESTS), fontsize=8.5)
    axes.set_yticks(range(len(names)))
    axes.set_yticklabels([f"{n}   ({a:.4f})" for n, a in zip(names, accuracies)],
                         fontsize=8.5)
    axes.grid(False)
    caught_per_test = grid.sum(axis=0)
    best_name = list(TESTS)[int(np.argmax(caught_per_test))].replace("\n", " ")
    axes.set_title(f"Test accuracy in brackets. The '{best_name}' test caught "
                   f"{int(caught_per_test.max())} of {len(names) - 1} bugs.")


FIGURES = [
    figure("bug-test-matrix", bug_test_matrix, size=(8.8, 4.2)),
]
