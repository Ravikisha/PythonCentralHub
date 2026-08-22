"""Shared datasets for the *Mathematics for Machine Learning* figures.

Every figure module in this group imports from here rather than seeding its own
generator, for two reasons:

1. **The same data has to appear on many pages.** The two-moons set is drawn by
   the SVM kernel figures (Ch 12) and by the projection figures (Ch 3); the
   polynomial set is fitted by Ch 8's capacity curve and Ch 9's degree sweep.
   When the reader meets it twice it must be the *same* scatter, or the
   cross-references between chapters quietly stop being true.
2. **Pages quote numbers from these plots.** A page that says "the singular
   values fall off a cliff after the fourth" is only correct while the matrix is
   fixed. Every helper here is seeded and deterministic, and the seed is a
   parameter so a page can pin its own.

Nothing here plots. No matplotlib import, so a page module can use these
helpers in a docstring example or a doctest without dragging in the Agg backend.

``build.py`` skips files whose names start with an underscore, so this module is
never mistaken for a page module.
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------- #
# Clusters and mixtures — Ch 6 (Gaussians), Ch 10 (PCA), Ch 11 (GMM)
# --------------------------------------------------------------------------- #


def gaussian_blobs(
    n: int = 300,
    k: int = 3,
    seed: int = 0,
    spread: float = 3.2,
    scale: float = 0.75,
) -> tuple[np.ndarray, np.ndarray]:
    """``k`` anisotropic Gaussian clusters in 2-D.

    Anisotropic on purpose: isotropic blobs make PCA and GMM look trivially
    easy, because the principal axes land on the coordinate axes and a spherical
    covariance fits as well as a full one. Each cluster here gets its own random
    rotation and aspect ratio, so the covariance structure is the thing the
    reader has to see.

    Returns ``(X, y)`` with ``X`` of shape ``(n, 2)`` and integer labels ``y``.
    The labels exist so a figure can colour the true clusters behind a fitted
    model; no page treats this as a supervised problem.
    """
    rng = np.random.default_rng(seed)
    centres = rng.uniform(-spread, spread, size=(k, 2))
    per = n // k

    chunks, labels = [], []
    for j in range(k):
        count = per if j < k - 1 else n - per * (k - 1)
        angle = rng.uniform(0, np.pi)
        rot = np.array(
            [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
        )
        stretch = np.diag(rng.uniform(0.35, 1.0, size=2) * scale)
        pts = rng.standard_normal((count, 2)) @ (stretch @ rot.T) + centres[j]
        chunks.append(pts)
        labels.append(np.full(count, j))

    return np.vstack(chunks), np.concatenate(labels)


def correlated_gaussian(
    n: int = 400,
    rho: float = 0.8,
    seed: int = 1,
    sd: tuple[float, float] = (1.0, 1.6),
) -> np.ndarray:
    """One 2-D Gaussian sample with a prescribed correlation ``rho``.

    Built by Cholesky rather than by ``multivariate_normal``, because that is
    exactly the construction the Cholesky page (§4.3) claims works: form the
    covariance, factor it as ``L Lᵀ``, and push standard normal noise through
    ``L``. The figure and the page's code block are then the same argument.
    """
    sx, sy = sd
    cov = np.array([[sx**2, rho * sx * sy], [rho * sx * sy, sy**2]])
    L = np.linalg.cholesky(cov)
    rng = np.random.default_rng(seed)
    return rng.standard_normal((n, 2)) @ L.T


# --------------------------------------------------------------------------- #
# Regression — Ch 5 (Taylor), Ch 8 (capacity), Ch 9 (linear regression)
# --------------------------------------------------------------------------- #


def polynomial_data(
    n: int = 30,
    degree: int = 3,
    noise: float = 0.25,
    seed: int = 2,
    domain: tuple[float, float] = (-1.0, 1.0),
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A noisy sample from a fixed polynomial of the given degree.

    Returns ``(x, y, coefficients)`` with coefficients in ``numpy.polyval``
    order (highest power first), so a page can state the *true* function and
    then show what a fit of the wrong degree does to it.

    The coefficients are drawn once from the seed and then scaled so the clean
    signal spans roughly ``[-1, 1]`` on the domain. Without that scaling the
    noise level would mean something different at every degree, and the
    overfitting figures across Ch 8 and Ch 9 would not be comparable.
    """
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(*domain, size=n))
    coef = rng.uniform(-1.0, 1.0, size=degree + 1)

    grid = np.linspace(*domain, 200)
    span = np.abs(np.polyval(coef, grid)).max()
    coef = coef / max(span, 1e-12)

    y = np.polyval(coef, x) + noise * rng.standard_normal(n)
    return x, y, coef


