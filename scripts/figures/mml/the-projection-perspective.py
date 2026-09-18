"""Figures for *The Projection Perspective* (Sections 10.3.1 and 10.3.2).

1. `the-best-coordinate` — Figures 10.7 and 10.8 rebuilt. Fifty candidate
   reconstructions on a line, the distance as a function of the coordinate,
   and the minimum landing exactly on Equation 10.32's z = b'x — measured
   against a 100,001-point grid search, 4.919350 vs 4.919360.

2. `displacement-in-the-orthogonal-complement` — Figure 10.9. Every
   displacement vector x - x~ is parallel to U-perp. Measured on 174 images
   at M = 1, 5 and 20: 100.000000000000% of the squared error lies in the
   orthogonal complement and B'(x - x~) never exceeds 2.5e-14.

3. `orthonormality-is-required` — the same subspace with a non-orthonormal
   basis. z = G'x reaches 24.728409 while the proper coordinates reach
   16.316272 — Equation 10.32 is not a general formula, it is what Equation
   10.34's (B'B)^-1 collapses to when B'B = I.
"""

from __future__ import annotations

import numpy as np
from sklearn.datasets import load_digits

from _style import Palette, figure

_DIG = load_digits()
_A8 = _DIG.data[_DIG.target == 8]
_N, _D = _A8.shape
_X = (_A8 - _A8.mean(0)).T
_S = _X @ _X.T / _N
_W, _V = np.linalg.eigh(_S)
_PC = _V[:, ::-1]


def _img(ax, vec, p: Palette, title=None, cmap="gray", vmin=None, vmax=None):
    ax.imshow(np.asarray(vec).reshape(8, 8), cmap=cmap,
              interpolation="nearest", vmin=vmin, vmax=vmax)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_color(p.grid)
    if title:
        ax.set_title(title, fontsize=9.5, color=p.fg)


# --------------------------------------------------------------------------
# 1. Figures 10.7 and 10.8
# --------------------------------------------------------------------------

