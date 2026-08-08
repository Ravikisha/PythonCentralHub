"""Figures for *Gradient Descent Explained*."""

import numpy as np

from _style import Palette, figure

# The Phase 03 five-point dataset, with the feature centred (x - 3) so the cost
# surface is well conditioned. Centring changes the intercept's meaning — it
# becomes y-bar = 4 — but leaves the slope at 0.6, exactly as computed by hand.
X = np.c_[np.ones(5), np.array([1.0, 2.0, 3.0, 4.0, 5.0]) - 3.0]
Y = np.array([2.0, 4.0, 5.0, 4.0, 5.0])
OPT = np.array([4.0, 0.6])  # b (on centred x), w
# Hessian is 2/n · XᵀX = diag(2, 4), so descent diverges above α = 2/4 = 0.5.


def _mse(theta):
    err = X @ theta - Y
    return float((err**2).mean())


def _descend(lr, steps=60, start=(0.0, 0.0)):
    """Batch gradient descent, returning the full parameter trace."""
    theta = np.array(start, dtype=float)
    path = [theta.copy()]
    for _ in range(steps):
        grad = 2 / len(Y) * X.T @ (X @ theta - Y)
        theta = theta - lr * grad
        if not np.all(np.isfinite(theta)) or np.abs(theta).max() > 1e6:
            path.append(theta.copy())
            break
        path.append(theta.copy())
    return np.array(path)


def learning_rate_paths(fig, ax, p: Palette) -> None:
    """Three learning rates walking across the same cost contours."""
    b = np.linspace(-0.6, 6.4, 240)
    w = np.linspace(-1.6, 2.6, 240)
    B, W = np.meshgrid(b, w)
    cost = np.zeros_like(B)
    for xi, yi in zip(X[:, 1], Y):
        cost += (yi - (B + W * xi)) ** 2
    cost /= len(Y)

    ax.contour(B, W, cost, levels=np.geomspace(cost.min() + 0.05, cost.max(), 14),
               colors=p.muted, linewidths=0.8, alpha=0.75)

    runs = [
        (0.03, p.green, "α = 0.03 — crawls, never arrives"),
        (0.20, p.blue, "α = 0.20 — straight in"),
        (0.46, p.red, "α = 0.46 — oscillates across the valley"),
    ]
    for lr, color, label in runs:
        path = _descend(lr, steps=70)
        path = path[np.all(np.isfinite(path), axis=1)]
        ax.plot(path[:, 0], path[:, 1], color=color, marker="o", markersize=2.8,
                linewidth=1.4, alpha=0.95, label=label)

    ax.plot(*OPT, marker="*", markersize=17, color=p.amber, linestyle="none", label="minimum")
    ax.set_xlabel("intercept $b$")
    ax.set_ylabel("slope $w$")
    ax.set_xlim(-0.6, 6.4)
    ax.set_ylim(-1.6, 2.6)
    ax.set_title("Same start, three learning rates, 70 steps each")
    ax.legend(loc="lower right", fontsize=8)


def convergence_curves(fig, ax, p: Palette) -> None:
    """Cost against iteration for four learning rates, including a divergent one."""
    runs = [
        (0.03, p.green, "α = 0.03 — too small"),
        (0.20, p.blue, "α = 0.20 — good"),
        (0.46, p.purple, "α = 0.46 — bounces, still converges"),
        (0.55, p.red, "α = 0.55 — diverges"),
    ]
    for lr, color, label in runs:
        path = _descend(lr, steps=60)
        costs = [_mse(t) if np.all(np.isfinite(t)) else np.nan for t in path]
        ax.plot(costs, color=color, label=label)

    ax.axhline(0.48, color=p.muted, linestyle="--", linewidth=1.1,
               label="minimum MSE = 0.48")
    ax.set_yscale("log")
    ax.set_xlabel("iteration")
    ax.set_ylabel("MSE (log scale)")
    ax.set_ylim(1e-1, 1e4)
    ax.set_title("A learning curve tells you immediately which rate is wrong")
    ax.legend(loc="upper right", fontsize=8)


def scaling_contours(fig, axes, p: Palette) -> None:
    """Two panels: unscaled features give a ravine, scaled features give a bowl."""
    ax1, ax2 = fig.subplots(1, 2)

    def draw(ax, stretch, title):
        u = np.linspace(-3, 3, 200)
        v = np.linspace(-3, 3, 200)
        U, V = np.meshgrid(u, v)
        cost = (U**2) / stretch + (V**2) * stretch
        ax.contour(U, V, cost, levels=np.geomspace(0.05, 40, 12), colors=p.grid, linewidths=0.9)

        # steepest descent zig-zags across a ravine, walks straight down a bowl
        pos = np.array([-2.6, 2.4])
        pts = [pos.copy()]
        for _ in range(40):
            grad = np.array([2 * pos[0] / stretch, 2 * pos[1] * stretch])
            pos = pos - 0.12 * grad
            pts.append(pos.copy())
        pts = np.array(pts)
        ax.plot(pts[:, 0], pts[:, 1], color=p.amber, marker="o", markersize=2.5, linewidth=1.4)
        ax.plot(0, 0, marker="*", markersize=13, color=p.blue, linestyle="none")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("$\\theta_1$")
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_aspect("equal")

    draw(ax1, 8.0, "Unscaled features: a narrow ravine")
    draw(ax2, 1.0, "Scaled features: a round bowl")
    ax1.set_ylabel("$\\theta_2$")
    fig.suptitle("Feature scaling changes the shape of the cost surface, not the answer",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("learning-rate-paths", learning_rate_paths, size=(8.0, 5.0)),
    figure("convergence-curves", convergence_curves, size=(8.0, 4.4)),
    figure("scaling-contours", scaling_contours, size=(8.4, 4.4), axes=False),
]
