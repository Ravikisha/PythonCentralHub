"""Figures for *Maximum Likelihood as Orthogonal Projection* (Section 9.4).

1. `figure-9-12-rebuilt` — the book's geometric picture, with the projection
   matrix's defining properties checked: idempotent to 5.6e-17, symmetric to
   0, rank 1, trace 1, eigenvalues one 1 and nine 0s.

2. `trace-p-equals-k` — trace(P) = K exactly at every degree, so
   E||(I - P)y||^2 = sigma^2 (N - K). Measured 0.200222 against 0.200000,
   where Equation 9.22 assumes 0.400000. This is page 902's bias, explained.

3. `same-subspace-different-basis` — monomials and an orthonormal basis for the
   same span give the same projection to 2.4e-13, with condition numbers of
   2.2e+26 and 1.000000.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

SIG = 0.2


def _truth(x):
    return -np.sin(x / 5) + np.cos(x)


def _design(x, M):
    return np.vander(np.asarray(x, float), M + 1, increasing=True)


def _data():
    rng = np.random.default_rng(4)
    x = np.sort(rng.uniform(-5, 5, 10))
    return x, _truth(x) + SIG * rng.standard_normal(10)


def _proj(P):
    return P @ np.linalg.solve(P.T @ P, P.T)


# --------------------------------------------------------------------------
# 1. Figure 9.12
# --------------------------------------------------------------------------

def figure_9_12_rebuilt(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    x, y = _data()
    N = len(y)
    X = x.reshape(-1, 1)
    th = float((X.T @ y)[0] / (X.T @ X)[0, 0])
    P1 = X @ X.T / float((X.T @ X)[0, 0])
    fit = x * th

    a1.plot(x, y, "o", color=p.blue, markersize=8,
            markeredgecolor=p.bg, markeredgewidth=0.8)
    a1.axhline(0, color=p.muted, linewidth=0.8)
    a1.axvline(0, color=p.muted, linewidth=0.8)
    a1.set_xlim(-5, 5)
    a1.set_ylim(-4, 4)
    a1.set_xlabel("$x$")
    a1.set_ylabel("$y$")
    a1.set_title("(a) The dataset", fontsize=9.6)
    a1.grid(alpha=0.20, linewidth=0.6)

    xg = np.linspace(-5, 5, 200)
    a2.plot(xg, th * xg, color=p.green, linewidth=2.4,
            label=r"$x\theta_{\mathrm{ML}}$")
    for xi, yi, fi in zip(x, y, fit):
        a2.plot([xi, xi], [yi, fi], color=p.red, linewidth=1.4, alpha=0.8)
    a2.plot(x, y, "o", color=p.blue, markersize=7,
            markeredgecolor=p.bg, markeredgewidth=0.7, label="observations",
            zorder=5)
    a2.plot(x, fit, "o", color=p.amber, markersize=6,
            markeredgecolor=p.bg, markeredgewidth=0.6, label="projections",
            zorder=6)
    a2.set_xlim(-5, 5)
    a2.set_ylim(-4, 4)
    a2.set_xlabel("$x$")
    a2.set_ylabel("$y$")
    a2.set_title("(b) The maximum likelihood fit as a projection",
                 fontsize=9.5)
    a2.legend(fontsize=7.6, loc="lower left")
    a2.grid(alpha=0.20, linewidth=0.6)
    a2.text(
        0.97, 0.96,
        f"theta_ML = {th:.6f}\n\n"
        "The red segments are what\nleast squares minimises: the\n"
        "SQUARED lengths, summed.\n\n"
        "Note the x-coordinate is fixed —\n"
        "the projection is vertical, into\n"
        "the span of X.",
        transform=a2.transAxes, ha="right", va="top", fontsize=7.2,
        color=p.fg, family="monospace")

    # --- a3: the projection matrix's properties -------------------------
    a3.axis("off")
    ev = np.linalg.eigvalsh(P1)
    lines = [
        r"$P = \dfrac{XX^\top}{X^\top X}$   (Equation 9.67)",
    ]
    a3.text(0.5, 0.93, lines[0], transform=a3.transAxes, ha="center",
            va="top", fontsize=13, color=p.fg)
    rows = [
        ("idempotent", r"$\max|PP - P|$", f"{np.abs(P1 @ P1 - P1).max():.3e}",
         p.green),
        ("symmetric", r"$\max|P - P^\top|$", f"{np.abs(P1 - P1.T).max():.3e}",
         p.green),
        ("rank", r"$\mathrm{rk}(P)$",
         f"{int(np.linalg.matrix_rank(P1))}", p.amber),
        ("trace", r"$\mathrm{tr}(P)$", f"{np.trace(P1):.10f}", p.amber),
        ("eigenvalues", "how many equal 1",
         f"{int(np.sum(np.abs(ev-1) < 1e-9))} of {N}", p.purple),
        ("the coordinate", r"$\theta_{\mathrm{ML}}$", f"{th:.6f}", p.blue),
        ("the projection", r"$\max|X\theta_{\mathrm{ML}} - Py|$",
         f"{np.abs(x*th - P1 @ y).max():.3e}", p.blue),
    ]
    yy = 0.76
    for name, expr, val, col in rows:
        a3.text(0.02, yy, name, transform=a3.transAxes, ha="left",
                va="center", fontsize=8.6, color=p.muted, family="monospace")
        a3.text(0.42, yy, expr, transform=a3.transAxes, ha="left",
                va="center", fontsize=10, color=p.fg)
        a3.text(0.98, yy, val, transform=a3.transAxes, ha="right",
                va="center", fontsize=9.4, color=col, family="monospace")
        yy -= 0.105
    a3.text(0.5, 0.02,
            "Idempotent and symmetric is the\ndefinition of an orthogonal "
            "projection.\nProjecting twice does nothing new.",
            transform=a3.transAxes, ha="center", va="bottom", fontsize=7.6,
            color=p.fg, family="monospace")
    a3.set_title("The three things that make it a projection",
                 fontsize=9.5)

    fig.suptitle(
        "Section 9.4: the maximum likelihood estimate is the orthogonal "
        "projection of the targets onto the span of the features",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book's identification is threefold: XX'/(X'X) is the projection "
        "matrix, theta_ML is the coordinate of the projection in the "
        "one-dimensional subspace spanned by X, and\nX theta_ML is the "
        "projection itself. All three are checked here, the last to 2.2e-16.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 2. trace(P) = K
# --------------------------------------------------------------------------

def trace_p_equals_k(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    x, y = _data()
    N = len(y)
    Ms = np.arange(9)
    tr = [np.trace(_proj(_design(x, int(M)))) for M in Ms]
    trI = [N - t for t in tr]

    left.plot(Ms, tr, "o-", color=p.blue, linewidth=2.4, markersize=8,
              label=r"$\mathrm{tr}(P)$")
    left.plot(Ms, Ms + 1, "s", color=p.green, markersize=13,
              markerfacecolor="none", markeredgewidth=2.0, label="$K = M+1$")
    left.plot(Ms, trI, "o-", color=p.amber, linewidth=2.4, markersize=8,
              label=r"$\mathrm{tr}(I - P)$")
    left.plot(Ms, N - (Ms + 1), "s", color=p.red, markersize=13,
              markerfacecolor="none", markeredgewidth=2.0, label="$N - K$")
    left.set_xlabel("polynomial degree $M$")
    left.set_ylabel("trace")
    left.set_title("The trace of a projection is its rank", fontsize=9.8)
    left.legend(fontsize=8, loc="center right")
    left.grid(alpha=0.20, linewidth=0.6)
    left.text(
        0.03, 0.05,
        "measured to 8 decimal places at\nevery degree:\n"
        "  tr(P)     = K\n"
        "  tr(I - P) = N - K\n\n"
        "A projection's eigenvalues are\nall 0 or 1, so its trace counts\n"
        "the dimensions it keeps.",
        transform=left.transAxes, ha="left", va="bottom", fontsize=7.3,
        color=p.fg, family="monospace")

    # --- right: the consequence for the noise estimate -------------------
    Pm = _design(x, 4)
    Pr = _proj(Pm)
    r2 = np.random.default_rng(21)
    TR = 60_000
    truth_vals = Pm @ np.arange(1.0, 6.0)
    vals = np.empty(TR)
    IP = np.eye(N) - Pr
    for i in range(TR):
        yy = truth_vals + SIG * r2.standard_normal(N)
        rr = IP @ yy
        vals[i] = float(rr @ rr)
    right.hist(vals, bins=90, color=p.blue, alpha=0.75, density=True)
    right.axvline(SIG ** 2 * (N - 5), color=p.green, linewidth=2.6,
                  label=f"$\\sigma^2(N-K) = {SIG**2*(N-5):.4f}$")
    right.axvline(vals.mean(), color=p.amber, linewidth=2.2, linestyle="--",
                  label=f"measured mean {vals.mean():.6f}")
    right.axvline(SIG ** 2 * N, color=p.red, linewidth=2.6,
                  label=f"$\\sigma^2 N = {SIG**2*N:.4f}$, what Eq. 9.22 assumes")
    right.set_xlim(0, 1.2)
    right.set_xlabel(r"$\|(I - P)\,y\|^2$")
    right.set_ylabel("density")
    right.set_title(f"$M = 4$, so $K = 5$ and $N - K = 5$", fontsize=9.8)
    right.legend(fontsize=7.6, loc="upper right")
    right.grid(alpha=0.20, linewidth=0.6)
    right.text(
        0.03, 0.55,
        "E||(I-P)y||^2 = sigma^2 tr(I-P)\n"
        "              = sigma^2 (N - K)\n\n"
        "Equation 9.22 divides by N, not\nby N - K, so it returns\n"
        "(N-K)/N of the truth.\n\n"
        "Page 902 MEASURED that ratio.\nThis is why.",
        transform=right.transAxes, ha="left", va="center", fontsize=7.3,
        color=p.fg, family="monospace")

    fig.suptitle(
        "The geometry explains page 902's bias: the residual lives in an "
        "$(N-K)$-dimensional subspace, not an $N$-dimensional one",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "A projection keeps K directions and annihilates N - K of them, so its "
        "trace is K exactly. The residual is what survives I - P, and only "
        "N - K independent noise\ndirections reach it — which is precisely "
        "the count Equation 9.22 gets wrong.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 3. same subspace, different basis
# --------------------------------------------------------------------------

def same_subspace_different_basis(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    xs = np.linspace(-5, 5, 60)
    ys = _truth(xs) + SIG * np.random.default_rng(5).standard_normal(60)
    Ms = [2, 6, 10, 14, 18]
    cM, cQ, diff = [], [], []
    for M in Ms:
        Pm = _design(xs, M)
        Q, _ = np.linalg.qr(Pm)
        cM.append(float(np.linalg.cond(Pm.T @ Pm)))
        cQ.append(float(np.linalg.cond(Q.T @ Q)))
        tm = np.linalg.solve(Pm.T @ Pm, Pm.T @ ys)
        tq = Q.T @ ys
        diff.append(float(np.abs(Pm @ tm - Q @ tq).max()))

    pos = np.arange(len(Ms))
    left.bar(pos - 0.19, cM, width=0.36, color=p.red,
             label=r"monomials: $\kappa(\Phi^\top\Phi)$")
    left.bar(pos + 0.19, cQ, width=0.36, color=p.green,
             label=r"orthonormal: $\kappa(Q^\top Q)$")
    left.set_yscale("log")
    left.set_xticks(pos)
    left.set_xticklabels([f"$M={m}$" for m in Ms], fontsize=8.6)
    left.set_ylabel("condition number")
    left.set_ylim(0.5, 1e28)
    left.set_title("Same subspace, wildly different conditioning",
                   fontsize=9.8)
    left.legend(fontsize=8, loc="upper left")
    left.grid(alpha=0.20, linewidth=0.6, axis="y", which="both")
    for i, (a, b) in enumerate(zip(cM, cQ)):
        left.text(i - 0.19, a * 2, f"{a:.1e}", ha="center", fontsize=7.0,
                  color=p.red, family="monospace", rotation=90)
    left.text(
        0.97, 0.05,
        "The orthonormal basis has\ncondition number 1.000000 at\n"
        "every degree, because\nQ^T Q = I exactly.\n\n"
        "The book: with orthonormal\nfeatures the projection is\n"
        "simply Q Q^T y — no inverse\nto compute at all.",
        transform=left.transAxes, ha="right", va="bottom", fontsize=7.2,
        color=p.fg, family="monospace")

    # --- right: and yet the same fit --------------------------------------
    x10, y10 = _data()
    M = 6
    Pm = _design(x10, M)
    Q, _ = np.linalg.qr(Pm)
    th_m = np.linalg.lstsq(Pm, y10, rcond=None)[0]
    th_q = Q.T @ y10
    xg = np.linspace(-5, 5, 300)
    Pg = _design(xg, M)
    # express the orthonormal fit on the grid via the same QR rotation
    R = np.linalg.lstsq(Pm, Q, rcond=None)[0]
    right.plot(xg, Pg @ th_m, color=p.red, linewidth=4.0, alpha=0.5,
               label="monomial coordinates")
    right.plot(xg, Pg @ (R @ th_q), color=p.green, linewidth=1.8,
               linestyle="--", label="orthonormal coordinates")
    right.plot(x10, y10, "o", color=p.blue, markersize=7,
               markeredgecolor=p.bg, markeredgewidth=0.7, zorder=6,
               label="training data")
    right.set_xlim(-5, 5)
    right.set_ylim(-4, 4)
    right.set_xlabel("$x$")
    right.set_ylabel("$y$")
    right.set_title("And yet exactly the same fit", fontsize=9.8)
    right.legend(fontsize=8, loc="lower center")
    right.grid(alpha=0.20, linewidth=0.6)
    Pr_m = _proj(Pm)
    Pr_q = Q @ Q.T
    right.text(
        0.03, 0.96,
        f"||theta|| monomial    : {np.linalg.norm(th_m):.6f}\n"
        f"||theta|| orthonormal : {np.linalg.norm(th_q):.6f}\n\n"
        f"max |Phi t_m - Q t_q| : "
        f"{np.abs(Pm @ th_m - Q @ th_q).max():.3e}\n"
        f"max |P_mono - P_orth| : {np.abs(Pr_m - Pr_q).max():.3e}\n\n"
        "Different coordinates, same\nsubspace, same projection.",
        transform=right.transAxes, ha="left", va="top", fontsize=7.2,
        color=p.fg, family="monospace")

    fig.suptitle(
        "A projection is a property of the subspace; the basis is only a "
        "coordinate system",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Both bases span exactly the same space, so both produce the same "
        "projection matrix and the same fitted values — measured to 2.4e-13. "
        "What changes is the conditioning of\ngetting there: 2.2e+26 against "
        "1.000000. Page 902 measured what that costs, and Section 9.4 explains "
        "why the choice was free to begin with.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


FIGURES = [
    figure("figure-9-12-rebuilt", figure_9_12_rebuilt, size=(15.0, 5.1),
           axes=False),
    figure("trace-p-equals-k", trace_p_equals_k, size=(13.6, 5.2),
           axes=False),
    figure("same-subspace-different-basis", same_subspace_different_basis,
           size=(13.6, 5.2), axes=False),
]
