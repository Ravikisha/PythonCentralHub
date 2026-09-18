"""Figures for *Problem Setting* (Section 10.1).

1. `code-and-reconstruction` — Figure 10.2 made concrete on a real image. One
   digit "8" (D = 64) encoded to z = B'x and decoded to x~ = Bz at M = 1, 2, 5,
   10, 20. The reconstruction always has 64 numbers in it; its rank never
   exceeds M.

2. `centring-is-not-optional` — Equation 10.1 is the covariance only when the
   mean is 0. Measured on 174 images of the digit "8": skipping the centring
   moves the leading direction 87.9996 degrees, onto the mean image itself
   (0.2851 degrees from it), and inflates the trace by 5.4245x.

3. `one-budget-two-bases` — Example 10.1's vector [5, 3] projected onto e2, e1
   and the best 1-D subspace. Same M = 1 budget, errors 5.000000, 3.000000 and
   0.000000. Choosing b is the whole of Sections 10.2 and 10.3.
"""

from __future__ import annotations

import numpy as np
from sklearn.datasets import load_digits

from _style import Palette, figure

# --------------------------------------------------------------------------
# the chapter's running dataset: the digit "8". The book uses MNIST at 28x28;
# this is the 8x8 UCI corpus that ships inside scikit-learn, so the numbers
# reproduce without a download.
# --------------------------------------------------------------------------

_DIG = load_digits()
_A8 = _DIG.data[_DIG.target == 8]          # (174, 64), rows are images
_MU = _A8.mean(0)
_XC = (_A8 - _MU).T                        # D x N, the book's column layout
_N = _XC.shape[1]
_S = _XC @ _XC.T / _N
_W, _V = np.linalg.eigh(_S)
_PC = _V[:, ::-1]                          # eigenvectors, largest first


def _img(ax, vec, p: Palette, title=None, cmap="gray", vmin=None, vmax=None):
    ax.imshow(np.asarray(vec).reshape(8, 8), cmap=cmap, interpolation="nearest",
              vmin=vmin, vmax=vmax)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_color(p.grid)
    if title:
        ax.set_title(title, fontsize=9.5, color=p.fg)


# --------------------------------------------------------------------------
# 1. Figure 10.2 on a real image
# --------------------------------------------------------------------------