def linear_data(
    n: int = 20,
    slope: float = 1.4,
    intercept: float = -0.5,
    noise: float = 0.35,
    seed: int = 3,
) -> tuple[np.ndarray, np.ndarray]:
    """A small, honestly-linear dataset for the least-squares pages.

    Small on purpose: at ``n = 20`` the reader can see every residual, and the
    Bayesian predictive band (§9.3) is visibly wider at the edges of the data,
    which is the whole point of the figure. At ``n = 500`` the band collapses
    and the page loses its argument.
    """
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(-2.5, 2.5, size=n))
    y = intercept + slope * x + noise * rng.standard_normal(n)
    return x, y


# --------------------------------------------------------------------------- #
# Classification — Ch 12 (SVM), Ch 3 (projection of labelled data)
# --------------------------------------------------------------------------- #


def two_moons(n: int = 200, noise: float = 0.16, seed: int = 4) -> tuple[np.ndarray, np.ndarray]:
    """The interleaving-crescents set, written out rather than imported.

    scikit-learn ships ``make_moons``, but this group must render without
    scikit-learn installed — ``build.py`` runs on whatever Python the author
    has, and the figures are committed so the site build never sees Python at
    all. Twenty lines here removes a dependency from the render path.

    Labels are ``-1`` and ``+1``, not ``0`` and ``1``, because that is the
    convention Chapter 12 uses throughout: the margin condition is
    ``yᵢ(wᵗxᵢ + b) ≥ 1``, which only reads correctly with symmetric labels.
    """
    rng = np.random.default_rng(seed)
    half = n // 2

    t_out = np.linspace(0, np.pi, half)
    outer = np.c_[np.cos(t_out), np.sin(t_out)]

    t_in = np.linspace(0, np.pi, n - half)
    inner = np.c_[1 - np.cos(t_in), 0.5 - np.sin(t_in)]

    X = np.vstack([outer, inner]) + noise * rng.standard_normal((n, 2))
    y = np.concatenate([np.full(half, -1), np.full(n - half, 1)])
    return X, y


def linearly_separable(
    n: int = 60,
    margin: float = 0.9,
    seed: int = 5,
) -> tuple[np.ndarray, np.ndarray]:
    """Two clouds with a genuine gap, for the hard-margin figures.

    ``margin`` is the half-width of the empty corridor around the true boundary
    ``x₂ = x₁``. Points are rejected and resampled until they clear it, so the
    hard-margin SVM on this data is feasible — which matters, because the §12.2
    page contrasts it against ``two_moons``, where it is not.
    """
    rng = np.random.default_rng(seed)
    pts, labels = [], []
    while len(pts) < n:
        p = rng.uniform(-3, 3, size=2)
        signed = (p[1] - p[0]) / np.sqrt(2.0)
        if abs(signed) < margin:
            continue
        pts.append(p)
        labels.append(1 if signed > 0 else -1)
    return np.array(pts), np.array(labels)


# --------------------------------------------------------------------------- #
# Matrices — Ch 2 (rank), Ch 4 (SVD, low-rank approximation)
# --------------------------------------------------------------------------- #


