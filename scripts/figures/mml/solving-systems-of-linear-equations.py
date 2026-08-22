"""Figures for *Solving Systems of Linear Equations*.

1. `elimination-cost` — a pure-Python Gaussian elimination against
   ``np.linalg.solve``, with an n-cubed reference. Both are cubic, which is the
   book's own reason for calling direct elimination impractical for millions of
   unknowns: the constant factor is enormous but the exponent is what kills you.

2. `normal-equations-conditioning` — the measured version of the book's warning
   that computing an inverse or pseudo-inverse is "generally not recommended".
   Solving least squares via the normal equations tracks kappa squared, so on a
   log-log axis its error line has twice the slope of ``lstsq``'s and it fails at
   roughly the square root of the conditioning lstsq survives.
"""

import time

import numpy as np

from _style import Palette, figure


def _gauss_solve(A, b):
    """Gaussian elimination with partial pivoting, written out in Python."""
    n = A.shape[0]
    M = np.c_[A, b].astype(float)
    for c in range(n):
        p = c + int(np.argmax(np.abs(M[c:, c])))
        if p != c:
            M[[c, p]] = M[[p, c]]
        piv = M[c, c]
        for i in range(c + 1, n):
            f = M[i, c] / piv
            for j in range(c, n + 1):
                M[i, j] -= f * M[c, j]
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (M[i, n] - M[i, i + 1:n] @ x[i + 1:n]) / M[i, i]
    return x


def elimination_cost(fig, ax, p: Palette) -> None:
    """Hand-written elimination against the library, both cubic."""
    rng = np.random.default_rng(2)
    sizes_slow = [6, 10, 16, 24, 36, 52, 74]
    sizes_fast = [6, 12, 25, 50, 100, 200, 400]

    def timed(fn, n, repeats):
        A = rng.standard_normal((n, n)) + n * np.eye(n)   # keep it well conditioned
        b = rng.standard_normal(n)
        best = float("inf")
        for _ in range(repeats):
            t0 = time.perf_counter()
            fn(A, b)
            best = min(best, time.perf_counter() - t0)
        return best

    t_slow = [timed(_gauss_solve, n, 1) for n in sizes_slow]
    t_fast = [timed(np.linalg.solve, n, 5) for n in sizes_fast]

    ax.loglog(sizes_slow, t_slow, "o-", color=p.red, linewidth=2, markersize=4,
              label="Gaussian elimination in Python")
    ax.loglog(sizes_fast, t_fast, "s-", color=p.blue, linewidth=2, markersize=4,
              label="np.linalg.solve (LAPACK)")

    ref = np.array(sizes_slow, dtype=float)
    ax.loglog(ref, t_slow[0] * (ref / ref[0]) ** 3, ":", color=p.muted,
              linewidth=1.2, label=r"reference slope $n^3$")

    ax.set_xlabel("system size $n$")
    ax.set_ylabel("time to solve (s)")
    ax.legend(loc="upper left", fontsize=9)


def normal_equations_conditioning(fig, ax, p: Palette) -> None:
    """Least squares via the normal equations against lstsq, as kappa grows."""
    kappas = np.logspace(1, 12, 23)
    n = 8
    rng = np.random.default_rng(5)
    x_true = rng.standard_normal(n)

    err_normal, err_lstsq, used = [], [], []
    m = n + 4                    # genuinely overdetermined, which is the point
    for i, kappa in enumerate(kappas):
        # A TALL matrix with an exactly prescribed condition number, built from
        # its own SVD. Stacking extra rows onto a square ill-conditioned block
        # does not work: whichever block is better conditioned dominates, and the
        # x axis then spans a far narrower range than it claims to.
        g = np.random.default_rng(200 + i)
        U, _ = np.linalg.qr(g.standard_normal((m, m)))
        V, _ = np.linalg.qr(g.standard_normal((n, n)))
        sv = np.geomspace(1.0, 1.0 / kappa, n)
        A = U[:, :n] @ np.diag(sv) @ V.T
        b = A @ x_true

        scale = np.linalg.norm(x_true)
        try:
            xn = np.linalg.solve(A.T @ A, A.T @ b)
            en = np.linalg.norm(xn - x_true) / scale
        except np.linalg.LinAlgError:
            en = np.nan                      # the normal equations went singular
        xl = np.linalg.lstsq(A, b, rcond=None)[0]

        err_normal.append(en)
        err_lstsq.append(np.linalg.norm(xl - x_true) / scale)
        used.append(np.linalg.cond(A))

    used = np.array(used)
    eps = np.finfo(float).eps

    ax.loglog(used, np.maximum(err_normal, 1e-18), "o-", color=p.red,
              linewidth=2, markersize=4, label=r"via normal equations $A^\top A$")
    ax.loglog(used, np.maximum(err_lstsq, 1e-18), "s-", color=p.blue,
              linewidth=2, markersize=4, label="np.linalg.lstsq")
    ax.loglog(used, eps * used, ":", color=p.amber, linewidth=1.4,
              label=r"$\varepsilon\,\kappa(A)$")
    ax.loglog(used, eps * used**2, ":", color=p.purple, linewidth=1.4,
              label=r"$\varepsilon\,\kappa(A)^2$")

    ax.axhline(1.0, color=p.muted, linewidth=1, linestyle="--")
    ax.text(used[0], 1.3, "100% error: no digits left", color=p.muted, fontsize=8.5)

    ax.set_xlabel(r"condition number $\kappa(A)$")
    ax.set_ylabel("relative error in the fit")
    ax.set_ylim(1e-18, 1e3)
    ax.legend(loc="upper left", fontsize=8.5)


FIGURES = [
    figure("elimination-cost", elimination_cost, size=(7.4, 4.2)),
    figure("normal-equations-conditioning", normal_equations_conditioning, size=(7.6, 4.6)),
]
