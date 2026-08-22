"""Figures for *Cholesky Decomposition*.

1. `cholesky-sampling` — the use the book names first. Independent standard
   normal noise multiplied by the Cholesky factor L acquires exactly the target
   covariance, and the figure measures the empirical covariance of fifty thousand
   samples against the matrix that was asked for. This is the transformation of
   random variables the book points at for the reparametrisation trick.

2. `cholesky-boundary` — Cholesky as a definiteness test. The lower-right entry
   of a fixed 2x2 matrix is swept, and for each value the figure reports whether
   the factorisation succeeds, the smallest eigenvalue, and the determinant. All
   three agree on the same boundary, and Cholesky is the only one of them that
   needs no tolerance.

3. `determinant-via-cholesky` — why numerical libraries factor first. For SPD
   matrices of growing size, the determinant computed as the squared product of
   the Cholesky diagonal is compared against a general LU determinant. On
   ill-conditioned input the two diverge, and the figure shows by how much.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

# The target covariance for the sampling figure. Strongly correlated, so a
# failure to reproduce it would be obvious rather than subtle.
TARGET = np.array([[2.0, 1.3], [1.3, 1.4]])


def cholesky_sampling(fig, ax, p: Palette) -> None:
    """L z has covariance L L-transpose, measured."""
    fig.clear()
    left, mid, right = fig.subplots(1, 3, gridspec_kw={"width_ratios": [1.0, 1.0, 1.15]})

    L = np.linalg.cholesky(TARGET)
    rng = np.random.default_rng(7)
    n = 50000
    Z = rng.normal(size=(n, 2))
    X = Z @ L.T

    emp_z = np.cov(Z.T)
    emp_x = np.cov(X.T)

    for a, data, title, colour in (
        (left, Z, "$z \\sim \\mathcal{N}(0, I)$", p.blue),
        (mid, X, "$x = Lz$", p.amber),
    ):
        a.scatter(data[:4000, 0], data[:4000, 1], s=2, alpha=0.18, color=colour,
                  edgecolor="none")
        # The one-sigma ellipse of the empirical covariance, drawn from its own
        # eigendecomposition rather than assumed.
        C = np.cov(data.T)
        w, V = np.linalg.eigh(C)
        th = np.linspace(0, 2 * np.pi, 200)
        circ = np.stack([np.cos(th), np.sin(th)], axis=1)
        ell = circ * np.sqrt(w) @ V.T
        a.plot(ell[:, 0], ell[:, 1], color=p.fg, linewidth=1.8)
        a.set_title(title, fontsize=10.5)
        a.set_aspect("equal")
        a.set_xlim(-5.2, 5.2)
        a.set_ylim(-5.2, 5.2)
        a.set_xlabel("$x_1$")
    left.set_ylabel("$x_2$")

    # The unit vectors, pushed through L, so the ellipse's axes are traceable.
    for i, colour in enumerate((p.green, p.purple)):
        e = np.zeros(2)
        e[i] = 1.0
        left.annotate("", xy=tuple(e * 2), xytext=(0, 0),
                      arrowprops=dict(arrowstyle="->", color=colour, linewidth=2.2))
        mid.annotate("", xy=tuple((L @ e) * 2), xytext=(0, 0),
                     arrowprops=dict(arrowstyle="->", color=colour, linewidth=2.2))

    right.axis("off")
    right.text(
        0.0, 0.98,
        "target  =  [[%.2f, %.2f],\n            [%.2f, %.2f]]\n\n"
        "L       =  [[%.4f, %.4f],\n            [%.4f, %.4f]]\n\n"
        "L L^T   =  [[%.4f, %.4f],\n            [%.4f, %.4f]]\n\n"
        "cov(z)  =  [[%.4f, %.4f],\n            [%.4f, %.4f]]\n\n"
        "cov(Lz) =  [[%.4f, %.4f],\n            [%.4f, %.4f]]\n\n"
        "samples: %d\n"
        "largest |cov(Lz) - target| = %.4f"
        % (
            TARGET[0, 0], TARGET[0, 1], TARGET[1, 0], TARGET[1, 1],
            L[0, 0], L[0, 1], L[1, 0], L[1, 1],
            *(L @ L.T).ravel(),
            *emp_z.ravel(),
            *emp_x.ravel(),
            n,
            float(np.abs(emp_x - TARGET).max()),
        ),
        transform=right.transAxes, color=p.fg, fontsize=8,
        family="monospace", va="top",
    )


def cholesky_boundary(fig, ax, p: Palette) -> None:
    """Three tests for definiteness, one boundary."""
    a_vals = np.linspace(0.2, 2.4, 400)
    smallest, determinant, ok = [], [], []
    for a in a_vals:
        A = np.array([[1.0, 0.9], [0.9, a]])
        smallest.append(float(np.linalg.eigvalsh(A)[0]))
        determinant.append(float(np.linalg.det(A)))
        try:
            np.linalg.cholesky(A)
            ok.append(1.0)
        except np.linalg.LinAlgError:
            ok.append(0.0)

    smallest = np.array(smallest)
    determinant = np.array(determinant)
    ok = np.array(ok)

    ax.plot(a_vals, smallest, color=p.blue, linewidth=2.2, label="smallest eigenvalue")
    ax.plot(a_vals, determinant, color=p.amber, linewidth=2.2, label="determinant $a - 0.81$")
    ax.fill_between(a_vals, -1.5, 1.5, where=ok > 0.5, color=p.green, alpha=0.10,
                    label="Cholesky succeeds")
    ax.fill_between(a_vals, -1.5, 1.5, where=ok < 0.5, color=p.red, alpha=0.10,
                    label="Cholesky raises")

    boundary = 0.81
    ax.axvline(boundary, color=p.fg, linewidth=1.4, linestyle="--")
    ax.axhline(0, color=p.grid, linewidth=0.9)

    # Cholesky at the boundary itself: a = 0.81 makes the matrix positive
    # SEMIdefinite, with eigenvalues 0 and 1.81 and determinant 0, and Cholesky
    # correctly refuses it. That is the whole argument for preferring it to an
    # eigenvalue comparison, which would need a tolerance to reject the same case.
    exact = np.array([[1.0, 0.9], [0.9, 0.81]])
    try:
        np.linalg.cholesky(exact)
        verdict = "succeeds (wrongly)"
    except np.linalg.LinAlgError:
        verdict = "raises, correctly"
    ax.annotate(
        "at $a = 0.81$ exactly:"
        + "\n"
        + f"eigenvalues {np.linalg.eigvalsh(exact)[0]:.0f} and "
        + f"{np.linalg.eigvalsh(exact)[1]:.2f}, det {np.linalg.det(exact):.0f}"
        + "\n"
        + f"Cholesky {verdict}",
        xy=(boundary, 0.0),
        xytext=(1.02, -1.02),
        color=p.fg, fontsize=8.5,
        arrowprops=dict(arrowstyle="->", color=p.fg, linewidth=1.0),
    )
    ax.text(
        0.02, 0.05,
        f"swept on a grid of {len(a_vals)} values,"
        + "\n"
        + f"spacing {a_vals[1] - a_vals[0]:.2e}",
        transform=ax.transAxes, color=p.muted, fontsize=7.6, va="bottom",
    )

    ax.set_xlabel("lower-right entry $a$ of $[[1, 0.9], [0.9, a]]$")
    ax.set_ylabel("value")
    ax.set_ylim(-1.5, 1.5)
    ax.set_title("all three tests agree, and only one needs no tolerance", fontsize=10.5)
    ax.legend(loc="upper left", fontsize=8.5)


def determinant_via_cholesky(fig, ax, p: Palette) -> None:
    """Cholesky determinant against a general LU determinant."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    rng = np.random.default_rng(23)

    # Well conditioned: both routes agree to machine precision.
    sizes = np.arange(2, 41)
    gaps_good, gaps_bad = [], []
    for n in sizes:
        M = rng.normal(size=(int(n), int(n)))
        A = M @ M.T + int(n) * np.eye(int(n))          # comfortably SPD
        L = np.linalg.cholesky(A)
        d_chol = float(np.prod(np.diag(L)) ** 2)
        d_lu = float(np.linalg.det(A))
        gaps_good.append(abs(d_chol - d_lu) / abs(d_lu))

        # Ill conditioned: prescribe the spectrum.
        Q, _ = np.linalg.qr(rng.normal(size=(int(n), int(n))))
        B = Q @ np.diag(np.geomspace(1.0, 1e-12, int(n))) @ Q.T
        Lb = np.linalg.cholesky(B + 1e-14 * np.eye(int(n)))
        d_cholb = float(np.prod(np.diag(Lb)) ** 2)
        d_lub = float(np.linalg.det(B + 1e-14 * np.eye(int(n))))
        gaps_bad.append(abs(d_cholb - d_lub) / max(abs(d_lub), 1e-300))

    left.semilogy(sizes, np.maximum(gaps_good, 1e-18), color=p.green, linewidth=2.0,
                  marker="o", markersize=3.0, label="well conditioned")
    left.semilogy(sizes, np.maximum(gaps_bad, 1e-18), color=p.red, linewidth=2.0,
                  marker="s", markersize=3.0, label=r"$\kappa \approx 10^{12}$")
    left.axhline(np.finfo(float).eps, color=p.muted, linewidth=1.0, linestyle=":")
    left.set_xlabel("matrix size $n$")
    left.set_ylabel("relative gap between the two determinants")
    left.set_title("$\\prod l_{ii}^2$ against a general determinant", fontsize=10.5)
    left.legend(loc="upper left", fontsize=8.5)

    # And the size of the numbers involved: a determinant of a 40x40 SPD matrix
    # overflows long before its Cholesky diagonal does.
    ns = np.arange(2, 176)
    dets, logdets = [], []
    for n in ns:
        M = rng.normal(size=(int(n), int(n)))
        A = M @ M.T + int(n) * np.eye(int(n))
        L = np.linalg.cholesky(A)
        dets.append(float(np.linalg.det(A)))
        logdets.append(2.0 * float(np.sum(np.log(np.diag(L)))))

    dets = np.array(dets)
    logdets = np.array(logdets)
    finite = np.isfinite(dets) & (dets > 0)

    right.plot(ns, logdets, color=p.blue, linewidth=2.2, label=r"$2\sum \log l_{ii}$")
    right.plot(ns[finite], np.log(dets[finite]), color=p.amber, linewidth=1.6,
               linestyle="--", label=r"$\log(\det A)$ from a direct determinant")
    first_bad = int(ns[~finite][0]) if (~finite).any() else None
    if first_bad is not None:
        right.axvline(first_bad, color=p.red, linewidth=1.4, linestyle=":")
        right.annotate(
            f"direct determinant overflows\nto inf at $n = {first_bad}$",
            xy=(first_bad, logdets[first_bad - 2]),
            xytext=(first_bad - 108, logdets[-1] * 0.55),
            color=p.red, fontsize=8.5,
            arrowprops=dict(arrowstyle="->", color=p.red, linewidth=1.0),
        )
    right.set_xlabel("matrix size $n$")
    right.set_ylabel("log determinant")
    right.set_title("the log determinant never overflows", fontsize=10.5)
    right.legend(loc="upper left", fontsize=8.5)


FIGURES = [
    figure("cholesky-sampling", cholesky_sampling, size=(11.0, 3.8), axes=False),
    figure("cholesky-boundary", cholesky_boundary, size=(7.4, 4.8)),
    figure("determinant-via-cholesky", determinant_via_cholesky, size=(9.8, 4.2), axes=False),
]
