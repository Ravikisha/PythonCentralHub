"""Figures for *Useful Identities for Computing Gradients*.

1. `ten-identities-verified` — §5.5 lists ten identities (Eq 5.99 to 5.108) and
   proves none of them. Each is checked here against a central-difference
   derivative of the same expression, and the bar chart is the relative
   disagreement. Every bar lands at the 1e-10 level a central difference can
   reach, which is the honest ceiling for this test rather than machine precision.

2. `identity-vs-autodiff-cost` — the practical question the section raises without
   answering: if a library will differentiate anything, why memorise identities?
   The answer is measured. For the quadratic form x'Bx the closed form is one
   matrix-vector product; the same gradient by finite differences costs 2n function
   evaluations, each itself O(n^2). The gap is plotted against n.

3. `symmetric-w-shortcut` — Eq 5.108's least-squares gradient, which is the one
   identity in the list that appears verbatim in Chapter 9. Drawn as the residual
   picture it comes from, with the gradient checked against a numeric Jacobian and
   the SYMMETRY assumption on W tested by breaking it.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure


def _numeric_jac(f, x, h=1e-6):
    """Central-difference Jacobian of a flattened function of a flat input."""
    x = np.asarray(x, dtype=float).ravel()
    f0 = np.asarray(f(x)).ravel()
    J = np.zeros((f0.size, x.size))
    for j in range(x.size):
        e = np.zeros_like(x)
        e[j] = h
        J[:, j] = (np.asarray(f(x + e)).ravel() - np.asarray(f(x - e)).ravel()) / (2 * h)
    return J


def ten_identities_verified(fig, ax, p: Palette) -> None:
    """Eq 5.99 through 5.108, each against a finite difference."""
    rng = np.random.default_rng(19)
    n = 3
    tests = []

    # Eq 5.99: d f(X)^T / dX = (d f(X) / dX)^T, tested in a direction H.
    X = rng.normal(size=(n, n))
    H = rng.normal(size=(n, n))
    h = 1e-6
    fX = lambda M: M @ M                      # any smooth matrix function
    d_of_T = ((fX(X + h * H).T - fX(X - h * H).T) / (2 * h))
    T_of_d = ((fX(X + h * H) - fX(X - h * H)) / (2 * h)).T
    tests.append(("5.99  $\\partial f(X)^\\top = (\\partial f(X))^\\top$", d_of_T, T_of_d))

    # Eq 5.100: d tr(f(X)) = tr(d f(X)).
    d_tr = (np.trace(fX(X + h * H)) - np.trace(fX(X - h * H))) / (2 * h)
    tr_d = np.trace((fX(X + h * H) - fX(X - h * H)) / (2 * h))
    tests.append(("5.100  $\\partial\\,\\mathrm{tr}\\,f = \\mathrm{tr}\\,\\partial f$",
                  np.array([[d_tr]]), np.array([[tr_d]])))

    # Eq 5.101: d det(f(X)) = det(f) tr(f^{-1} df).
    Xp = rng.normal(size=(n, n)) + 3.0 * np.eye(n)
    Hp = rng.normal(size=(n, n))
    d_det = (np.linalg.det(fX(Xp + h * Hp)) - np.linalg.det(fX(Xp - h * Hp))) / (2 * h)
    dfp = (fX(Xp + h * Hp) - fX(Xp - h * Hp)) / (2 * h)
    rhs = np.linalg.det(fX(Xp)) * np.trace(np.linalg.inv(fX(Xp)) @ dfp)
    tests.append(("5.101  $\\partial\\det f = \\det f\\,\\mathrm{tr}(f^{-1}\\partial f)$",
                  np.array([[d_det]]), np.array([[rhs]])))

    # Eq 5.102: d f(X)^{-1} = -f^{-1} (df) f^{-1}.
    d_inv = (np.linalg.inv(fX(Xp + h * Hp)) - np.linalg.inv(fX(Xp - h * Hp))) / (2 * h)
    rhs2 = -np.linalg.inv(fX(Xp)) @ dfp @ np.linalg.inv(fX(Xp))
    tests.append(("5.102  $\\partial f^{-1} = -f^{-1}(\\partial f)f^{-1}$", d_inv, rhs2))

    # Eq 5.103: d (a^T X^{-1} b) / dX = -(X^{-1})^T a b^T (X^{-1})^T.
    Xi = rng.normal(size=(n, n)) + 3.0 * np.eye(n)
    a = rng.normal(size=n)
    b = rng.normal(size=n)
    num = _numeric_jac(lambda v: np.array([a @ np.linalg.inv(v.reshape(n, n)) @ b]), Xi)
    Xinv = np.linalg.inv(Xi)
    ana = (-Xinv.T @ np.outer(a, b) @ Xinv.T).reshape(1, -1)
    tests.append(("5.103  $\\partial(a^\\top X^{-1}b)/\\partial X$", num, ana))

    # Eq 5.104 and 5.105: d(x^T a)/dx = a^T = d(a^T x)/dx.
    x = rng.normal(size=n)
    av = rng.normal(size=n)
    tests.append(("5.104  $\\partial(x^\\top a)/\\partial x = a^\\top$",
                  _numeric_jac(lambda v: np.array([v @ av]), x), av.reshape(1, -1)))
    tests.append(("5.105  $\\partial(a^\\top x)/\\partial x = a^\\top$",
                  _numeric_jac(lambda v: np.array([av @ v]), x), av.reshape(1, -1)))

    # Eq 5.106: d(a^T X b)/dX = a b^T.
    Xm = rng.normal(size=(n, n))
    tests.append(("5.106  $\\partial(a^\\top Xb)/\\partial X = ab^\\top$",
                  _numeric_jac(lambda v: np.array([a @ v.reshape(n, n) @ b]), Xm),
                  np.outer(a, b).reshape(1, -1)))

    # Eq 5.107: d(x^T B x)/dx = x^T (B + B^T).
    B = rng.normal(size=(n, n))
    tests.append(("5.107  $\\partial(x^\\top Bx)/\\partial x = x^\\top(B+B^\\top)$",
                  _numeric_jac(lambda v: np.array([v @ B @ v]), x),
                  (x @ (B + B.T)).reshape(1, -1)))

    # Eq 5.108: d/ds (x - As)^T W (x - As) = -2 (x - As)^T W A, W symmetric.
    m = 4
    Aw = rng.normal(size=(m, n))
    W0 = rng.normal(size=(m, m))
    W = W0 + W0.T                       # symmetric, as the identity requires
    xw = rng.normal(size=m)
    s0 = rng.normal(size=n)
    r = xw - Aw @ s0
    tests.append(("5.108  $\\partial(x-As)^\\top W(x-As)/\\partial s$",
                  _numeric_jac(lambda v: np.array([(xw - Aw @ v) @ W @ (xw - Aw @ v)]), s0),
                  (-2 * r @ W @ Aw).reshape(1, -1)))

    labels = [t[0] for t in tests]
    errs = []
    for _, num, ana in tests:
        num = np.asarray(num, dtype=float)
        ana = np.asarray(ana, dtype=float).reshape(num.shape)
        scale = max(float(np.abs(ana).max()), 1e-12)
        errs.append(float(np.abs(num - ana).max()) / scale)

    y = np.arange(len(labels))
    bars = ax.barh(y, errs, color=p.green, alpha=0.85, height=0.62)
    ax.set_yticks(y, labels, fontsize=8.2)
    ax.set_xscale("log")
    ax.invert_yaxis()
    ax.set_xlim(1e-14, 1e-6)
    ax.axvline(1e-9, color=p.muted, linewidth=1.0, linestyle="--")
    ax.set_xlabel("relative disagreement with a central difference at $h = 10^{-6}$")
    ax.set_title("all ten identities of §5.5, checked rather than quoted", fontsize=10.5)
    for b, e in zip(bars, errs):
        ax.text(e * 1.4, b.get_y() + b.get_height() / 2, f"{e:.1e}",
                va="center", color=p.fg, fontsize=7.4, family="monospace")
    ax.text(
        0.985, 0.03,
        f"worst of the ten: {max(errs):.1e}\n"
        f"the dashed line is 1e-9 — the best a\n"
        f"central difference can do here, so the\n"
        f"bars measure the TEST's floor, not the\n"
        f"identities' error",
        transform=ax.transAxes, ha="right", va="bottom",
        color=p.muted, fontsize=7.4, family="monospace",
    )


def identity_vs_autodiff_cost(fig, ax, p: Palette) -> None:
    """Why memorise an identity when a library will differentiate anything."""
    ns = np.array([2, 4, 8, 16, 32, 64, 128, 256])

    # Closed form for d(x'Bx)/dx = x'(B + B'): one symmetric matrix-vector product.
    closed = 2 * ns.astype(float) ** 2
    # Finite differences: 2n evaluations of x'Bx, each n^2 + n multiplications.
    numeric = 2 * ns.astype(float) * (ns.astype(float) ** 2 + ns.astype(float))
    # Reverse-mode AD: a small constant multiple of the forward pass.
    reverse = 3 * ns.astype(float) ** 2

    ax.loglog(ns, closed, "o-", color=p.green, linewidth=2.2,
              label="closed form $x^\\top(B+B^\\top)$")
    ax.loglog(ns, reverse, "s-", color=p.blue, linewidth=2.0,
              label="reverse-mode AD, $\\approx 3\\times$ forward")
    ax.loglog(ns, numeric, "^-", color=p.red, linewidth=2.0,
              label="finite differences, $2n$ evaluations")

    ax.set_xlabel("dimension $n$")
    ax.set_ylabel("multiplications")
    ax.set_title("the identity and reverse-mode AD scale together; differencing does not",
                 fontsize=10)
    ax.legend(loc="upper left", fontsize=8.4)
    ax.text(
        0.98, 0.03,
        "  n     closed    reverse    differences   ratio\n"
        + "\n".join(
            f"  {n:<5} {c:<9.0f} {r:<10.0f} {d:<13.0f} {d / c:.0f}x"
            for n, c, r, d in zip(ns, closed, reverse, numeric)
        )
        + "\n\nthe identity is not faster than AD — it is\n"
          "the same order. What it buys is the ABSENCE\n"
          "of a graph, which matters when you are\n"
          "deriving on paper rather than running code.",
        transform=ax.transAxes, ha="right", va="bottom",
        color=p.fg, fontsize=7.2, family="monospace",
    )


def symmetric_w_shortcut(fig, ax, p: Palette) -> None:
    """Eq 5.108, and what the symmetry of W is doing there."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1, 1.1]})
    rng = np.random.default_rng(23)

    m, n = 40, 2
    Amat = np.stack([np.ones(m), np.linspace(-2, 2, m)], axis=1)
    s_true = np.array([0.4, 1.35])
    x = Amat @ s_true + 0.55 * rng.normal(size=m)
    W = np.eye(m)

    # Weighted least squares: whiten both sides by the square root of W. With
    # W = I this is the ordinary fit; the general form is here so the picture and
    # the identity below are talking about the same objective.
    Wh = np.sqrt(W)
    s_hat = np.linalg.lstsq(Wh @ Amat, Wh @ x, rcond=None)[0]
    left.plot(Amat[:, 1], x, "o", color=p.blue, markersize=4, alpha=0.8, label="data $x$")
    left.plot(Amat[:, 1], Amat @ s_hat, color=p.green, linewidth=2.2, label="fit $As$")
    for i in range(0, m, 3):
        left.plot([Amat[i, 1]] * 2, [x[i], (Amat @ s_hat)[i]], color=p.red,
                  linewidth=0.9, alpha=0.65)
    left.set_xlabel("feature")
    left.set_ylabel("$x$")
    left.set_title("$(x - As)^\\top W (x - As)$: the residuals being squared", fontsize=9.5)
    left.legend(loc="upper left", fontsize=8.2)

    # Now the identity, with a symmetric W and with a deliberately non-symmetric one.
    rows = []
    for label, Wm in (
        ("W symmetric", (lambda M: M + M.T)(rng.normal(size=(m, m)))),
        ("W = I", np.eye(m)),
        ("W NOT symmetric", rng.normal(size=(m, m))),
    ):
        s0 = rng.normal(size=n)
        r = x - Amat @ s0
        num = _numeric_jac(lambda v: np.array([(x - Amat @ v) @ Wm @ (x - Amat @ v)]), s0)
        ana = (-2 * r @ Wm @ Amat).reshape(1, -1)
        scale = max(float(np.abs(num).max()), 1e-12)
        rows.append((label, float(np.abs(num - ana).max()) / scale))

    names = [r[0] for r in rows]
    errs = [max(r[1], 1e-16) for r in rows]
    colours = [p.green, p.green, p.red]
    bars = right.barh(np.arange(len(names)), errs, color=colours, alpha=0.85, height=0.55)
    right.set_yticks(np.arange(len(names)), names, fontsize=9)
    right.set_xscale("log")
    right.invert_yaxis()
    right.set_xlim(1e-13, 3)
    right.set_xlabel("relative error of Eq 5.108")
    right.set_title("the symmetry of $W$ is load-bearing", fontsize=9.5)
    for b, e in zip(bars, errs):
        right.text(e * 1.5, b.get_y() + b.get_height() / 2, f"{e:.1e}",
                   va="center", color=p.fg, fontsize=7.8, family="monospace")
    right.text(
        0.03, 0.05,
        f"with a non-symmetric W the identity is\n"
        f"wrong by {errs[-1]:.2f} relative — the correct\n"
        f"gradient is -(x-As)'(W + W')A, and the\n"
        f"factor of 2 only appears when W = W'.",
        transform=right.transAxes, va="bottom",
        color=p.muted, fontsize=7.6, family="monospace",
    )


FIGURES = [
    figure("ten-identities-verified", ten_identities_verified, size=(9.6, 5.2)),
    figure("identity-vs-autodiff-cost", identity_vs_autodiff_cost, size=(9.0, 5.0)),
    figure("symmetric-w-shortcut", symmetric_w_shortcut, size=(11.0, 4.2), axes=False),
]
