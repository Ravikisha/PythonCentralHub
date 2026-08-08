"""Shared synthetic datasets for the Phase 06 (unsupervised) figures.

Every generator is seeded, so the numbers quoted in the prose stay true across
rebuilds. Import from the page modules rather than re-rolling data per figure —
several pages compare algorithms on *the same* points and the comparison is only
meaningful if the points really are identical.
"""

from __future__ import annotations

import numpy as np
from sklearn.datasets import make_blobs, make_moons, make_swiss_roll


def blobs(n=300, k=4, seed=42, std=0.85):
    X, y = make_blobs(n_samples=n, centers=k, cluster_std=std, random_state=seed)
    return X, y


def moons(n=300, seed=42, noise=0.06):
    return make_moons(n_samples=n, noise=noise, random_state=seed)


# seed 170 places the three blob centres so the shear below genuinely overlaps
# them — the same setup scikit-learn uses in its own "assumptions" demo.
ANISO_SEED = 170
SHEAR = np.array([[0.60834549, -0.63667341], [-0.40887718, 0.85253229]])


def anisotropic(n=600, seed=ANISO_SEED):
    """Blobs sheared along a diagonal — the classic k-means failure case."""
    X, y = make_blobs(n_samples=n, centers=3, random_state=seed)
    return X @ SHEAR, y


def varied_variance(n=600, seed=ANISO_SEED):
    X, y = make_blobs(n_samples=n, centers=3, cluster_std=[1.0, 2.5, 0.5],
                      random_state=seed)
    return X, y


def structureless(n=600, seed=0):
    """Uniform noise: there is nothing to find, but k-means finds k anyway."""
    rng = np.random.default_rng(seed)
    return rng.uniform(-4, 4, size=(n, 2)), np.zeros(n)


def two_rings_with_noise(seed=7):
    """Two dense arcs plus uniform background clutter — DBSCAN's home turf."""
    rng = np.random.default_rng(seed)
    X, y = make_moons(n_samples=280, noise=0.05, random_state=seed)
    clutter = rng.uniform([-1.6, -1.0], [2.6, 1.6], size=(40, 2))
    return np.vstack([X, clutter]), np.concatenate([y, np.full(40, -1)])


def swiss_roll(n=1200, seed=42, noise=0.05):
    X, t = make_swiss_roll(n_samples=n, noise=noise, random_state=seed)
    return X, t


def contaminated(n_inliers=280, n_outliers=20, seed=3):
    """A tight bivariate-normal cloud with uniform outliers around it."""
    rng = np.random.default_rng(seed)
    cov = np.array([[1.0, 0.75], [0.75, 1.0]])
    inliers = rng.multivariate_normal([0, 0], cov, size=n_inliers)
    outliers = rng.uniform(-5, 5, size=(n_outliers, 2))
    X = np.vstack([inliers, outliers])
    y = np.concatenate([np.ones(n_inliers), -np.ones(n_outliers)])
    return X, y


def scatter(ax, X, labels, p, size=16, noise_label=-1, alpha=0.9):
    """Draw a labelled 2-D scatter with the site palette. -1 renders as grey."""
    colors = [p.blue, p.amber, p.green, p.purple, p.red]
    for lab in sorted(set(labels)):
        m = labels == lab
        if lab == noise_label:
            ax.scatter(X[m, 0], X[m, 1], s=size * 0.55, c=p.muted, marker="x",
                       linewidths=1.0, label="noise", zorder=2)
        else:
            ax.scatter(X[m, 0], X[m, 1], s=size, c=colors[int(lab) % len(colors)],
                       alpha=alpha, edgecolors="none", zorder=3)
    ax.set_xticks([])
    ax.set_yticks([])


BASKETS = [
    ["bread", "butter", "milk"],
    ["bread", "butter"],
    ["bread", "milk", "jam"],
    ["butter", "milk"],
    ["bread", "butter", "milk", "jam"],
    ["beer", "chips"],
    ["bread", "jam"],
    ["beer", "chips", "salsa"],
    ["bread", "butter", "jam"],
    ["milk", "cereal"],
    ["bread", "butter", "milk"],
    ["beer", "chips"],
    ["bread", "milk"],
    ["butter", "jam"],
    ["bread", "butter", "milk", "cereal"],
    ["chips", "salsa"],
    ["bread", "butter"],
    ["milk", "cereal", "bread"],
    ["beer", "chips", "bread"],
    ["bread", "butter", "milk"],
]
"""Twenty grocery baskets. Small enough to count by hand on the Apriori page,
large enough that support, confidence and lift come out to non-trivial values."""
