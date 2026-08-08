"""Figures for *Time Series Forecasting Fundamentals*."""

import functools
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import daily_series, lag_frame  # noqa: E402
from _style import Palette, figure  # noqa: E402

HORIZON = 28


@functools.lru_cache(maxsize=1)
def setup():
    """One series, one 80/20 chronological split, three fitted models."""
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    series, parts = daily_series()
    frame = lag_frame(series)
    X, y = frame.drop(columns="y"), frame["y"]
    split = int(len(frame) * 0.8)

    ridge = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    ridge.fit(X.iloc[:split], y.iloc[:split])
    gbm = HistGradientBoostingRegressor(random_state=0)
    gbm.fit(X.iloc[:split], y.iloc[:split])

    return {
        "series": series, "parts": parts, "X": X, "y": y, "split": split,
        "ridge": ridge, "gbm": gbm,
        "X_te": X.iloc[split:], "y_te": y.iloc[split:],
        "pred_ridge": ridge.predict(X.iloc[split:]),
        "pred_gbm": gbm.predict(X.iloc[split:]),
    }


def recursive_forecast(horizon=HORIZON):
    """Feed each prediction back in as the next row's lag_1."""
    d = setup()
    X, series, model = d["X"], d["series"], d["ridge"]
    last_train = X.index[d["split"] - 1]
    hist = list(series.loc[:last_train])
    t0 = float(X.loc[last_train, "t"])

    out = []
    for h in range(horizon):
        stamp = last_train + pd.Timedelta(days=h + 1)
        row = {"lag_1": hist[-1], "lag_2": hist[-2], "lag_3": hist[-3],
               "lag_7": hist[-7], "lag_14": hist[-14],
               "roll_7": float(np.mean(hist[-7:])),
               "roll_28": float(np.mean(hist[-28:])),
               "dow": stamp.dayofweek, "t": t0 + h + 1}
        value = float(model.predict(pd.DataFrame([row], columns=X.columns))[0])
        out.append(value)
        hist.append(value)
    return np.array(out)


def the_series(fig, axes, p: Palette) -> None:
    """What the model is allowed to explain, component by component."""
    d = setup()
    series, parts = d["series"], d["parts"]
    cut = d["X"].index[d["split"]]

    gs = fig.add_gridspec(2, 1, height_ratios=[2, 1.25], hspace=0.42)
    top, bottom = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])

    top.plot(series.index, series.values, color=p.blue, lw=1.0)
    top.axvline(cut, color=p.amber, lw=1.6)
    top.annotate(f"train ends {cut.date()}", (cut, series.max()),
                 xytext=(-6, -4), textcoords="offset points", ha="right",
                 fontsize=9, color=p.amber)
    top.set_ylabel("demand")
    top.set_title(f"1,096 days; sd {series.std():.2f}", fontsize=10.5)

    for name, col in (("trend", p.green), ("weekly", p.purple),
                      ("yearly", p.amber), ("noise", p.muted)):
        # centred, so the four are comparable on one axis
        values = parts[name].values - parts[name].values.mean()
        bottom.plot(parts.index, values, color=col, lw=1.0,
                    label=f"{name} — sd {parts[name].std():.2f}")
    bottom.axhline(0, color=p.grid, lw=1)
    bottom.set_ylabel("component (centred)")
    bottom.set_ylim(-45, 62)
    bottom.legend(loc="upper center", ncol=4, fontsize=8.5)
    bottom.set_title(f"Only the AR(1) noise is unpredictable — sd "
                     f"{parts['noise'].std():.2f} against the series' "
                     f"{series.std():.2f}", fontsize=10.5)


def baselines_and_models(fig, axes, p: Palette) -> None:
    """A model that cannot beat 'last week' has not earned its complexity."""
    from sklearn.metrics import mean_absolute_error

    d = setup()
    y_te, X_te = d["y_te"], d["X_te"]
    window = slice(0, 90)

    axs = fig.subplots(1, 2, width_ratios=[1.75, 1])

    axs[0].plot(y_te.index[window], y_te.values[window], color=p.fg, lw=1.8,
                label="actual")
    axs[0].plot(y_te.index[window], X_te["lag_7"].values[window], color=p.muted,
                lw=1.1, label="seasonal naive")
    axs[0].plot(y_te.index[window], d["pred_ridge"][window], color=p.blue,
                lw=1.4, label="ridge on lags")
    axs[0].set_ylabel("demand")
    axs[0].set_title("First 90 test days", fontsize=10.5)
    axs[0].legend(loc="upper left", fontsize=8.5, ncol=3)
    for label in axs[0].get_xticklabels():
        label.set_rotation(18)
        label.set_horizontalalignment("right")

    mae_naive = mean_absolute_error(y_te, X_te["lag_1"])
    rows = [
        ("train mean", np.full(len(y_te), d["y"].iloc[:d["split"]].mean()), p.red),
        ("naive", X_te["lag_1"].values, p.muted),
        ("seasonal naive", X_te["lag_7"].values, p.purple),
        ("gradient boosting", d["pred_gbm"], p.green),
        ("ridge on lags", d["pred_ridge"], p.blue),
    ]
    mase = [mean_absolute_error(y_te, pred) / mae_naive for _, pred, _ in rows]
    idx = np.arange(len(rows))
    axs[1].barh(idx, mase, color=[c for _, _, c in rows], height=0.55)
    for i, v in enumerate(mase):
        axs[1].annotate(f"{v:.3f}", (v + 0.03, i), va="center", fontsize=9,
                        color=p.muted)
    axs[1].axvline(1.0, color=p.amber, lw=1.4, ls="--")
    axs[1].annotate("naive", (1.03, -0.42), fontsize=8.5, color=p.amber)
    axs[1].set_yticks(idx)
    axs[1].set_yticklabels([n for n, _, _ in rows], fontsize=9)
    axs[1].set_xlim(0, max(mase) * 1.18)
    axs[1].set_xlabel("MASE (MAE relative to the naive forecast)")
    axs[1].set_title("Below 1.0 means better than 'yesterday'", fontsize=10.5)

    fig.suptitle("Ridge on lags reaches MASE 0.560; the train mean is 2.5x worse "
                 "than doing nothing.", fontsize=10.5, color=p.muted)


