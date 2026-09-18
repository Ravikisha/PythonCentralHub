"""Figures for *Key Steps of PCA in Practice* (Section 10.6).

1. `the-six-steps` — Figure 10.11 rebuilt: original, centred, standardised,
   eigendecomposed, projected, and mapped back through Equation 10.61.

2. `units-change-the-answer` — the same two variables with the first column in
   metres, centimetres and millimetres. The unstandardised leading direction
   swings 77.3982 degrees; after Step 2 the three answers agree to 1.2e-06
   degrees.

3. `standardise-carefully` — two traps in Step 2 and Step 4. Dividing by a zero
   standard deviation produces 2,088 NaNs on the digit-"8" images, and
   standardising a test set with its own statistics reports 15.400250 where the
   honest number is 15.781992.
"""

from __future__ import annotations

import numpy as np
from sklearn.datasets import load_digits

from _style import Palette, figure

_DIG = load_digits()
_A8 = _DIG.data[_DIG.target == 8]
_N, _D = _A8.shape


def _toy(n=160, seed=12):
    rng = np.random.default_rng(seed)
    t = rng.normal(0, 1.6, n)
    return np.c_[3.4 + t, 1.6 + 0.75 * t + rng.normal(0, 0.55, n)]


def _lead(A):
    Ac = A - A.mean(0)
    w, V = np.linalg.eigh(Ac.T @ Ac / len(A))
    v = V[:, -1]
    return v * np.sign(v[int(np.argmax(np.abs(v)))]), w[::-1]


# --------------------------------------------------------------------------
# 1. Figure 10.11
# --------------------------------------------------------------------------

def the_six_steps(fig, ax, p: Palette) -> None:
    fig.clear()
    axes = fig.subplots(2, 3)
    A = _toy()
    mu, sd = A.mean(0), A.std(0)
    C = A - mu
    Z = C / sd
    w, V = np.linalg.eigh(Z.T @ Z / len(Z))
    b = V[:, -1] * np.sign(V[int(np.argmax(np.abs(V[:, -1]))), -1])
    Zt = Z @ np.outer(b, b)
    Back = Zt * sd + mu

    panels = [
        (A, "(a) the original data", p.blue, None),
        (C, "(b) Step 1: subtract the mean", p.blue, None),
        (Z, "(c) Step 2: divide by the sd", p.blue, np.eye(2)),
        (Z, "(d) Step 3: eigendecompose", p.blue, 2.0 * V * np.sqrt(w)[None, :]),
        (Zt, "(e) Step 4: project", p.amber, None),
        (Back, "(f) Equation 10.61: undo it", p.amber, None),
    ]
    for k, (P, ttl, col, arrows) in enumerate(panels):
        a = axes[k // 3][k % 3]
        if k == 4:
            a.scatter(Z[:, 0], Z[:, 1], s=8, color=p.muted, alpha=0.45)
        if k == 5:
            a.scatter(A[:, 0], A[:, 1], s=8, color=p.muted, alpha=0.45)
        a.scatter(P[:, 0], P[:, 1], s=10, color=col, alpha=0.9)
        if arrows is not None:
            for j in (1, 0):
                a.arrow(0, 0, arrows[0, j], arrows[1, j],
                        color=p.amber if j == 1 else p.green, width=0.035,
                        length_includes_head=True, zorder=6)
        a.set_title(ttl, fontsize=9.5)
        a.set_aspect("equal")
        if k in (0, 5):
            a.set_xlim(-1, 8)
            a.set_ylim(-2.2, 5.2)
        else:
            a.set_xlim(-4.2, 4.2)
            a.set_ylim(-4.2, 4.2)
        if k >= 3:
            a.set_xlabel("$x_1$")
        if k % 3 == 0:
            a.set_ylabel("$x_2$")
    fig.suptitle("Figure 10.11: the six steps, on one dataset",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 2. why Step 2 exists
# --------------------------------------------------------------------------

def units_change_the_answer(fig, ax, p: Palette) -> None:
    fig.clear()
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.85], hspace=0.5,
                          wspace=0.38)

    rng = np.random.default_rng(7)
    n = 400
    h = 1.70 + 0.09 * rng.standard_normal(n)
    wt = 20 * (h - 1.70) / 0.09 + 70 + 8 * rng.standard_normal(n)

    units = [("metres", 1.0), ("centimetres", 100.0), ("millimetres", 1000.0)]
    raw, std = [], []
    for k, (name, sc) in enumerate(units):
        A = np.c_[h * sc, wt]
        b, w = _lead(A)
        raw.append(b)
        Ac = (A - A.mean(0))
        a = fig.add_subplot(gs[0, k])
        a.scatter(Ac[:, 0], Ac[:, 1], s=7, color=p.muted, alpha=0.5)
        L = 2.6 * np.abs(Ac).max()
        a.plot([-L * b[0], L * b[0]], [-L * b[1], L * b[1]], color=p.red,
               lw=2.2)
        lim = 1.15 * np.abs(Ac).max()
        a.set_xlim(-lim, lim)
        a.set_ylim(-lim, lim)
        a.set_aspect("equal")
        a.set_title(f"height in {name}\n$b_1$ keeps {w[0]/w.sum():.2%}",
                    fontsize=9.5)
        a.set_xlabel("centred height")
        if k == 0:
            a.set_ylabel("centred weight (kg)")
        As = Ac / A.std(0)
        std.append(_lead(As)[0])

    def ang(u, v):
        return float(np.degrees(np.arccos(min(1.0, abs(u @ v)))))

    b1 = fig.add_subplot(gs[1, :2])
    pairs = [("m vs cm", raw[0], raw[1], std[0], std[1]),
             ("cm vs mm", raw[1], raw[2], std[1], std[2]),
             ("m vs mm", raw[0], raw[2], std[0], std[2])]
    idx = np.arange(3)
    rv = [ang(a_, b_) for _, a_, b_, _, _ in pairs]
    sv = [max(ang(c_, d_), 1e-7) for _, _, _, c_, d_ in pairs]
    b1.bar(idx - 0.18, rv, width=0.36, color=p.red, label="no Step 2")
    b1.bar(idx + 0.18, sv, width=0.36, color=p.blue, label="after Step 2")
    for k, v in enumerate(rv):
        b1.text(k - 0.18, v * 1.25, f"{v:.2f}°", ha="center", fontsize=9,
                color=p.fg)
    for k, v in enumerate(sv):
        b1.text(k + 0.18, v * 1.8, f"{v:.0e}°", ha="center", fontsize=8,
                color=p.fg)
    b1.set_yscale("log")
    b1.set_ylim(1e-8, 1e4)
    b1.set_xticks(idx)
    b1.set_xticklabels([n for n, *_ in pairs])
    b1.set_ylabel("angle between the two $b_1$")
    b1.legend(fontsize=9, loc="upper left")
    b1.set_title("the data never changed; only the unit did", fontsize=10)

    b2 = fig.add_subplot(gs[1, 2])
    A = np.c_[h, wt]
    Ac = A - A.mean(0)
    S = Ac.T @ Ac / n
    Ss = (Ac / A.std(0)).T @ (Ac / A.std(0)) / n
    b2.bar(["$\\mathrm{tr}(S)$", "$\\mathrm{tr}(S_{\\mathrm{std}})$"],
           [np.trace(S), np.trace(Ss)], color=[p.red, p.blue], width=0.5)
    b2.set_yscale("log")
    b2.set_ylim(1, 1e4)
    for k, v in enumerate([np.trace(S), np.trace(Ss)]):
        b2.text(k, v * 1.4, f"{v:.4f}", ha="center", fontsize=9, color=p.fg)
    b2.set_title("the total variance\nis $D$ after Step 2", fontsize=9.5)

    fig.suptitle("Step 2 is not cosmetic: without it, PCA answers a question "
                 "about your units",
                 fontsize=11.5, fontweight="bold", color=p.fg)


