"""Figures for *Principal Component Analysis (PCA)*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _style import Palette, figure  # noqa: E402


def _corr_cloud(seed=0, n=180):
    rng = np.random.default_rng(seed)
    a = rng.normal(0, 2.2, n)
    b = rng.normal(0, 0.55, n)
    th = np.radians(32)
    R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
    return np.column_stack([a, b]) @ R.T


def projection_geometry(fig, axes, p: Palette) -> None:
    """Three candidate axes; only one minimises the squared residuals."""
    X = _corr_cloud()
    Xc = X - X.mean(0)
    axs = fig.subplots(1, 3, sharex=True, sharey=True)

    from sklearn.decomposition import PCA

    pc1 = PCA(n_components=2).fit(Xc).components_[0]
    best = float(np.degrees(np.arctan2(pc1[1], pc1[0])) % 180)

    for ax, deg in zip(axs, (0.0, best, 90.0)):
        u = np.array([np.cos(np.radians(deg)), np.sin(np.radians(deg))])
        t = Xc @ u
        proj = np.outer(t, u)
        for q, r in zip(Xc, proj):
            ax.plot([q[0], r[0]], [q[1], r[1]], color=p.red, lw=0.6, alpha=0.5,
                    zorder=2)
        ax.scatter(Xc[:, 0], Xc[:, 1], s=11, c=p.blue, alpha=0.7,
                   edgecolors="none", zorder=3)
        ax.scatter(proj[:, 0], proj[:, 1], s=9, c=p.amber, zorder=4)
        L = 6.5
        ax.plot([-L * u[0], L * u[0]], [-L * u[1], L * u[1]], color=p.amber, lw=2,
                zorder=1)
        var = float(t.var())
        resid = float(((Xc - proj) ** 2).sum(1).mean())
        ax.set_title(f"axis at {deg:.0f}°\nvariance {var:.2f}\n"
                     f"squared error {resid:.2f}", fontsize=9.5)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
    axs[1].set_xlabel("the middle axis is PC1", color=p.amber)


def scree_and_cumulative(fig, axes, p: Palette) -> None:
    """Individual and cumulative explained variance on the digits data."""
    from sklearn.datasets import load_digits
    from sklearn.decomposition import PCA

    X = load_digits().data
    pca = PCA().fit(X)
    evr = pca.explained_variance_ratio_
    cum = np.cumsum(evr)

    axs = fig.subplots(1, 2)
    axs[0].bar(np.arange(1, 31), evr[:30], color=p.blue)
    axs[0].set_xlabel("component")
    axs[0].set_ylabel("explained variance ratio")
    axs[0].set_title("Scree plot (first 30 of 64)")

    axs[1].plot(np.arange(1, len(cum) + 1), cum, color=p.blue)
    for i, (thr, col) in enumerate(((0.90, p.amber), (0.95, p.green))):
        d = int(np.searchsorted(cum, thr) + 1)
        axs[1].axhline(thr, color=col, ls="--", lw=1.3)
        axs[1].axvline(d, color=col, ls="--", lw=1.3)
        axs[1].annotate(f"{int(thr * 100)}% of the variance → d = {d}",
                        (d + 2.5, 0.42 - 0.11 * i), color=col, fontsize=9)
    axs[1].set_xlabel("number of components")
    axs[1].set_ylabel("cumulative explained variance")
    axs[1].set_title("How many dimensions do you actually need?")


def reconstruction_grid(fig, axes, p: Palette) -> None:
    """Compress a digit down and push it back out again."""
    from sklearn.datasets import load_digits
    from sklearn.decomposition import PCA

    digits = load_digits()
    X = digits.data
    idx = [0, 1, 2, 3]
    ds = [64, 32, 16, 8, 4, 2]

    axs = fig.subplots(len(idx), len(ds) + 1)
    for r, i in enumerate(idx):
        axs[r, 0].imshow(X[i].reshape(8, 8), cmap="gray")
        axs[r, 0].set_xticks([])
        axs[r, 0].set_yticks([])
        if r == 0:
            axs[r, 0].set_title("original", fontsize=9)
    for c, d in enumerate(ds, start=1):
        pca = PCA(n_components=d, random_state=0).fit(X)
        Xr = pca.inverse_transform(pca.transform(X[idx]))
        for r in range(len(idx)):
            axs[r, c].imshow(Xr[r].reshape(8, 8), cmap="gray")
            axs[r, c].set_xticks([])
            axs[r, c].set_yticks([])
        if True:
            axs[0, c].set_title(f"d = {d}\n{pca.explained_variance_ratio_.sum():.0%}",
                                fontsize=9)
    for ax in axs.ravel():
        ax.grid(False)


def pca_needs_scaling(fig, axes, p: Palette) -> None:
    """Un-standardised columns hand PC1 to whichever feature has big units."""
    from sklearn.datasets import load_wine
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    data = load_wine()
    X, y = data.data, data.target

    axs = fig.subplots(1, 2)
    for ax, (Xi, title) in zip(axs, [
        (X, "Raw columns"),
        (StandardScaler().fit_transform(X), "Standardised columns"),
    ]):
        pca = PCA(n_components=2, random_state=0).fit(Xi)
        Z = pca.transform(Xi)
        for c, col in zip((0, 1, 2), (p.blue, p.amber, p.green)):
            ax.scatter(Z[y == c, 0], Z[y == c, 1], s=16, c=col, edgecolors="none")
        top = data.feature_names[int(np.argmax(np.abs(pca.components_[0])))]
        ax.set_title(f"{title}\nPC1 {pca.explained_variance_ratio_[0]:.1%} — "
                     f"dominated by '{top}'", fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])


def kernel_pca(fig, axes, p: Palette) -> None:
    """Linear PCA cannot unfold concentric circles; an RBF kernel can."""
    from sklearn.datasets import make_circles
    from sklearn.decomposition import PCA, KernelPCA

    X, y = make_circles(n_samples=400, factor=0.35, noise=0.05, random_state=0)
    axs = fig.subplots(1, 3)

    for ax, (Z, title) in zip(axs, [
        (X, "Original 2-D data"),
        (PCA(n_components=2).fit_transform(X), "Linear PCA"),
        (KernelPCA(n_components=2, kernel="rbf", gamma=10).fit_transform(X),
         "Kernel PCA (RBF, gamma=10)"),
    ]):
        for c, col in ((0, p.blue), (1, p.amber)):
            ax.scatter(Z[y == c, 0], Z[y == c, 1], s=12, c=col, edgecolors="none")
        ax.set_title(title, fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])


FIGURES = [
    figure("projection-geometry", projection_geometry, size=(8.8, 3.4), axes=False),
    figure("scree-and-cumulative", scree_and_cumulative, size=(8.8, 3.5), axes=False),
    figure("reconstruction-grid", reconstruction_grid, size=(8.4, 5.0), axes=False),
    figure("pca-needs-scaling", pca_needs_scaling, size=(8.4, 3.6), axes=False),
    figure("kernel-pca", kernel_pca, size=(8.8, 3.2), axes=False),
]
