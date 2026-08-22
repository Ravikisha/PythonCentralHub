"""Figures for *Inner Product of Functions*.

1. `sin-cos-cancels` — the book's Example 3.9 with the areas shaded. sin and cos
   over [-pi, pi], their pointwise product underneath, and the positive and
   negative lobes filled separately. The two areas are computed and printed:
   they are equal to the digit, so their difference — the inner product — is
   zero. Orthogonality of functions is exact cancellation, not approximate
   smallness.

2. `fourier-partial-sums` — what the orthogonal family in Equation 3.38 is for.
   A square wave rebuilt from its projections onto sin(kx), with the partial
   sums drawn for a few truncation levels and the squared error against the
   number of terms plotted beside them. Every coefficient is one integral, and
   because the family is orthogonal, adding a term never requires revisiting an
   earlier one.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

GRID = 200001  # odd, so the midpoint of the interval is a sample


def _x() -> np.ndarray:
    return np.linspace(-np.pi, np.pi, GRID)


def sin_cos_cancels(fig, ax, p: Palette) -> None:
    """Two functions, their product, and the two areas that cancel."""
    fig.clear()
    top, bottom = fig.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [1.0, 1.1]})

    x = _x()
    u = np.sin(x)
    v = np.cos(x)
    w = u * v

    top.plot(x, u, color=p.blue, linewidth=2.2, label=r"$u(x) = \sin x$")
    top.plot(x, v, color=p.amber, linewidth=2.2, label=r"$v(x) = \cos x$")
    top.axhline(0, color=p.grid, linewidth=0.9)
    top.legend(loc="upper right", fontsize=8.5, ncol=2)
    top.set_ylim(-1.35, 1.65)
    top.set_ylabel("value")

    bottom.plot(x, w, color=p.purple, linewidth=2.0, label=r"$u(x)\,v(x) = \frac{1}{2}\sin 2x$")
    bottom.fill_between(x, 0, w, where=w > 0, color=p.green, alpha=0.42, label="positive area")
    bottom.fill_between(x, 0, w, where=w < 0, color=p.red, alpha=0.42, label="negative area")
    bottom.axhline(0, color=p.grid, linewidth=0.9)
    bottom.set_xlabel("$x$")
    bottom.set_ylabel("product")
    bottom.legend(loc="upper right", fontsize=8, ncol=3)
    bottom.set_ylim(-0.78, 0.98)

    pos = float(np.trapezoid(np.where(w > 0, w, 0.0), x))
    neg = float(np.trapezoid(np.where(w < 0, w, 0.0), x))
    total = float(np.trapezoid(w, x))

    # A second, independent check: is the product an odd function?
    odd_gap = float(np.max(np.abs(w + w[::-1])))

    bottom.text(
        0.015,
        0.06,
        f"positive area  {pos:+.10f}\n"
        f"negative area  {neg:+.10f}\n"
        f"integral       {total:+.3e}\n"
        f"max |w(x) + w(-x)|  {odd_gap:.1e}  (odd, so it had to cancel)",
        transform=bottom.transAxes,
        color=p.fg,
        fontsize=8.5,
        family="monospace",
        va="bottom",
    )
    for a in (top, bottom):
        a.set_xticks(
            [-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi],
            [r"$-\pi$", r"$-\pi/2$", "0", r"$\pi/2$", r"$\pi$"],
        )
    top.set_title(r"$\langle \sin, \cos\rangle = \int_{-\pi}^{\pi}\sin x\,\cos x\,dx$", fontsize=10.5)


def fourier_partial_sums(fig, ax, p: Palette) -> None:
    """A square wave rebuilt one orthogonal direction at a time."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.35, 1.0]})

    x = _x()
    target = np.sign(np.sin(x))

    # Coefficients by projection: c_k = <target, sin kx> / <sin kx, sin kx>.
    kmax = 64
    coeffs = np.zeros(kmax + 1)
    for k in range(1, kmax + 1):
        basis = np.sin(k * x)
        coeffs[k] = float(np.trapezoid(target * basis, x) / np.trapezoid(basis * basis, x))

    def partial(n: int) -> np.ndarray:
        out = np.zeros_like(x)
        for k in range(1, n + 1):
            out = out + coeffs[k] * np.sin(k * x)
        return out

    left.plot(x, target, color=p.muted, linewidth=1.8, label="square wave")
    for n, colour in ((1, p.red), (3, p.amber), (9, p.blue), (33, p.green)):
        left.plot(x, partial(n), color=colour, linewidth=1.7, label=f"{n} terms")
    left.axhline(0, color=p.grid, linewidth=0.9)
    left.set_xticks(
        [-np.pi, 0, np.pi],
        [r"$-\pi$", "0", r"$\pi$"],
    )
    left.set_xlabel("$x$")
    left.set_ylabel("value")
    left.set_title("partial sums of the projections", fontsize=10.5)
    left.legend(loc="lower right", fontsize=8)

    ns = np.arange(1, kmax + 1)
    errs = np.array([float(np.trapezoid((target - partial(int(n))) ** 2, x)) for n in ns])
    right.plot(ns, errs, color=p.blue, linewidth=2.0, marker="o", markersize=2.6)
    right.set_xscale("log")
    right.set_yscale("log")
    right.set_xlabel("number of terms")
    right.set_ylabel(r"$\|f - f_n\|^2$")
    right.set_title("squared error, measured", fontsize=10.5)

    odd = [round(coeffs[k], 6) for k in (1, 3, 5, 7)]
    even = [round(coeffs[k], 12) for k in (2, 4, 6)]
    right.text(
        0.04,
        0.06,
        f"c1, c3, c5, c7 = {odd}\n"
        f"c2, c4, c6 = {even}\n"
        f"4/pi = {4 / np.pi:.6f}, 4/(3pi) = {4 / (3 * np.pi):.6f}\n"
        f"error at 1 term: {errs[0]:.4f}\n"
        f"error at {kmax} terms: {errs[-1]:.4f}",
        transform=right.transAxes,
        color=p.fg,
        fontsize=7.6,
        family="monospace",
        va="bottom",
    )


FIGURES = [
    figure("sin-cos-cancels", sin_cos_cancels, size=(8.2, 5.6), axes=False),
    figure("fourier-partial-sums", fourier_partial_sums, size=(10.0, 4.2), axes=False),
]
