"""Figures for *Cost Functions — Mean Squared Error*."""

import numpy as np

from _style import Palette, figure


def loss_shapes(fig, ax, p: Palette) -> None:
    """MSE, MAE and Huber as functions of a single residual."""
    e = np.linspace(-3, 3, 400)
    delta = 1.0
    huber = np.where(np.abs(e) <= delta, 0.5 * e**2, delta * (np.abs(e) - 0.5 * delta))

    ax.plot(e, e**2, color=p.blue, label="squared error  $e^2$")
    ax.plot(e, np.abs(e), color=p.amber, label="absolute error  $|e|$")
    ax.plot(e, 2 * huber, color=p.green, linestyle="--",
            label="Huber ($\\delta=1$, scaled)")

    ax.axvline(0, color=p.muted, linewidth=1)
    ax.set_xlabel("residual $e = y - \\hat{y}$")
    ax.set_ylabel("penalty")
    ax.set_ylim(0, 9)
    ax.set_title("Squaring punishes large misses far harder than small ones")
    ax.legend(loc="upper center")


def outlier_sensitivity(fig, ax, p: Palette) -> None:
    """How much one drifting point moves the MSE-optimal versus MAE-optimal fit."""
    rng = np.random.default_rng(0)
    x = np.linspace(0, 10, 20)
    y = 2.0 * x + 1.0 + rng.normal(0, 1.0, x.size)

    shifts = np.linspace(0, 60, 25)
    mse_slopes, mae_slopes = [], []

    for s in shifts:
        y_shift = y.copy()
        y_shift[-1] = y[-1] + s

        # MSE optimum: the closed form
        w = ((x - x.mean()) * (y_shift - y_shift.mean())).sum() / ((x - x.mean()) ** 2).sum()
        mse_slopes.append(w)

        # MAE optimum: coarse search, enough to show the contrast
        cand = np.linspace(0, 8, 801)
        b = np.median(y_shift[:, None] - cand[None, :] * x[:, None], axis=0)
        cost = np.abs(y_shift[:, None] - (cand[None, :] * x[:, None] + b[None, :])).sum(axis=0)
        mae_slopes.append(cand[cost.argmin()])

    ax.plot(shifts, mse_slopes, color=p.blue, label="slope minimising MSE")
    ax.plot(shifts, mae_slopes, color=p.amber, label="slope minimising MAE")
    ax.axhline(2.0, color=p.muted, linestyle="--", linewidth=1.2, label="true slope = 2")

    ax.set_xlabel("how far one single point is dragged upward")
    ax.set_ylabel("fitted slope")
    ax.set_title("One outlier drags the MSE fit away; the MAE fit barely notices")
    ax.legend(loc="upper left")


def cost_surface(fig, ax, p: Palette) -> None:
    """Contours of MSE over (w, b) — the bowl that makes optimisation easy."""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([2.0, 4.0, 5.0, 4.0, 5.0])

    w = np.linspace(-0.6, 1.8, 220)
    b = np.linspace(0.4, 4.0, 220)
    W, B = np.meshgrid(w, b)
    cost = np.zeros_like(W)
    for xi, yi in zip(x, y):
        cost += (yi - (W * xi + B)) ** 2
    cost /= len(x)

    levels = np.geomspace(cost.min() + 0.02, cost.max(), 14)
    cs = ax.contour(W, B, cost, levels=levels, colors=p.blue, linewidths=1.0, alpha=0.85)
    ax.clabel(cs, inline=True, fontsize=7, fmt="%.1f")

    ax.plot(0.6, 2.2, marker="*", markersize=16, color=p.amber, linestyle="none",
            label="minimum  $(w{=}0.6,\\; b{=}2.2)$")
    ax.set_xlabel("slope $w$")
    ax.set_ylabel("intercept $b$")
    ax.set_title("MSE over the two parameters is a convex bowl — one minimum, no traps")
    ax.legend(loc="upper right")


FIGURES = [
    figure("loss-shapes", loss_shapes, size=(8.0, 4.4)),
    figure("outlier-sensitivity", outlier_sensitivity, size=(8.0, 4.4)),
    figure("cost-surface", cost_surface, size=(8.0, 5.0)),
]
