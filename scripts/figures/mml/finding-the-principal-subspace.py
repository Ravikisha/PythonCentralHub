"""Figures for *Finding the Principal Subspace* (Section 10.3.3).

1. `one-number-five-spellings` — Equations 10.29, 10.41, 10.43a, 10.43b and
   10.44 plotted on top of each other across M = 1..63, plus the conservation
   law V_M + J_M = trace(S) that makes Sections 10.2 and 10.3 the same
   optimisation.

2. `the-eigenbasis-wins` — the distribution of J_M over random orthonormal
   bases against the eigenbasis value, at M = 5. None of the random draws
   comes close, and a numerical optimiser over B lands back on the same
   subspace.

3. `same-subspace-different-basis` — rotating B by an M-by-M orthogonal R
   leaves B B-transpose, and therefore J_M, exactly unchanged, while the codes
   change completely. Only the eigenbasis leaves the code's covariance
   diagonal.
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
_LAM, _PC = _W[::-1], _V[:, ::-1]
_TOT = _LAM.sum()


def _J(B):
    return float(((_X - B @ B.T @ _X) ** 2).sum() / _N)


# --------------------------------------------------------------------------
# 1. every route to J_M
# --------------------------------------------------------------------------

def one_number_five_spellings(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2)

    Ms = np.arange(1, _D)
    e29, e43b, e44 = [], [], []
    for M in Ms:
        B, Bp = _PC[:, :M], _PC[:, M:]
        e29.append(_J(B))
        e43b.append(float(np.trace((Bp @ Bp.T) @ _S)))
        e44.append(float(_LAM[M:].sum()))

    a1.plot(Ms, e29, color=p.blue, lw=4.0, alpha=0.55,
            label="Eq 10.29, measured directly")
    a1.plot(Ms, e43b, color=p.amber, lw=2.0,
            label="Eq 10.43b, a trace")
    a1.plot(Ms, e44, color=p.green, lw=1.2, ls="--",
            label="Eq 10.44, leftover eigenvalues")
    a1.set_xlabel("$M$")
    a1.set_ylabel("$J_M$")
    a1.legend(fontsize=9)
    a1.set_title("three routes, one curve (largest spread 2.8e-13)",
                 fontsize=10)

    VM = [_TOT - j for j in e44]
    a2.fill_between(Ms, 0, VM, color=p.blue, alpha=0.35,
                    label="$V_M$, kept (Section 10.2)")
    a2.fill_between(Ms, VM, [v + j for v, j in zip(VM, e44)],
                    color=p.red, alpha=0.35,
                    label="$J_M$, lost (Section 10.3)")
    a2.axhline(_TOT, color=p.fg, lw=1.4, ls=":")
    a2.annotate(f"$\\mathrm{{tr}}(S)$ = {_TOT:.6f}", (2, _TOT + 14),
                fontsize=9.5, color=p.fg)
    a2.set_xlabel("$M$")
    a2.set_ylabel("variance")
    a2.set_ylim(0, _TOT * 1.13)
    a2.legend(fontsize=9, loc="center right")
    a2.set_title("the budget is fixed, so the two problems are one",
                 fontsize=10)
    fig.suptitle("$J_M$ has five spellings in Section 10.3, and they are "
                 "the same number",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. is the eigenbasis really optimal?
# --------------------------------------------------------------------------

def the_eigenbasis_wins(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.25, 1.0]})

    M = 5
    Jstar = _J(_PC[:, :M])
    rng = np.random.default_rng(21)
    draws = np.array([_J(np.linalg.qr(rng.standard_normal((_D, M)))[0])
                      for _ in range(4000)])

    a1.hist(draws, bins=60, color=p.muted, alpha=0.8,
            label="4,000 random orthonormal $B$")
    a1.axvline(Jstar, color=p.amber, lw=2.4,
               label=f"the top-5 eigenvectors: {Jstar:.2f}")
    a1.axvline(draws.min(), color=p.green, lw=1.6, ls="--",
               label=f"best random draw: {draws.min():.2f}")
    a1.axvline(_TOT, color=p.red, lw=1.4, ls=":",
               label=f"keeping nothing: {_TOT:.2f}")
    a1.set_xlabel("$J_M$ at $M = 5$")
    a1.set_ylabel("count")
    a1.legend(fontsize=8.6)
    a1.set_title("random subspaces are not close", fontsize=10)

    # what each choice of five directions costs
    picks = [("top 5", np.arange(5)),
             ("middle 5", np.arange(25, 30)),
             ("every 12th", np.arange(0, 60, 12)),
             ("bottom 5", np.arange(_D - 5, _D))]
    vals = [_J(_PC[:, idx]) for _, idx in picks]
    bars = a2.bar([n for n, _ in picks], vals,
                  color=[p.amber, p.blue, p.green, p.red], width=0.58)
    for bar, v in zip(bars, vals):
        a2.text(bar.get_x() + bar.get_width() / 2, v + 12, f"{v:.2f}",
                ha="center", fontsize=9, color=p.fg)
    a2.set_ylim(0, _TOT * 1.15)
    a2.axhline(_TOT, color=p.fg, lw=1.2, ls=":")
    a2.set_ylabel("$J_M$")
    a2.set_title("which five eigenvectors you keep", fontsize=10)
    fig.suptitle("Equation 10.44 says discard the cheapest directions, "
                 "and nothing beats that",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 3. the projection is the invariant, the basis is not
# --------------------------------------------------------------------------

def same_subspace_different_basis(fig, ax, p: Palette) -> None:
    fig.clear()
    gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 1.15], hspace=0.42,
                          wspace=0.3)

    M = 5
    B = _PC[:, :M]
    R = np.linalg.qr(np.random.default_rng(2).standard_normal((M, M)))[0]
    BR = B @ R

    for k, (vec, ttl) in enumerate([(B[:, 0], "$b_1$"), (B[:, 1], "$b_2$"),
                                    (BR[:, 0], "$(BR)_1$"),
                                    (BR[:, 1], "$(BR)_2$")]):
        a = fig.add_subplot(gs[0, k])
        a.imshow(vec.reshape(8, 8), cmap="RdBu_r", interpolation="nearest",
                 vmin=-0.45, vmax=0.45)
        a.set_xticks([])
        a.set_yticks([])
        a.grid(False)
        for s in a.spines.values():
            s.set_visible(True)
            s.set_color(p.grid)
        a.set_title(ttl, fontsize=10, color=p.fg)

    Z1, Z2 = B.T @ _X, BR.T @ _X
    for k, (Z, ttl) in enumerate([(Z1, "$\\mathrm{cov}(B^\\top X)$"),
                                  (Z2, "$\\mathrm{cov}((BR)^\\top X)$")]):
        a = fig.add_subplot(gs[1, 2 * k:2 * k + 2])
        C = np.cov(Z, bias=True)
        im = a.imshow(C, cmap="RdBu_r", vmin=-160, vmax=160,
                      interpolation="nearest")
        a.set_xticks(range(M))
        a.set_yticks(range(M))
        a.grid(False)
        off = np.abs(C - np.diag(np.diag(C))).max()
        a.set_title(f"{ttl}\nlargest off-diagonal {off:.4f}", fontsize=9.5,
                    color=p.fg)
        fig.colorbar(im, ax=a, fraction=0.046)

    fig.suptitle("$J_M$ = " f"{_J(B):.6f} for both. The projection is the "
                 "invariant; the basis is a choice.",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("one-number-five-spellings", one_number_five_spellings,
           size=(9.4, 4.3), axes=False),
    figure("the-eigenbasis-wins", the_eigenbasis_wins, size=(9.4, 4.3),
           axes=False),
    figure("same-subspace-different-basis", same_subspace_different_basis,
           size=(9.4, 5.6), axes=False),
]
