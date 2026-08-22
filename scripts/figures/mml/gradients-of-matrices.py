"""Figures for *Gradients of Matrices*.

1. `tensor-shape-ladder` — the shape bookkeeping of §5.4, which is where readers
   lose the thread. Differentiating a matrix with respect to a matrix gives a
   fourth-order tensor, and the figure lays out the shape at each step for the
   book's own examples, plus the two flattenings that make it computable: collapse
   the matrix into a vector, or read the Jacobian as a partitioned block matrix.

2. `identities-verified` — every gradient rule §5.4 and §5.5 state, checked against
   a finite-difference Jacobian of the same function. The bar chart is the relative
   error of each rule, and every bar sits at machine precision. A rule with a
   transposed factor or a missing trace would stand out immediately.

3. `trace-gradient-structure` — d tr(AXB) / dX = (BA)^T, drawn. The gradient of a
   scalar function of a matrix is a matrix of the same shape as X, and its entries
   have visible structure: it is a rank-limited outer-product pattern whenever A
   and B are thin, which is exactly what makes the identity worth memorising.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure


def tensor_shape_ladder(fig, ax, p: Palette) -> None:
    """The shapes, and the two ways to flatten them."""
    ax.axis("off")

    ax.text(
        0.5, 1.0,
        "differentiating with respect to a matrix: the shapes",
        transform=ax.transAxes, ha="center", va="top",
        color=p.fg, fontsize=11, fontweight="bold",
    )

    rows = [
        ("f(X) = tr(AXB)", "R^{ExF} -> R", "df/dX", "1 x (E x F)",
         "a scalar of a matrix: one row, E*F columns"),
        ("f(X) = Ax,  x in R^N", "R^N -> R^M", "df/dx", "M x N",
         "Example 5.9: the answer is A itself"),
        ("f(X) = AX,  X in R^{NxP}", "R^{NxP} -> R^{MxP}", "df/dX", "(M x P) x (N x P)",
         "a matrix of a matrix: a FOURTH-order tensor"),
        ("f(X) = X^{-1}", "R^{nxn} -> R^{nxn}", "df/dX", "(n x n) x (n x n)",
         "same, and the rule is -X^{-1} (dX) X^{-1}"),
        ("f(X) = X^T X", "R^{nxm} -> R^{mxm}", "df/dX", "(m x m) x (n x m)",
         "the Gram map of §4.5, differentiated"),
    ]

    y = 0.86
    for label, x in (("function", 0.03), ("as a map", 0.30), ("derivative", 0.52),
                     ("shape", 0.63), ("what that means", 0.80)):
        ax.text(x, y, label, color=p.muted, fontsize=8.4, fontweight="bold",
                transform=ax.transAxes)

    for i, (fn, mp, dv, shape, note) in enumerate(rows):
        yy = 0.78 - i * 0.085
        ax.text(0.03, yy, fn, color=p.fg, fontsize=8.4, family="monospace",
                transform=ax.transAxes)
        ax.text(0.30, yy, mp, color=p.muted, fontsize=8.0, family="monospace",
                transform=ax.transAxes)
        ax.text(0.52, yy, dv, color=p.fg, fontsize=8.4, family="monospace",
                transform=ax.transAxes)
        ax.text(0.63, yy, shape, color=p.amber, fontsize=8.4, family="monospace",
                fontweight="bold", transform=ax.transAxes)
        ax.text(0.80, yy, note, color=p.muted, fontsize=7.6, transform=ax.transAxes)

    ax.text(
        0.03, 0.30,
        "two ways to make a fourth-order tensor computable",
        transform=ax.transAxes, color=p.green, fontsize=9.4, fontweight="bold",
    )
    ax.text(
        0.03, 0.24,
        "1. FLATTEN.  Re-shape X in R^{NxP} into a vector in R^{NP}, and the\n"
        "   derivative becomes an ordinary Jacobian of size (MP) x (NP). This is\n"
        "   what every autodiff library does internally, and it is why a library\n"
        "   gradient always comes back with the same shape as the parameter.\n\n"
        "2. PARTITION.  Keep the tensor, but read it as an M x N grid of P x P\n"
        "   blocks. The book's §5.4 uses this, and it is the version to use by\n"
        "   hand, because each block is usually a familiar small object.",
        transform=ax.transAxes, color=p.fg, fontsize=8.2, family="monospace", va="top",
    )


def identities_verified(fig, ax, p: Palette) -> None:
    """Every rule in §5.4 and §5.5, against a finite-difference Jacobian."""
    rng = np.random.default_rng(11)

    def numeric_jac(f, x, h=1e-6):
        """Central-difference Jacobian of a flattened function of a flat input."""
        x = np.asarray(x, dtype=float).ravel()
        f0 = np.asarray(f(x)).ravel()
        J = np.zeros((f0.size, x.size))
        for j in range(x.size):
            e = np.zeros_like(x)
            e[j] = h
            J[:, j] = (np.asarray(f(x + e)).ravel() - np.asarray(f(x - e)).ravel()) / (2 * h)
        return J

    tests = []

    # d(Ax)/dx = A                                              (Example 5.9)
    M, N = 4, 3
    Am = rng.normal(size=(M, N))
    x0 = rng.normal(size=N)
    tests.append(("$d(Ax)/dx = A$", numeric_jac(lambda v: Am @ v, x0), Am))

    # d(x^T x)/dx = 2 x^T
    tests.append((
        "$d(x^\\top x)/dx = 2x^\\top$",
        numeric_jac(lambda v: np.array([v @ v]), x0),
        (2 * x0).reshape(1, -1),
    ))

    # d(x^T A x)/dx = x^T (A + A^T)
    As = rng.normal(size=(N, N))
    tests.append((
        "$d(x^\\top Ax)/dx = x^\\top(A + A^\\top)$",
        numeric_jac(lambda v: np.array([v @ As @ v]), x0),
        (x0 @ (As + As.T)).reshape(1, -1),
    ))

    # d f(z)/dx with z = A x + b, f = sin elementwise            (Exercise 5.7b)
    E, D = 4, 3
    Ab = rng.normal(size=(E, D))
    bb = rng.normal(size=E)
    xb = rng.normal(size=D)
    zb = Ab @ xb + bb
    tests.append((
        "$d\\,\\sin(Ax+b)/dx = \\mathrm{diag}(\\cos z)A$",
        numeric_jac(lambda v: np.sin(Ab @ v + bb), xb),
        np.diag(np.cos(zb)) @ Ab,
    ))

    # d log(1 + x^T x)/dx = 2 x^T / (1 + x^T x)                  (Exercise 5.7a)
    tests.append((
        "$d\\log(1 + x^\\top x)/dx$",
        numeric_jac(lambda v: np.array([np.log(1 + v @ v)]), x0),
        (2 * x0 / (1 + x0 @ x0)).reshape(1, -1),
    ))

    # d tr(AXB)/dX = (BA)^T, flattened row-major to match numeric_jac
    Dd, Ee, Ff = 3, 4, 2
    Aa = rng.normal(size=(Dd, Ee))
    Bb = rng.normal(size=(Ff, Dd))
    X0 = rng.normal(size=(Ee, Ff))
    tests.append((
        "$d\\,\\mathrm{tr}(AXB)/dX = (BA)^\\top$",
        numeric_jac(lambda v: np.array([np.trace(Aa @ v.reshape(Ee, Ff) @ Bb)]), X0),
        (Bb @ Aa).T.reshape(1, -1),
    ))

    # d(X^{-1})/dX contracted with a direction: -X^{-1} H X^{-1}
    n = 3
    Xn = rng.normal(size=(n, n)) + 2.5 * np.eye(n)
    H = rng.normal(size=(n, n))
    h = 1e-6
    num = (np.linalg.inv(Xn + h * H) - np.linalg.inv(Xn - h * H)) / (2 * h)
    ana = -np.linalg.inv(Xn) @ H @ np.linalg.inv(Xn)
    tests.append(("$d(X^{-1}) = -X^{-1}(dX)X^{-1}$", num, ana))

    # d|det X|/dX = det(X) X^{-T}
    num2 = numeric_jac(lambda v: np.array([np.linalg.det(v.reshape(n, n))]), Xn)
    ana2 = (np.linalg.det(Xn) * np.linalg.inv(Xn).T).reshape(1, -1)
    tests.append(("$d\\det X/dX = \\det(X)X^{-\\top}$", num2, ana2))

    labels = [t[0] for t in tests]
    errs = []
    for _, num, ana in tests:
        num = np.asarray(num, dtype=float)
        ana = np.asarray(ana, dtype=float).reshape(num.shape)
        scale = max(float(np.abs(ana).max()), 1e-12)
        errs.append(float(np.abs(num - ana).max()) / scale)

    ypos = np.arange(len(labels))
    bars = ax.barh(ypos, errs, color=p.green, alpha=0.85, height=0.6)
    ax.set_yticks(ypos, labels, fontsize=8.6)
    ax.set_xscale("log")
    ax.set_xlabel("largest relative disagreement with a central-difference Jacobian")
    ax.invert_yaxis()
    ax.axvline(1e-9, color=p.muted, linewidth=1.0, linestyle="--")
    ax.set_xlim(1e-13, 1e-6)
    ax.set_title("eight gradient identities, each checked numerically", fontsize=10.5)

    for b, e in zip(bars, errs):
        ax.text(e * 1.35, b.get_y() + b.get_height() / 2, f"{e:.1e}",
                va="center", color=p.fg, fontsize=7.6, family="monospace")

    ax.text(
        0.985, 0.03,
        f"worst of the eight: {max(errs):.1e}\n"
        f"dashed line: 1e-9, the level a central\n"
        f"difference can reach at h = 1e-6",
        transform=ax.transAxes, ha="right", va="bottom",
        color=p.muted, fontsize=7.6, family="monospace",
    )


def trace_gradient_structure(fig, ax, p: Palette) -> None:
    """d tr(AXB)/dX = (BA)^T has visible structure."""
    fig.clear()
    axes = fig.subplots(1, 3, gridspec_kw={"width_ratios": [1, 1, 1.15]})
    rng = np.random.default_rng(4)

    D, E, F = 2, 7, 6
    A = rng.normal(size=(D, E))
    B = rng.normal(size=(F, D))
    G = (B @ A).T                      # the gradient, shape E x F

    for a, M, title in (
        (axes[0], A, f"$A$, {D}x{E}"),
        (axes[1], B, f"$B$, {F}x{D}"),
        (axes[2], G, f"$(BA)^\\top$, {E}x{F} — same shape as $X$"),
    ):
        span = float(np.abs(M).max())
        im = a.imshow(M, cmap="RdBu_r", vmin=-span, vmax=span, aspect="auto")
        a.set_title(title, fontsize=9.5)
        a.set_xticks([])
        a.set_yticks([])
        for (i, j), v in np.ndenumerate(M):
            a.text(j, i, f"{v:+.1f}", ha="center", va="center",
                   color=p.bg if abs(v) > span * 0.55 else p.fg, fontsize=6.4)

    r = int(np.linalg.matrix_rank(G))
    fig.text(
        0.5, -0.04,
        f"$A$ is {D}x{E} and $B$ is {F}x{D}, so $BA$ has rank at most {D} — measured rank of the "
        f"gradient: {r}. The gradient of a scalar function of a matrix always has the SHAPE of that "
        f"matrix, and here it also inherits a rank ceiling from the factors, which is why the "
        f"identity is worth knowing rather than re-deriving.",
        ha="center", va="top", color=p.muted, fontsize=8.4,
    )


FIGURES = [
    figure("tensor-shape-ladder", tensor_shape_ladder, size=(10.6, 5.4)),
    figure("identities-verified", identities_verified, size=(9.2, 4.8)),
    figure("trace-gradient-structure", trace_gradient_structure, size=(11.2, 3.6), axes=False),
]
