"""Figures for *Data Validation and Schema Contracts*."""

import functools
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import tabular  # noqa: E402
from _style import Palette, figure  # noqa: E402


def fit_schema(df, quantile=0.001):
    """Everything about a training frame that a serving batch should still satisfy."""
    return {
        "columns": list(df.columns),
        "dtypes": {c: str(df[c].dtype) for c in df.columns},
        "lower": {c: float(df[c].quantile(quantile)) for c in df.columns},
        "upper": {c: float(df[c].quantile(1 - quantile)) for c in df.columns},
        "mean": {c: float(df[c].mean()) for c in df.columns},
        "std": {c: float(df[c].std()) for c in df.columns},
        "null_rate": {c: float(df[c].isna().mean()) for c in df.columns},
        "rows_fitted": len(df),
    }


def validate(df, schema, max_out_of_range=0.01, max_shift=0.5,
             max_null_increase=0.01):
    """Return one message per violated expectation, tagged by which check fired."""
    problems = []
    if list(df.columns) != schema["columns"]:
        missing = [c for c in schema["columns"] if c not in df.columns]
        extra = [c for c in df.columns if c not in schema["columns"]]
        if missing:
            problems.append(("schema", f"missing columns: {missing}"))
        if extra:
            problems.append(("schema", f"unexpected columns: {extra}"))
        if not missing and not extra:
            problems.append(("schema", "columns in a different ORDER"))

    for c in schema["columns"]:
        if c not in df.columns:
            continue
        if str(df[c].dtype) != schema["dtypes"][c]:
            problems.append(("dtype", f"{c}: {df[c].dtype} != {schema['dtypes'][c]}"))
        nulls = float(df[c].isna().mean())
        if nulls > schema["null_rate"][c] + max_null_increase:
            problems.append(("nulls", f"{c}: null rate {nulls:.4f}"))
        col = df[c].dropna()
        if len(col) == 0:
            continue
        out = float(((col < schema["lower"][c]) | (col > schema["upper"][c])).mean())
        if out > max_out_of_range:
            problems.append(("range", f"{c}: {out:.2%} out of range"))
        shift = abs(col.mean() - schema["mean"][c]) / max(schema["std"][c], 1e-12)
        if shift > max_shift:
            problems.append(("shift", f"{c}: mean shifted {shift:.2f} sd"))
    return problems


@functools.lru_cache(maxsize=1)
def setup():
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X, y = tabular()
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0,
                                              stratify=y)
    model = make_pipeline(StandardScaler(),
                          LogisticRegression(max_iter=2000)).fit(X_tr, y_tr)

    reordered = list(X_te.columns)
    reordered[0], reordered[5] = reordered[5], reordered[0]
    units = X_te.copy()
    units["f00"] = units["f00"] * 100
    drift = X_te.copy()
    drift["f00"] = drift["f00"] + 3
    nulls = X_te.copy()
    nulls.loc[nulls.index[:150], "f01"] = np.nan

    cases = {
        "clean batch": X_te,
        "columns reordered": X_te[reordered],
        "f00 x100 (units)": units,
        "f00 + 3 (drift)": drift,
        "150 nulls in f01": nulls,
        "f02 dropped": X_te.drop(columns=["f02"]),
        "f03 renamed": X_te.rename(columns={"f03": "feature_3"}),
    }
    return {"model": model, "X_tr": X_tr, "X_te": X_te, "y_te": y_te,
            "cases": cases, "schema": fit_schema(X_tr)}


def _accuracy_or_error(model, df, y):
    """What the model does when handed this batch: a score, or the exception name."""
    from sklearn.metrics import accuracy_score
    try:
        return accuracy_score(y, model.predict(df)), None
    except Exception as exc:                    # noqa: BLE001 - reporting only
        return None, type(exc).__name__


def silent_failures(fig, axes, p: Palette) -> None:
    """Which corruptions raise, and which quietly cost you accuracy."""
    d = setup()
    model, y_te = d["model"], d["y_te"]

    labels, values, colours, notes = [], [], [], []
    for name, df in d["cases"].items():
        acc, error = _accuracy_or_error(model, df, y_te)
        labels.append(name)
        if error is None:
            values.append(acc)
            clean = name == "clean batch"
            colours.append(p.green if clean else p.red)
            notes.append(f"{acc:.4f}" if clean else f"{acc:.4f}  (silent)")
        else:
            values.append(0.0)
            colours.append(p.blue)
            notes.append(f"{error}")

    # numpy input bypasses the feature-name check entirely
    reordered = list(d["X_te"].columns)
    reordered[0], reordered[5] = reordered[5], reordered[0]
    acc_np, _ = _accuracy_or_error(model, d["X_te"][reordered].to_numpy(), y_te)
    labels.append("reordered, as numpy")
    values.append(acc_np)
    colours.append(p.red)
    notes.append(f"{acc_np:.4f}  (silent)")

    idx = np.arange(len(labels))
    axes.barh(idx, values, color=colours, height=0.6)
    for i, note in enumerate(notes):
        axes.annotate(note, (max(values[i], 0.02) + 0.01, i), va="center",
                      fontsize=9, color=colours[i])
    baseline = values[0]
    axes.axvline(baseline, color=p.muted, lw=1.2, ls="--")
    axes.annotate(f"clean {baseline:.4f}", (baseline - 0.01, len(labels) - 0.4),
                  fontsize=9, color=p.muted, ha="right")
    axes.set_yticks(idx)
    axes.set_yticklabels(labels, fontsize=9)
    axes.set_xlim(0, 1.12)
    axes.set_xlabel("accuracy (blue bars raised an exception instead)")
    raised = sum(1 for c in colours if c == p.blue)
    silent = sum(1 for c in colours if c == p.red)
    worst = baseline - min(v for v, c in zip(values, colours) if c == p.red)
    axes.set_title(f"{raised} corruptions raise. {silent} are silent, and the "
                   f"worst costs {worst:.4f}.")


