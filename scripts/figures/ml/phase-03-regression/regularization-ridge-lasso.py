"""Figures for *Regularization — Ridge and Lasso Regression*."""

import numpy as np

from _style import Palette, figure


def _diabetes():
    from sklearn.datasets import load_diabetes

    data = load_diabetes()
    return data.data, data.target, list(data.feature_names)


def coefficient_paths(fig, axes, p: Palette) -> None:
    """Ridge and Lasso coefficient paths on the same data, side by side."""
    from sklearn.linear_model import Ridge, Lasso
    from sklearn.preprocessing import StandardScaler

    X, y, names = _diabetes()
    # Penalties act on coefficient magnitude, so the features must share a scale
    # before any of these paths mean anything.
    X = StandardScaler().fit_transform(X)
    alphas = np.geomspace(1e-2, 1e3, 60)
    axs = fig.subplots(1, 2, sharey=True)

    for ax, Model, title in ((axs[0], Ridge, "Ridge (L2): everything shrinks, nothing vanishes"),
                             (axs[1], Lasso, "Lasso (L1): coefficients hit exactly zero")):
        coefs = []
        for a in alphas:
            m = Model(alpha=a, max_iter=200000)
            m.fit(X, y)
            coefs.append(m.coef_)
        coefs = np.array(coefs)

        for j in range(coefs.shape[1]):
            ax.plot(alphas, coefs[:, j], linewidth=1.5)
        ax.axhline(0, color=p.muted, linewidth=1, linestyle="--")
        ax.set_xscale("log")
        ax.set_xlabel("regularisation strength $\\alpha$ (log)")
        ax.set_title(title, fontsize=9.5)

    axs[0].set_ylabel("coefficient value")
    fig.suptitle("Ten diabetes features, penalised two different ways",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def constraint_geometry(fig, axes, p: Palette) -> None:
    """Why L1 zeroes coefficients and L2 does not: the corner of the diamond."""
    axs = fig.subplots(1, 2)
    centre = np.array([1.9, 1.15])

    def ellipses(ax):
        u = np.linspace(-0.6, 3.2, 300)
        v = np.linspace(-0.6, 2.6, 300)
        U, V = np.meshgrid(u, v)
        cost = 2.0 * (U - centre[0]) ** 2 + 0.8 * (U - centre[0]) * (V - centre[1]) \
            + 1.4 * (V - centre[1]) ** 2
        ax.contour(U, V, cost, levels=[0.35, 1.1, 2.4, 4.4, 7.2],
                   colors=p.blue, linewidths=1.0, alpha=0.9)
        ax.plot(*centre, marker="o", color=p.blue, markersize=6)
        ax.annotate("OLS solution", centre, textcoords="offset points", xytext=(8, 6),
                    fontsize=8.5, color=p.blue)

    # L1 — a diamond, touched first at a corner where one coefficient is zero
    t = 1.0
    axs[0].fill([t, 0, -t, 0], [0, t, 0, -t], color=p.amber, alpha=0.22)
    axs[0].plot([t, 0, -t, 0, t], [0, t, 0, -t, 0], color=p.amber, linewidth=1.8)
    ellipses(axs[0])
    axs[0].plot(0, t, marker="*", markersize=15, color=p.green, linestyle="none")
    axs[0].annotate("touches at a corner\n$\\theta_1 = 0$", (0, t), textcoords="offset points",
                    xytext=(-70, -34), fontsize=8.5, color=p.green)
    axs[0].set_title("Lasso: $|\\theta_1| + |\\theta_2| \\leq t$", fontsize=10)

    # L2 — a circle, touched on a smooth edge where both stay non-zero
    ang = np.linspace(0, 2 * np.pi, 200)
    axs[1].fill(t * np.cos(ang), t * np.sin(ang), color=p.amber, alpha=0.22)
    axs[1].plot(t * np.cos(ang), t * np.sin(ang), color=p.amber, linewidth=1.8)
    ellipses(axs[1])
    touch = centre / np.linalg.norm(centre) * t
    axs[1].plot(*touch, marker="*", markersize=15, color=p.green, linestyle="none")
    axs[1].annotate("touches on a curve\nboth non-zero", touch, textcoords="offset points",
                    xytext=(-96, -34), fontsize=8.5, color=p.green)
    axs[1].set_title("Ridge: $\\theta_1^2 + \\theta_2^2 \\leq t$", fontsize=10)

    for ax in axs:
        ax.axhline(0, color=p.muted, linewidth=0.9)
        ax.axvline(0, color=p.muted, linewidth=0.9)
        ax.set_xlim(-1.5, 3.2)
        ax.set_ylim(-1.5, 2.6)
        ax.set_aspect("equal")
        ax.set_xlabel("$\\theta_1$")
        ax.grid(False)
    axs[0].set_ylabel("$\\theta_2$")
    fig.suptitle("The shape of the penalty decides whether coefficients reach zero",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def alpha_vs_error(fig, ax, p: Palette) -> None:
    """Validation error against alpha — the U that picks the hyperparameter.

    Run on the degree-2 expansion (65 features) rather than the raw ten, because
    with 442 samples and ten well-behaved columns there is nothing to regularise
    and the curve would be almost flat.
    """
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import PolynomialFeatures, StandardScaler

    X, y, _ = _diabetes()
    alphas = np.geomspace(1e-2, 1e4, 34)
    scores = []
    for a in alphas:
        model = make_pipeline(
            PolynomialFeatures(2, include_bias=False), StandardScaler(), Ridge(alpha=a)
        )
        s = cross_val_score(model, X, y, cv=5, scoring="neg_mean_squared_error")
        scores.append(-s.mean())

    ax.plot(alphas, scores, color=p.blue, marker="o", markersize=3.5)
    best_i = int(np.argmin(scores))
    ax.axvline(alphas[best_i], color=p.amber, linestyle="--", linewidth=1.4,
               label=f"best $\\alpha \\approx$ {alphas[best_i]:.0f}  ·  MSE {scores[best_i]:.0f}")
    ax.axhline(scores[0], color=p.muted, linestyle=":", linewidth=1.2,
               label=f"barely penalised: MSE {scores[0]:.0f}")
    ax.set_xscale("log")
    ax.set_xlabel("$\\alpha$ (log scale)")
    ax.set_ylabel("5-fold CV mean squared error")
    ax.set_title("65 polynomial features: too little penalty overfits, too much underfits")
    ax.legend(loc="upper left")


FIGURES = [
    figure("coefficient-paths", coefficient_paths, size=(9.0, 4.2), axes=False),
    figure("constraint-geometry", constraint_geometry, size=(8.6, 4.4), axes=False),
    figure("alpha-vs-error", alpha_vs_error, size=(8.0, 4.4)),
]
