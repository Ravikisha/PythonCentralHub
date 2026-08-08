"""Figure for *Capstone 3 — Demand Forecasting for Ordering Decisions*."""

import functools
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "phase-10-applied"))

from _style import Palette, figure  # noqa: E402

C_UNDER, C_OVER = 9.0, 1.0
Q_STAR = C_UNDER / (C_UNDER + C_OVER)


def _series():
    """Import the Phase 10 series generator by path, whatever `_data` is loaded."""
    import importlib.util

    path = os.path.join(HERE, "..", "phase-10-applied", "_data.py")
    spec = importlib.util.spec_from_file_location("pch_phase10_data", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def order_cost(order, actual):
    short = np.maximum(actual - order, 0.0)
    over = np.maximum(order - actual, 0.0)
    return (float((C_UNDER * short + C_OVER * over).sum()),
            float(short.sum()), float(over.sum()))


@functools.lru_cache(maxsize=1)
def setup():
    from sklearn.linear_model import QuantileRegressor, Ridge
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    data = _series()
    series, _ = data.daily_series()
    frame = data.lag_frame(series)
    X, y = frame.drop(columns="y"), frame["y"]
    split = int(len(frame) * 0.8)
    X_tr, X_te = X.iloc[:split], X.iloc[split:]
    y_tr, y_te = y.iloc[:split], y.iloc[split:]

    ridge = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(X_tr, y_tr)
    point = ridge.predict(X_te)

    # safety stock tuned on the last 20% of the training window
    v = int(split * 0.8)
    val_pred, val_actual = ridge.predict(X.iloc[v:split]), y.iloc[v:split].values
    buffers = np.arange(0, 30.5, 0.5)
    costs = [order_cost(val_pred + b, val_actual)[0] for b in buffers]
    buffer = float(buffers[int(np.argmin(costs))])

    def quantile_order(q):
        model = make_pipeline(
            StandardScaler(),
            QuantileRegressor(quantile=q, alpha=1e-4, solver="highs"))
        model.fit(X_tr, y_tr)
        return model.predict(X_te)

    return {"y_te": y_te.values, "point": point, "buffer": buffer,
            "quantile_order": quantile_order, "n_test": len(y_te)}


def newsvendor(fig, axes, p: Palette) -> None:
    """The ordering quantile that minimises cost is the cost ratio itself."""
    d = setup()
    actual, point, buffer = d["y_te"], d["point"], d["buffer"]

    quantiles = np.array([0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.99])
    costs, service = [], []
    for q in quantiles:
        order = d["quantile_order"](q)
        costs.append(order_cost(order, actual)[0])
        service.append(1.0 - float((actual > order).mean()))

    axs = fig.subplots(1, 2)

    axs[0].plot(quantiles, costs, "o-", color=p.blue, lw=2.2,
                label="quantile forecast")
    axs[0].axvline(Q_STAR, color=p.amber, lw=1.6,
                   label=f"theory q* = {Q_STAR:.2f}")
    best = int(np.argmin(costs))
    axs[0].scatter([quantiles[best]], [costs[best]], s=90, facecolor="none",
                   edgecolor=p.green, lw=2.2,
                   label=f"empirical minimum {quantiles[best]:.2f}")
    plain = order_cost(point, actual)[0]
    buffered = order_cost(point + buffer, actual)[0]
    axs[0].axhline(plain, color=p.red, lw=1.4, ls="--",
                   label=f"order = point forecast: {plain:,.0f}")
    axs[0].axhline(buffered, color=p.muted, lw=1.4, ls=":",
                   label=f"point + {buffer:.1f} safety stock: {buffered:,.0f}")
    axs[0].set_xlabel("ordering quantile")
    axs[0].set_ylabel(f"total cost over {d['n_test']} days")
    axs[0].set_ylim(0, plain * 1.15)
    axs[0].set_title(f"Cheapest at q = {quantiles[best]:.2f}, "
                     f"costing {costs[best]:,.0f}", fontsize=10.5)
    axs[0].legend(loc="upper center", fontsize=7.5)

    axs[1].plot(quantiles, service, "o-", color=p.green, lw=2.2)
    axs[1].plot([0.5, 1.0], [0.5, 1.0], color=p.muted, lw=1, ls="--",
                label="realised = requested")
    axs[1].scatter([Q_STAR], [service[int(np.argmin(np.abs(quantiles - Q_STAR)))]],
                   s=80, color=p.amber, zorder=5)
    axs[1].annotate(f"q*={Q_STAR:.2f} delivers "
                    f"{service[int(np.argmin(np.abs(quantiles - Q_STAR)))]:.4f}",
                    (Q_STAR - 0.005, service[int(np.argmin(np.abs(quantiles - Q_STAR)))] - 0.06),
                    fontsize=9, color=p.amber, ha="right")
    axs[1].set_xlabel("ordering quantile")
    axs[1].set_ylabel("days without a stockout")
    axs[1].set_title("The quantile you ask for is the service level you get",
                     fontsize=10.5)
    axs[1].legend(loc="upper left", fontsize=8.5)

    fig.suptitle(f"Stockout costs {C_UNDER:.0f}x holding, so order the "
                 f"{Q_STAR:.0%} quantile — not the forecast.",
                 fontsize=10.5, color=p.muted)


FIGURES = [
    figure("newsvendor", newsvendor, size=(8.8, 4.0), axes=False),
]