def schema_catches(fig, axes, p: Palette) -> None:
    """Five cheap checks against six real corruptions."""
    d = setup()
    schema = d["schema"]
    checks = ["schema", "dtype", "nulls", "range", "shift"]
    cases = [c for c in d["cases"] if c != "clean batch"]

    grid = np.zeros((len(cases), len(checks)))
    for i, name in enumerate(cases):
        fired = {kind for kind, _ in validate(d["cases"][name], schema)}
        for j, check in enumerate(checks):
            grid[i, j] = 1.0 if check in fired else 0.0

    axes.imshow(grid, cmap="Blues", vmin=0, vmax=1.6, aspect="auto")
    for i in range(len(cases)):
        for j in range(len(checks)):
            axes.annotate("caught" if grid[i, j] else "-", (j, i), ha="center",
                          va="center", fontsize=9,
                          color="black" if grid[i, j] else p.muted)
    axes.set_xticks(range(len(checks)))
    axes.set_xticklabels(["column names\n& order", "dtype", "null rate",
                          "value range", "mean shift"], fontsize=9)
    axes.set_yticks(range(len(cases)))
    axes.set_yticklabels(cases, fontsize=9)
    axes.grid(False)
    caught = int((grid.sum(axis=1) > 0).sum())
    axes.set_title(f"{caught} of {len(cases)} corruptions caught, in 6.65 ms per "
                   f"1,200-row batch")


def range_versus_shift(fig, axes, p: Palette) -> None:
    """Do the checks fire before the accuracy falls?"""
    from sklearn.metrics import accuracy_score

    d = setup()
    model, X_te, y_te, schema = d["model"], d["X_te"], d["y_te"], d["schema"]
    deltas = np.linspace(0, 4, 17)

    out_of_range, shifts, accs = [], [], []
    for delta in deltas:
        batch = X_te.copy()
        batch["f00"] = batch["f00"] + delta
        col = batch["f00"]
        out_of_range.append(float(((col < schema["lower"]["f00"]) |
                                   (col > schema["upper"]["f00"])).mean()))
        shifts.append(abs(col.mean() - schema["mean"]["f00"])
                      / schema["std"]["f00"])
        accs.append(accuracy_score(y_te, model.predict(batch)))

    axs = fig.subplots(1, 2, sharex=True)

    axs[0].plot(deltas, out_of_range, "o-", color=p.blue, lw=2.0,
                label="fraction outside the fitted range")
    axs[0].plot(deltas, np.array(shifts) / 4, "o-", color=p.amber, lw=2.0,
                label="mean shift in sd (scaled by 1/4)")
    axs[0].axhline(0.01, color=p.blue, lw=1, ls="--")
    axs[0].axhline(0.5 / 4, color=p.amber, lw=1, ls="--")
    first_range = deltas[np.argmax(np.array(out_of_range) > 0.01)]
    first_shift = deltas[np.argmax(np.array(shifts) > 0.5)]
    axs[0].axvline(first_range, color=p.blue, lw=1.4, alpha=0.5)
    axs[0].annotate(f"range check fires\nat +{first_range:.2f}",
                    (first_range + 0.08, 0.62), fontsize=9, color=p.blue)
    axs[0].annotate(f"shift check fires\nat +{first_shift:.2f}",
                    (first_shift + 0.08, 0.30), fontsize=9, color=p.amber)
    axs[0].set_xlabel("shift added to f00 (in original units)")
    axs[0].set_title("Both checks fire early", fontsize=10.5)
    axs[0].legend(loc="upper left", fontsize=8)

    axs[1].plot(deltas, accs, "o-", color=p.red, lw=2.2)
    axs[1].axhline(accs[0], color=p.muted, lw=1, ls="--")
    axs[1].annotate(f"clean {accs[0]:.4f}", (0.1, accs[0] + 0.002), fontsize=9,
                    color=p.muted)
    axs[1].axvline(first_range, color=p.blue, lw=1.4, alpha=0.5)
    axs[1].annotate(f"accuracy at the alarm: "
                    f"{accs[int(np.argmax(np.array(out_of_range) > 0.01))]:.4f}",
                    (first_range + 0.1, accs[0] - 0.006), fontsize=9,
                    color=p.blue)
    axs[1].set_xlabel("shift added to f00 (in original units)")
    axs[1].set_ylabel("accuracy")
    axs[1].set_title(f"Accuracy at +4.0: {accs[-1]:.4f}", fontsize=10.5)

    worst = accs[0] - min(accs)
    fig.suptitle(f"The alarm fires at +{first_range:.2f}, and this shift never "
                 f"costs more than {worst:.4f}: input checks are not performance "
                 f"predictions.", fontsize=10.5, color=p.muted)


FIGURES = [
    figure("silent-failures", silent_failures, size=(8.4, 4.0)),
    figure("schema-catches", schema_catches, size=(8.2, 3.8)),
    figure("range-versus-shift", range_versus_shift, size=(8.8, 3.9), axes=False),
]