def random_split_lies(fig, axes, p: Palette) -> None:
    """Shuffling rows lets a model interpolate between its own neighbours."""
    from sklearn.model_selection import KFold, TimeSeriesSplit, cross_val_score

    d = setup()
    X, y = d["X"], d["y"]

    axs = fig.subplots(1, 2, width_ratios=[1.1, 1])

    # fold schematic
    n = 40
    for row, (name, splitter) in enumerate((("shuffled\nKFold",
                                             KFold(5, shuffle=True,
                                                   random_state=0)),
                                            ("TimeSeries\nSplit",
                                             TimeSeriesSplit(5)))):
        for fold, (tr, te) in enumerate(splitter.split(np.arange(n))):
            yy = row * 6 + fold
            axs[0].scatter(tr, np.full(len(tr), yy), s=9, color=p.blue,
                           marker="s")
            axs[0].scatter(te, np.full(len(te), yy), s=9, color=p.amber,
                           marker="s")
        axs[0].annotate(name, (-2.5, row * 6 + 2), ha="right", va="center",
                        fontsize=9, color=p.fg)
    axs[0].set_xlim(-14, n)
    axs[0].set_ylim(-1, 11)
    axs[0].set_yticks([])
    axs[0].set_xlabel("row index (time)")
    axs[0].grid(False)
    axs[0].set_title("Blue trains, amber tests", fontsize=10.5)

    labels, shuffled, ordered = [], [], []
    for name, model in (("ridge on lags", d["ridge"]),
                        ("gradient boosting", d["gbm"])):
        labels.append(name)
        shuffled.append(-cross_val_score(
            model, X, y, cv=KFold(5, shuffle=True, random_state=0),
            scoring="neg_mean_absolute_error").mean())
        ordered.append(-cross_val_score(
            model, X, y, cv=TimeSeriesSplit(5),
            scoring="neg_mean_absolute_error").mean())

    idx = np.arange(len(labels))
    axs[1].bar(idx - 0.2, shuffled, 0.4, color=p.red, label="shuffled KFold")
    axs[1].bar(idx + 0.2, ordered, 0.4, color=p.blue, label="TimeSeriesSplit")
    for i, (s, o) in enumerate(zip(shuffled, ordered)):
        axs[1].annotate(f"{s:.2f}", (i - 0.2, s + 0.15), ha="center", fontsize=9,
                        color=p.red)
        axs[1].annotate(f"{o:.2f}", (i + 0.2, o + 0.15), ha="center", fontsize=9,
                        color=p.blue)
    axs[1].set_xticks(idx)
    axs[1].set_xticklabels(labels, fontsize=9)
    axs[1].set_ylim(0, max(ordered) * 1.35)
    axs[1].set_ylabel("cross-validated MAE")
    axs[1].set_title("The flexible model is the one that gets flattered",
                     fontsize=10.5)
    axs[1].legend(loc="upper left", fontsize=8.5)

    fig.suptitle("Shuffling costs the boosting model 3.69 MAE of honesty and the "
                 "ridge 0.73.", fontsize=10.5, color=p.muted)