# --------------------------------------------------------------------------
# 3. two traps
# --------------------------------------------------------------------------

def standardise_carefully(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2 = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.0, 1.15]})

    sd = _A8.std(0)
    a1.imshow(sd.reshape(8, 8), cmap="inferno", interpolation="nearest")
    for k in np.flatnonzero(sd == 0):
        a1.add_patch(__import__("matplotlib").patches.Rectangle(
            (k % 8 - 0.5, k // 8 - 0.5), 1, 1, fill=False, edgecolor=p.blue,
            lw=1.8))
    a1.set_xticks([])
    a1.set_yticks([])
    a1.grid(False)
    for s in a1.spines.values():
        s.set_visible(True)
        s.set_color(p.grid)
    a1.set_title(f"{int((sd == 0).sum())} pixels have sd exactly 0\n"
                 f"Equation 10.58 makes "
                 f"{int((sd == 0).sum()) * _N:,} NaNs", fontsize=10)

    rng = np.random.default_rng(3)
    idx = rng.permutation(_N)
    tr, te = idx[:140], idx[140:]
    mu, sdt = _A8[tr].mean(0), _A8[tr].std(0)
    live = sdt > 0
    Z = np.zeros((len(tr), _D))
    Z[:, live] = (_A8[tr][:, live] - mu[live]) / sdt[live]
    w, V = np.linalg.eigh(Z.T @ Z / len(tr))
    PC = V[:, ::-1]

    mu_te, sd_te = _A8[te].mean(0), _A8[te].std(0)
    live_te = sd_te > 0

    def rt(B, m, s, lv):
        Zq = np.zeros((len(te), _D))
        Zq[:, lv] = (_A8[te][:, lv] - m[lv]) / s[lv]
        Xt = (Zq @ B) @ B.T
        back = Xt * np.where(lv, s, 1.0) + m
        return float(np.sqrt(((_A8[te] - back) ** 2).sum(1).mean()))

    Ms = [1, 5, 10, 20, 40]
    honest = [rt(PC[:, :M], mu, sdt, live) for M in Ms]
    leaky = [rt(PC[:, :M], mu_te, sd_te, live_te) for M in Ms]
    a2.plot(Ms, honest, color=p.blue, lw=2.2, marker="o",
            label="training mean and sd (Step 4)")
    a2.plot(Ms, leaky, color=p.red, lw=2.2, marker="s", ls="--",
            label="the test set's own mean and sd")
    for M, hh, ll in zip(Ms, honest, leaky):
        if M == 10:
            a2.annotate(f"{hh:.6f}", (M + 1.4, hh + 1.8), fontsize=9,
                        color=p.blue)
            a2.annotate(f"{ll:.6f}", (M + 1.4, ll - 3.0), fontsize=9,
                        color=p.red)
    a2.set_xlabel("$M$")
    a2.set_ylabel("test RMS error, original units")
    a2.legend(fontsize=9)
    a2.set_title("using the test set's statistics flatters the result",
                 fontsize=10)
    fig.suptitle("Two ways Step 2 goes wrong, both silent",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("the-six-steps", the_six_steps, size=(9.4, 6.0), axes=False),
    figure("units-change-the-answer", units_change_the_answer,
           size=(9.6, 6.2), axes=False),
    figure("standardise-carefully", standardise_carefully, size=(9.4, 4.2),
           axes=False),
]