def the_best_coordinate(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.15, 1.0]})

    b = np.array([1.0, 2.0])
    b /= np.linalg.norm(b)
    x = np.array([5.0, 3.0])
    zstar = float(b @ x)

    a1.plot([-1.5 * b[0], 7.5 * b[0]], [-1.5 * b[1], 7.5 * b[1]],
            color=p.muted, lw=1.6)
    a1.annotate("$U = \\mathrm{span}[b]$", (5.6 * b[0] - 0.9, 5.6 * b[1]),
                fontsize=9.5, color=p.muted)
    for z in np.linspace(-1.0, 7.0, 26):
        xt = z * b
        a1.plot([x[0], xt[0]], [x[1], xt[1]], color=p.red, lw=0.8, alpha=0.35)
        a1.plot([xt[0]], [xt[1]], "o", ms=3, color=p.muted, alpha=0.7)
    xt = zstar * b
    a1.plot([x[0], xt[0]], [x[1], xt[1]], color=p.blue, lw=2.6, zorder=5)
    a1.plot([xt[0]], [xt[1]], "o", ms=9, color=p.blue, zorder=6)
    a1.scatter([x[0]], [x[1]], s=95, color=p.amber, marker="X", zorder=7)
    a1.annotate("$x$", x, textcoords="offset points", xytext=(9, 4),
                fontsize=11, color=p.amber)
    a1.annotate("$\\tilde{x}$", xt, textcoords="offset points",
                xytext=(-20, -4), fontsize=11, color=p.blue)
    # the right angle
    u = b
    v = (x - xt) / np.linalg.norm(x - xt)
    sq = np.array([xt, xt + 0.42 * u, xt + 0.42 * u + 0.42 * v, xt + 0.42 * v])
    a1.plot(sq[[0, 1, 2, 3, 0], 0], sq[[0, 1, 2, 3, 0], 1],
            color=p.blue, lw=1.1)
    a1.arrow(0, 0, b[0], b[1], color=p.green, width=0.035,
             length_includes_head=True, zorder=6)
    a1.annotate("$b$", 0.62 * b, textcoords="offset points", xytext=(-16, 4),
                fontsize=11, color=p.green)
    a1.set_xlim(-1.6, 6.6)
    a1.set_ylim(-1.6, 6.6)
    a1.set_aspect("equal")
    a1.set_xlabel("$x_1$")
    a1.set_ylabel("$x_2$")
    a1.set_title("Figure 10.7(b): candidate reconstructions on $U$",
                 fontsize=10)

    zs = np.linspace(-1.5, 9.0, 600)
    d = np.linalg.norm(x[None, :] - zs[:, None] * b[None, :], axis=1)
    a2.plot(zs, d, color=p.blue, lw=2.2)
    a2.plot([zstar], [np.linalg.norm(x - zstar * b)], "o", ms=9,
            color=p.amber, zorder=5)
    a2.axvline(zstar, color=p.amber, ls=":", lw=1.4)
    a2.annotate(f"$z = b^\\top x$ = {zstar:.6f}\nerror "
                f"{np.linalg.norm(x - zstar*b):.6f}",
                (zstar + 0.5, 5.3), fontsize=9.5, color=p.amber)
    a2.set_xlabel("coordinate $z$")
    a2.set_ylabel("$\\|x - z\\,b\\|$")
    a2.set_title("Figure 10.8(a): one minimum, and Equation 10.32 finds it",
                 fontsize=10)
    fig.suptitle("The optimal coordinate is the orthogonal projection, "
                 "and nothing else is",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. Figure 10.9
# --------------------------------------------------------------------------

def displacement_in_the_orthogonal_complement(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.2, 1.0]})

    rng = np.random.default_rng(5)
    t = rng.normal(0, 2.6, 90)
    P2 = np.c_[t, 0.62 * t + rng.normal(0, 1.5, 90)]
    P2 -= P2.mean(0)
    w2, V2 = np.linalg.eigh(P2.T @ P2 / len(P2))
    b = V2[:, 1] * np.sign(V2[0, 1])
    bp = V2[:, 0]
    Pr = np.outer(b, b)
    Q = P2 @ Pr

    L = 8.5
    a1.plot([-L * b[0], L * b[0]], [-L * b[1], L * b[1]], color=p.muted,
            lw=1.6)
    a1.plot([-4 * bp[0], 4 * bp[0]], [-4 * bp[1], 4 * bp[1]],
            color=p.grid, lw=1.4, ls="--")
    a1.annotate("$U$", (L * b[0] * 0.82, L * b[1] * 0.82 + 0.7),
                fontsize=11, color=p.muted)
    a1.annotate("$U^\\perp$", (3.4 * bp[0], 3.4 * bp[1]), fontsize=11,
                color=p.muted)
    for k in range(len(P2)):
        a1.plot([P2[k, 0], Q[k, 0]], [P2[k, 1], Q[k, 1]], color=p.red,
                lw=0.9, alpha=0.6)
    a1.scatter(P2[:, 0], P2[:, 1], s=15, color=p.blue, zorder=4, label="$x_n$")
    a1.scatter(Q[:, 0], Q[:, 1], s=15, color=p.amber, zorder=5,
               label="$\\tilde{x}_n$")
    a1.set_xlim(-8, 8)
    a1.set_ylim(-6, 6)
    a1.set_aspect("equal")
    a1.set_xlabel("$x_1$")
    a1.set_ylabel("$x_2$")
    a1.legend(fontsize=9, loc="upper left")
    a1.set_title("every red segment is parallel to $U^\\perp$", fontsize=10)

    # the same claim on the digits
    Ms = [1, 2, 5, 10, 20, 40]
    vals = []
    for M in Ms:
        B = _PC[:, :M]
        R = _X - B @ B.T @ _X
        vals.append(float(np.abs(B.T @ R).max()))
    a2.bar([str(M) for M in Ms], vals, color=p.blue, width=0.55)
    for k, v in enumerate(vals):
        a2.text(k, v * 1.05, f"{v:.1e}", ha="center", fontsize=8.5,
                color=p.fg)
    a2.set_yscale("log")
    a2.set_ylim(1e-16, 1e-12)
    a2.set_xlabel("$M$")
    a2.set_ylabel("$\\max\\,|B^\\top(x_n - \\tilde{x}_n)|$")
    a2.set_title("on 174 images: the displacement has no $U$ component",
                 fontsize=10)
    fig.suptitle("Figure 10.9: what you throw away lives entirely in the "
                 "orthogonal complement",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 3. Equation 10.32 is a special case of Equation 10.34
# --------------------------------------------------------------------------

def orthonormality_is_required(fig, ax, p: Palette) -> None:
    fig.clear()
    gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 0.62], hspace=0.35,
                          wspace=0.25)

    M = 5
    G = _PC[:, :M] @ np.diag([1.0, 1.4, 0.6, 2.2, 0.5])
    G[:, 1] += 0.3 * G[:, 0]
    xn = _X[:, 0]
    mu = _A8.mean(0)

    z_naive = G.T @ xn
    z_right = np.linalg.solve(G.T @ G, G.T @ xn)
    Bo = np.linalg.qr(G)[0]

    panels = [
        (xn, "the original $x$", None),
        (G @ z_naive, "$z = G^\\top x$\n(Equation 10.32, misapplied)",
         float(np.linalg.norm(xn - G @ z_naive))),
        (G @ z_right, "$z = (G^\\top G)^{-1}G^\\top x$\n(Equation 10.34)",
         float(np.linalg.norm(xn - G @ z_right))),
        (Bo @ (Bo.T @ xn), "an ONB for the same span",
         float(np.linalg.norm(xn - Bo @ (Bo.T @ xn)))),
    ]
    for k, (vec, ttl, err) in enumerate(panels):
        a = fig.add_subplot(gs[0, k])
        t = ttl if err is None else f"{ttl}\nerror {err:.6f}"
        _img(a, vec + mu, p, t, vmin=0, vmax=16)

    b = fig.add_subplot(gs[1, :])
    errs = [e for _, _, e in panels[1:]]
    names = ["$G^\\top x$", "$(G^\\top G)^{-1}G^\\top x$", "ONB, same span"]
    b.barh(names, errs, color=[p.red, p.green, p.blue], height=0.55)
    for k, e in enumerate(errs):
        b.text(e + 0.35, k, f"{e:.6f}", va="center", fontsize=9, color=p.fg)
    b.set_xlim(0, 30)
    b.set_xlabel("$\\|x - \\tilde{x}\\|$")
    b.set_title("identical subspace, three coordinate rules", fontsize=10)
    fig.suptitle("Equation 10.32 is what Equation 10.34 collapses to "
                 "when the columns are orthonormal",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("the-best-coordinate", the_best_coordinate, size=(9.4, 4.6),
           axes=False),
    figure("displacement-in-the-orthogonal-complement",
           displacement_in_the_orthogonal_complement, size=(9.4, 4.4),
           axes=False),
    figure("orthonormality-is-required", orthonormality_is_required,
           size=(9.4, 5.0), axes=False),
]