def digit_matrix(size: int = 24) -> np.ndarray:
    """A small greyscale image, drawn from shapes, for rank-k reconstruction.

    Hand-drawn rather than loaded: the SVD approximation figures need a matrix
    whose singular values decay fast enough that rank 4 already looks like the
    original, and whose structure a reader recognises at a glance so the
    degradation is obvious. Concentric rectangles plus a diagonal do both, and
    the file stays dependency-free.

    Returns a ``(size, size)`` array in ``[0, 1]``.
    """
    img = np.zeros((size, size))
    for r in range(size):
        for c in range(size):
            ring = min(r, c, size - 1 - r, size - 1 - c)
            img[r, c] = 0.15 + 0.28 * (ring % 3)
    idx = np.arange(size)
    img[idx, idx] = 1.0
    img[idx, size - 1 - idx] = 0.85
    return np.clip(img, 0.0, 1.0)


def blocks_image(size: int = 64) -> np.ndarray:
    """A low-rank test image: smooth sky, axis-aligned blocks, one soft glow.

    Written rather than loaded, and shaped deliberately. Every axis-aligned
    rectangle of constant value is a rank-1 matrix, so a scene made of a handful
    of them has a small exact rank with fast singular-value decay -- which is the
    behaviour the book's Stonehenge figures show and the behaviour a rank-k
    approximation page needs. A concentric-rings pattern would look tidier and be
    full rank, so the approximation would never converge and the figure would
    teach the wrong lesson.

    At the default size the rank is 8, the top five singular values carry about
    99.6% of the squared energy, and the reconstruction is exact from rank 8.

    Returns a ``(size, size)`` array in ``[0, 1]``.
    """
    img = np.zeros((size, size))
    rows = np.linspace(0.0, 1.0, size)[:, None]
    img += 0.10 + 0.25 * rows                      # rank 1: a smooth gradient

    # Each entry is (row start, row end, col start, col end, value), in fractions.
    rects = [
        (0.62, 0.98, 0.06, 0.20, 0.55),
        (0.30, 0.98, 0.26, 0.36, 0.72),
        (0.24, 0.32, 0.06, 0.52, 0.85),
        (0.45, 0.98, 0.60, 0.72, 0.65),
        (0.70, 0.98, 0.78, 0.94, 0.48),
        (0.38, 0.46, 0.58, 0.96, 0.80),
    ]
    for r0, r1, c0, c1, value in rects:
        img[int(r0 * size) : int(r1 * size), int(c0 * size) : int(c1 * size)] = value

    xs = np.linspace(0.0, 1.0, size)
    X, Y = np.meshgrid(xs, xs)
    img += 0.18 * np.exp(-(((X - 0.5) ** 2 + (Y - 0.16) ** 2) / 0.012))
    return np.clip(img, 0.0, 1.0)


def rank_deficient(
    rows: int = 12,
    cols: int = 8,
    rank: int = 3,
    noise: float = 0.0,
    seed: int = 6,
) -> np.ndarray:
    """An exactly-rank-``rank`` matrix, optionally plus tiny noise.

    With ``noise = 0`` the trailing singular values are zero to floating-point
    round-off, which is what the rank page needs. With ``noise = 1e-10`` they
    are small but nonzero — which is the *actual* situation in every real
    computation, and the reason ``np.linalg.matrix_rank`` takes a tolerance.
    Both figures come from this one helper so the comparison is honest.
    """
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((rows, rank)) @ rng.standard_normal((rank, cols))
    if noise:
        A = A + noise * rng.standard_normal((rows, cols))
    return A


def ill_conditioned(n: int = 6, kappa: float = 1e6, seed: int = 7) -> np.ndarray:
    """A square matrix with a prescribed condition number.

    Built by choosing the singular values outright — geometrically spaced from
    ``1`` down to ``1/kappa`` — and sandwiching them between two random
    orthogonal matrices from a QR decomposition. A Hilbert matrix would also be
    ill conditioned, but its κ is whatever it happens to be; here the page can
    say "κ = 10⁶" and mean it.
    """
    rng = np.random.default_rng(seed)
    Q1, _ = np.linalg.qr(rng.standard_normal((n, n)))
    Q2, _ = np.linalg.qr(rng.standard_normal((n, n)))
    s = np.geomspace(1.0, 1.0 / kappa, n)
    return Q1 @ np.diag(s) @ Q2.T