def horizon_decay(fig, axes, p: Palette) -> None:
    """One-step error is not forecast error."""
    from sklearn.metrics import mean_absolute_error

    d = setup()
    y_te = d["y_te"]
    rec = recursive_forecast()
    actual = y_te.values[:HORIZON]
    one_step = d["pred_ridge"][:HORIZON]

    axs = fig.subplots(1, 2, width_ratios=[1.3, 1])

    days = np.arange(1, HORIZON + 1)
    axs[0].plot(days, actual, color=p.fg, lw=1.9, label="actual")
    axs[0].plot(days, one_step, color=p.blue, lw=1.5,
                label="one-step-ahead (sees yesterday)")
    axs[0].plot(days, rec, color=p.red, lw=1.5, ls="--",
                label="recursive (sees nothing after day 0)")
    axs[0].set_xlabel("days after the training cut")
    axs[0].set_ylabel("demand")
    axs[0].set_title("Two very different questions", fontsize=10.5)
    axs[0].legend(loc="lower left", fontsize=8.5)

    hs = np.arange(1, HORIZON + 1)
    mae_rec = [np.abs(rec[:h] - actual[:h]).mean() for h in hs]
    mae_one = [np.abs(one_step[:h] - actual[:h]).mean() for h in hs]
    axs[1].plot(hs, mae_one, color=p.blue, lw=2.0, label="one-step-ahead")
    axs[1].plot(hs, mae_rec, color=p.red, lw=2.0, label="recursive")
    for h in (7, 14, 28):
        axs[1].annotate(f"{mae_rec[h - 1]:.2f}", (h, mae_rec[h - 1] + 0.28),
                        ha="center", fontsize=8.5, color=p.red)
    axs[1].set_xlabel("horizon (days averaged)")
    axs[1].set_ylabel("MAE up to that horizon")
    axs[1].set_ylim(0, max(mae_rec) * 1.25)
    axs[1].set_title(f"Recursive MAE {mae_rec[-1]:.2f} against one-step "
                     f"{mae_one[-1]:.2f}", fontsize=10.5)
    axs[1].legend(loc="lower right", fontsize=8.5)

    fig.suptitle("A one-step MAE is a claim about tomorrow, not about the month.",
                 fontsize=10.5, color=p.muted)


def centred_rolling_leak(fig, axes, p: Palette) -> None:
    """A rolling mean centred on the row averages the future into the features."""
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    d = setup()
    series = d["series"]
    frame = lag_frame(series)
    leaky = frame.copy()
    leaky["roll_centred"] = series.rolling(7, center=True).mean()
    leaky = leaky.dropna()
    honest = frame.loc[leaky.index]

    scores = []
    for name, f in (("honest\n(lags only)", honest),
                    ("with a centred\nrolling mean", leaky)):
        X, y = f.drop(columns="y"), f["y"]
        s = int(len(f) * 0.8)
        model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
        model.fit(X.iloc[:s], y.iloc[:s])
        pred = model.predict(X.iloc[s:])
        scores.append((name, mean_absolute_error(y.iloc[s:], pred),
                       r2_score(y.iloc[s:], pred)))

    axs = fig.subplots(1, 2, width_ratios=[1.15, 1])

    # what the centred window sees
    t = np.arange(-6, 7)
    axs[0].axvspan(-3, 3, color=p.red, alpha=0.16)
    axs[0].scatter(t, np.zeros_like(t), s=45, color=p.muted)
    axs[0].scatter([0], [0], s=110, color=p.amber, zorder=5)
    axs[0].annotate("the row being predicted", (0, 0.16), ha="center",
                    fontsize=9.5, color=p.amber)
    axs[0].annotate("rolling(7, center=True) averages\nthree days of the FUTURE",
                    (0, -0.34), ha="center", fontsize=9.5, color=p.red)
    axs[0].set_xlim(-6.8, 6.8)
    axs[0].set_ylim(-0.6, 0.45)
    axs[0].set_yticks([])
    axs[0].set_xlabel("days relative to the row")
    axs[0].grid(False)
    axs[0].set_title("Where the leak comes from", fontsize=10.5)

    idx = np.arange(len(scores))
    axs[1].bar(idx, [s[1] for s in scores], color=[p.blue, p.red], width=0.5)
    for i, s in enumerate(scores):
        axs[1].annotate(f"MAE {s[1]:.3f}\nR2 {s[2]:.4f}", (i, s[1] + 0.16),
                        ha="center", fontsize=9.5, color=p.muted)
    axs[1].set_xticks(idx)
    axs[1].set_xticklabels([s[0] for s in scores], fontsize=9.5)
    axs[1].set_ylim(0, max(s[1] for s in scores) * 1.35)
    axs[1].set_ylabel("test MAE (lower is better)")
    axs[1].set_title("A 25% 'improvement' that cannot be deployed",
                     fontsize=10.5)

    fig.suptitle("The feature is legal-looking, chronologically impossible, and "
                 "improves every metric.", fontsize=10.5, color=p.muted)


FIGURES = [
    figure("the-series", the_series, size=(8.8, 5.0), axes=False),
    figure("baselines-and-models", baselines_and_models, size=(9.0, 3.9),
           axes=False),
    figure("random-split-lies", random_split_lies, size=(8.8, 3.7), axes=False),
    figure("horizon-decay", horizon_decay, size=(8.8, 3.9), axes=False),
    figure("centred-rolling-leak", centred_rolling_leak, size=(8.8, 3.8),
           axes=False),
]