def code_and_reconstruction(fig, ax, p: Palette) -> None:
    fig.clear()
    Ms = [1, 2, 5, 10, 20]
    gs = fig.add_gridspec(2, len(Ms) + 1, height_ratios=[1.0, 1.0],
                          hspace=0.18, wspace=0.2)

    x = _XC[:, 3]                       # one centred image
    a = fig.add_subplot(gs[0, 0])
    _img(a, x + _MU, p, "x   (D = 64)", vmin=0, vmax=16)
    a = fig.add_subplot(gs[1, 0])
    a.axis("off")
    a.text(0.5, 0.55, "residual\n$x - \\tilde{x}$", ha="center", va="center",
           fontsize=9.5, color=p.muted, transform=a.transAxes)

    for k, M in enumerate(Ms):
        B = _PC[:, :M]
        z = B.T @ x
        r = x - B @ z
        err = float(np.linalg.norm(r))
        pct = 100 * (_N * M + 64 * M) / (_N * 64)
        a = fig.add_subplot(gs[0, k + 1])
        _img(a, B @ z + _MU, p, f"M = {M}\nstores {pct:.1f}%",
             vmin=0, vmax=16)
        a = fig.add_subplot(gs[1, k + 1])
        _img(a, r, p, f"error {err:.2f}", cmap="RdBu_r", vmin=-9, vmax=9)

    fig.suptitle("Figure 10.2 on one image: x  ->  z = B'x  ->  x~ = Bz",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. what the zero-mean assumption is doing
# --------------------------------------------------------------------------

def centring_is_not_optional(fig, ax, p: Palette) -> None:
    fig.clear()
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1.0], hspace=0.4,
                          wspace=0.32)

    # -- a 2-D cloud that makes the geometry visible -----------------------
    rng = np.random.default_rng(0)
    t = rng.normal(0, 1.0, 160)
    pts = np.c_[6.0 + t, 5.0 - 0.9 * t + rng.normal(0, 0.28, 160)]
    m = pts.mean(0)

    def lead(mat):
        w, v = np.linalg.eigh(mat.T @ mat / len(mat))
        return v[:, -1]

    d_raw, d_cen = lead(pts), lead(pts - m)
    d_raw = d_raw * np.sign(d_raw @ m)          # point it at the cloud
    d_cen = d_cen * np.sign(d_cen[0])

    a = fig.add_subplot(gs[0, :2])
    a.scatter(pts[:, 0], pts[:, 1], s=12, color=p.muted, alpha=0.65,
              label="data")
    a.scatter([m[0]], [m[1]], s=70, color=p.red, zorder=5, marker="X",
              label="mean")
    L = 10.0
    a.plot([0, L * d_raw[0]], [0, L * d_raw[1]], color=p.amber, lw=2.4,
           label="leading direction of Eq 10.1 as written")
    a.plot([m[0] - 2.6 * d_cen[0], m[0] + 2.6 * d_cen[0]],
           [m[1] - 2.6 * d_cen[1], m[1] + 2.6 * d_cen[1]],
           color=p.blue, lw=2.4, label="leading direction after centring")
    a.scatter([0], [0], s=40, color=p.fg, zorder=5)
    a.annotate("origin", (0, 0), textcoords="offset points", xytext=(9, -4),
               fontsize=9, color=p.fg)
    a.set_xlim(-0.8, 9.8)
    a.set_ylim(-3.6, 8.6)
    a.set_aspect("equal")
    a.set_xlabel("$x_1$")
    a.set_ylabel("$x_2$")
    a.legend(loc="lower right", fontsize=8.2)
    a.set_title("uncentred, the leading direction points at the mean",
                fontsize=10)

    # -- the same thing, measured on the digits ---------------------------
    b = fig.add_subplot(gs[0, 2])
    S_raw = _A8.T @ _A8 / _N
    w_r, v_r = np.linalg.eigh(S_raw)
    names = ["centred\n$b_1$ vs mean", "uncentred\n$b_1$ vs mean",
             "centred vs\nuncentred $b_1$"]
    mh = _MU / np.linalg.norm(_MU)
    angs = [np.degrees(np.arccos(abs(_PC[:, 0] @ mh))),
            np.degrees(np.arccos(abs(v_r[:, -1] @ mh))),
            np.degrees(np.arccos(abs(_PC[:, 0] @ v_r[:, -1])))]
    b.barh(names, angs, color=[p.blue, p.amber, p.green], height=0.55)
    for k, v in enumerate(angs):
        b.text(v + 2.5, k, f"{v:.2f}", va="center", fontsize=9, color=p.fg)
    b.set_xlim(0, 115)
    b.set_xlabel("angle, degrees")
    b.set_title("174 images of '8'", fontsize=10)

    # -- the three images -------------------------------------------------
    for k, (vec, ttl) in enumerate([
            (_MU, "the mean image"),
            (v_r[:, -1], "uncentred $b_1$"),
            (_PC[:, 0], "centred $b_1$")]):
        c = fig.add_subplot(gs[1, k])
        _img(c, vec, p, ttl, cmap="gray" if k == 0 else "RdBu_r")
    fig.suptitle("Equation 10.1 is a covariance only when the mean is 0",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 3. Example 10.1, and why the basis is the whole problem
# --------------------------------------------------------------------------

def one_budget_two_bases(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.25, 1.0]})

    x = np.array([5.0, 3.0])
    bases = [("$b = e_2$", np.array([0.0, 1.0]), p.amber),
             ("$b = e_1$", np.array([1.0, 0.0]), p.green),
             ("", x / np.linalg.norm(x), p.blue)]

    a1.scatter([x[0]], [x[1]], s=90, color=p.red, marker="X", zorder=6)
    a1.annotate("$x = [5, 3]^\\top$", x, textcoords="offset points",
                xytext=(10, 6), fontsize=10, color=p.fg)
    for name, b, col in bases:
        xt = b * float(b @ x)
        a1.plot([-1.2 * b[0], 6.2 * b[0]], [-1.2 * b[1], 6.2 * b[1]],
                color=col, lw=1.8, alpha=0.85)
        a1.plot([x[0], xt[0]], [x[1], xt[1]], color=col, lw=1.6, ls=":")
        a1.scatter([xt[0]], [xt[1]], s=55, color=col, zorder=5)
        a1.annotate(name, xt, textcoords="offset points", xytext=(8, -14),
                    fontsize=9.5, color=col)
    a1.annotate("$b = x/\\|x\\|$", (3.2, 1.55), fontsize=9.5, color=p.blue)
    a1.scatter([0], [0], s=35, color=p.fg, zorder=5)
    a1.set_xlim(-1.4, 7.2)
    a1.set_ylim(-1.4, 6.2)
    a1.set_aspect("equal")
    a1.set_xlabel("$x_1$")
    a1.set_ylabel("$x_2$")
    a1.set_title("Example 10.1: one vector, three 1-D subspaces", fontsize=10)

    errs = [float(np.linalg.norm(x - b * (b @ x))) for _, b, _ in bases]
    a2.bar(["$e_2$", "$e_1$", "the best $b$"], errs,
           color=[c for _, _, c in bases], width=0.55)
    for k, e in enumerate(errs):
        a2.text(k, e + 0.12, f"{e:.6f}", ha="center", fontsize=9, color=p.fg)
    a2.set_ylim(0, 6.0)
    a2.set_ylabel("reconstruction error")
    a2.set_title("same M = 1 budget, three answers", fontsize=10)
    fig.suptitle("The code length is given. The basis is not.",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("code-and-reconstruction", code_and_reconstruction,
           size=(9.2, 5.4), axes=False),
    figure("centring-is-not-optional", centring_is_not_optional,
           size=(9.6, 6.4), axes=False),
    figure("one-budget-two-bases", one_budget_two_bases,
           size=(9.0, 4.2), axes=False),
]
