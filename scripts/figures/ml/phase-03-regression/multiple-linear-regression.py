"""Figures for *Multiple Linear Regression*."""

import numpy as np

from _style import Palette, figure


def coefficient_bars(fig, ax, p: Palette) -> None:
    """Standardised coefficients on the diabetes dataset — size and sign at a glance."""
    from sklearn.datasets import load_diabetes
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler

    data = load_diabetes()
    X = StandardScaler().fit_transform(data.data)
    model = LinearRegression().fit(X, data.target)

    order = np.argsort(model.coef_)
    names = [data.feature_names[i] for i in order]
    values = model.coef_[order]
    colors = [p.red if v < 0 else p.blue for v in values]

    ax.barh(names, values, color=colors, height=0.65)
    ax.axvline(0, color=p.muted, linewidth=1.1)
    ax.set_xlabel("coefficient (target units per standard deviation of the feature)")
    ax.set_title("Standardise first, then coefficients are comparable to each other")


def multicollinearity(fig, axes, p: Palette) -> None:
    """Correlated features make individual coefficients unstable, not the predictions."""
    axs = fig.subplots(1, 2)
    rng = np.random.default_rng(11)
    n = 80

    coef_pairs, coef_pairs_corr = [], []
    for _ in range(120):
        x1 = rng.normal(size=n)
        x2_ind = rng.normal(size=n)
        x2_corr = 0.99 * x1 + 0.14 * rng.normal(size=n)
        for store, x2 in ((coef_pairs, x2_ind), (coef_pairs_corr, x2_corr)):
            y = 2 * x1 + 2 * x2 + rng.normal(0, 1.0, n)
            design = np.c_[np.ones(n), x1, x2]
            coef, *_ = np.linalg.lstsq(design, y, rcond=None)
            store.append(coef[1:])

    for ax, pairs, title in ((axs[0], np.array(coef_pairs), "Independent features (r ≈ 0)"),
                             (axs[1], np.array(coef_pairs_corr), "Collinear features (r ≈ 0.99)")):
        ax.scatter(pairs[:, 0], pairs[:, 1], color=p.blue, s=18, alpha=0.7, edgecolor="none")
        ax.plot(2, 2, marker="*", markersize=15, color=p.amber, linestyle="none")
        ax.set_title(f"{title}\nspread = {pairs.std(axis=0).mean():.2f}", fontsize=9.5)
        ax.set_xlabel("$\\hat{w}_1$")
        ax.axhline(2, color=p.muted, linewidth=0.9, linestyle="--")
        ax.axvline(2, color=p.muted, linewidth=0.9, linestyle="--")
    axs[0].set_ylabel("$\\hat{w}_2$")
    fig.suptitle("120 refits on fresh samples: collinearity scatters the coefficients",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def predicted_vs_actual(fig, ax, p: Palette) -> None:
    """The all-purpose multi-feature diagnostic: predicted against actual."""
    from sklearn.datasets import load_diabetes
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split

    data = load_diabetes()
    X_tr, X_te, y_tr, y_te = train_test_split(data.data, data.target,
                                              test_size=0.3, random_state=42)
    model = LinearRegression().fit(X_tr, y_tr)
    pred = model.predict(X_te)
    r2 = model.score(X_te, y_te)

    lim = [min(y_te.min(), pred.min()) - 10, max(y_te.max(), pred.max()) + 10]
    ax.plot(lim, lim, color=p.muted, linestyle="--", linewidth=1.3, label="perfect prediction")
    ax.scatter(y_te, pred, color=p.blue, s=26, alpha=0.7, edgecolor="none",
               label=f"held-out patients  ·  $R^2$ = {r2:.2f}")

    ax.set_xlabel("actual disease progression")
    ax.set_ylabel("predicted")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_title("Ten features instead of one: $R^2$ rises from 0.34 to about 0.48")
    ax.legend(loc="upper left")


FIGURES = [
    figure("coefficient-bars", coefficient_bars, size=(8.0, 4.4)),
    figure("multicollinearity", multicollinearity, size=(8.4, 4.2), axes=False),
    figure("predicted-vs-actual", predicted_vs_actual, size=(7.2, 5.0)),
]