# --------------------------------------------------------------------------- #
# Anscombe-style pathologies — Ch 6 (correlation is not dependence)
# --------------------------------------------------------------------------- #


def same_correlation(n: int = 120, seed: int = 8) -> dict[str, np.ndarray]:
    """Four 2-D datasets that share a correlation coefficient but nothing else.

    The §6.4 page claims that a single correlation number hides the shape of a
    relationship. That claim needs a figure where the four panels genuinely
    report the same ``r``, so each dataset here is standardised and then rotated
    to hit the target correlation exactly rather than approximately.

    Returns a dict of ``name -> (n, 2)`` array, in the order the figure draws
    them: ``linear``, ``curved``, ``clustered``, ``outlier``.
    """
    rng = np.random.default_rng(seed)
    target = 0.8

    def _fit(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Standardise, then mix in a second orthogonal component to hit r."""
        x = (x - x.mean()) / x.std()
        y = (y - y.mean()) / y.std()
        resid = y - np.dot(y, x) / np.dot(x, x) * x
        resid = resid / resid.std()
        return np.c_[x, target * x + np.sqrt(1 - target**2) * resid]

    x = rng.uniform(-2, 2, n)
    linear = _fit(x, x + 0.5 * rng.standard_normal(n))

    xc = rng.uniform(-2, 2, n)
    curved = _fit(xc, xc**2)

    xg = np.r_[rng.normal(-1.4, 0.25, n // 2), rng.normal(1.4, 0.25, n - n // 2)]
    clustered = _fit(xg, xg + 0.3 * rng.standard_normal(n))

    xo = np.r_[rng.normal(0, 0.3, n - 4), np.array([3.0, 3.1, 3.2, 3.3])]
    yo = np.r_[rng.normal(0, 0.3, n - 4), np.array([3.0, 3.2, 3.1, 3.4])]
    outlier = _fit(xo, yo)

    return {
        "linear": linear,
        "curved": curved,
        "clustered": clustered,
        "outlier": outlier,
    }


# --------------------------------------------------------------------------- #
# A genuinely high-dimensional dataset — Ch 2 (rank), Ch 10 (PCA)
# --------------------------------------------------------------------------- #


def digits_dataset() -> tuple[np.ndarray, np.ndarray, str]:
    """The 8x8 handwritten-digit images, centred, as a (1797, 64) matrix.

    Returns ``(X, y, source)`` where ``source`` names which path was taken.

    The rest of this module is deliberately dependency-free, so this helper
    *tries* scikit-learn and falls back to a synthetic low-rank-plus-noise matrix
    with the same shape. The fallback is not the same data and the figures that
    use it say so via the returned ``source`` string — a figure must never claim
    to show real data when it is showing a stand-in.

    Real digits are worth the try because they make a point synthetic data
    cannot: the matrix has rank 61 rather than 64, because three border pixels
    are blank in every single image. Exact dependence in real data is usually
    something dull like that, while the *interesting* redundancy is the soft kind
    rank cannot see.
    """
    try:
        from sklearn.datasets import load_digits  # noqa: PLC0415

        d = load_digits()
        X = d.data.astype(float)
        return X - X.mean(axis=0), d.target, "scikit-learn load_digits"
    except Exception:
        rng = np.random.default_rng(21)
        latent = rng.standard_normal((1797, 10))
        mixing = rng.standard_normal((10, 64)) * 4.0
        X = latent @ mixing + rng.standard_normal((1797, 64)) * 0.6
        return X - X.mean(axis=0), np.zeros(1797, dtype=int), "synthetic fallback"
