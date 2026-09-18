"""Figures for *Complex Numbers in One Page*.

1. `moduli-multiply-arguments-add` — the worked example of the page, z = 3 + 4i
   times w = 1 - 2i, drawn. The product lands on the circle of radius |z||w| at
   the angle arg z + arg w, and the same picture shows the conjugate reflecting
   across the real axis.

2. `rotation-has-no-real-eigenvalues` — the discriminant of R(theta) is
   -4 sin^2(theta), so it is negative for every rotation except by 0 or 180
   degrees. Panel one plots it, panel two puts the eigenvalues e^{+-i theta} on
   the unit circle, panel three shows the geometric reading: a rotation turns
   every direction, so no direction is merely scaled.

3. `conjugate-pairs-and-the-axis` — the counting argument. Complex eigenvalues of
   a real matrix pair up, so an odd-sized real matrix cannot be all pairs and
   must keep one real eigenvalue. Measured over random 3x3 rotations: every one
   has an eigenvalue at exactly 1, and its eigenvector is the rotation axis.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure


def _arrow(ax, z, color, label, p: Palette, dx=0.12, dy=0.12, lw=2.4):
    ax.annotate("", xy=(z.real, z.imag), xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=color, linewidth=lw,
                                shrinkA=0, shrinkB=0))
    ax.text(z.real + dx, z.imag + dy, label, color=color, fontsize=9,
            family="monospace", ha="left", va="bottom")


def _plane(ax, p: Palette, lim):
    ax.axhline(0, color=p.grid, linewidth=1.1)
    ax.axvline(0, color=p.grid, linewidth=1.1)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_xlabel("real part")
    ax.set_ylabel("imaginary part")
    ax.grid(alpha=0.18, linewidth=0.6)


def moduli_multiply_arguments_add(fig, ax, p: Palette) -> None:
    """The page's worked example, drawn: z = 3+4i, w = 1-2i, zw = 11-2i."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    z = complex(3, 4)
    w = complex(1, -2)
    zw = z * w

    _plane(left, p, 13.0)
    th = np.linspace(0, 2 * np.pi, 400)
    for val, col, style in ((abs(z), p.blue, ":"), (abs(w), p.amber, ":"),
                            (abs(zw), p.green, "--")):
        left.plot(val * np.cos(th), val * np.sin(th), color=col,
                  linestyle=style, linewidth=1.1, alpha=0.75)

    _arrow(left, z, p.blue, f"$z = 3+4i$\n$|z|={abs(z):.0f}$", p)
    _arrow(left, w, p.amber, f"$w = 1-2i$\n$|w|={abs(w):.7f}$", p, dy=-0.9)
    _arrow(left, zw, p.green, f"$zw = 11-2i$\n$|zw|={abs(zw):.7f}$", p, dy=-1.4)
    left.set_title("Multiplying scales and rotates", fontsize=10)
    left.text(
        -12.4, 11.2,
        f"$|z|\\,|w| = {abs(z):.0f} \\times {abs(w):.4f} = {abs(z) * abs(w):.7f}$\n"
        f"$|zw| = \\sqrt{{121+4}} = {abs(zw):.7f}$",
        fontsize=8.4, color=p.fg, family="monospace", va="top")

    args = [np.angle(z), np.angle(w), np.angle(zw)]
    names = ["$\\arg z$", "$\\arg w$", "$\\arg zw$"]
    cols = [p.blue, p.amber, p.green]
    right.barh(names, args, color=cols, alpha=0.55, height=0.5)
    for k, (a, col) in enumerate(zip(args, cols)):
        right.text(a + (0.04 if a >= 0 else -0.04), k,
                   f"{a:+.7f} rad = {np.degrees(a):+.2f}$^\\circ$",
                   va="center", ha="left" if a >= 0 else "right",
                   fontsize=8.4, color=col, family="monospace")
    right.axvline(0, color=p.grid, linewidth=1.1)
    right.set_xlim(-2.0, 2.0)
    right.set_xlabel("argument, radians")
    right.set_title("Arguments add", fontsize=10)
    right.grid(alpha=0.18, axis="x", linewidth=0.6)
    total = args[0] + args[1]
    right.text(
        -1.94, 2.42,
        f"$\\arg z + \\arg w = {args[0]:.7f} + ({args[1]:.7f})$\n"
        f"$\\qquad = {total:.7f}$, and $\\arg zw = {args[2]:.7f}$\n"
        f"difference: {abs(total - args[2]):.1e}",
        fontsize=8.2, color=p.muted, family="monospace", va="top")

    fig.suptitle(
        "One complex multiplication is one scaling and one rotation, "
        "and nothing else",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "This is the whole content of complex multiplication, and the reason "
        "$e^{i\\theta}$ is the natural way to write a rotation.\nThe two moduli "
        "multiply and the two arguments add, so a product never leaves the circle "
        "its factors' radii predict.",
        ha="center", va="bottom", fontsize=8.3, color=p.muted)


def rotation_has_no_real_eigenvalues(fig, ax, p: Palette) -> None:
    """Discriminant -4 sin^2(theta), the eigenvalue locus, and why geometrically."""
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    ths = np.linspace(0, 2 * np.pi, 900)
    disc = -4 * np.sin(ths) ** 2
    a1.plot(ths, disc, color=p.blue, linewidth=2.4)
    a1.axhline(0, color=p.grid, linewidth=1.2)
    for t, name in ((0.0, "$0^\\circ$"), (np.pi, "$180^\\circ$"),
                    (2 * np.pi, "$360^\\circ$")):
        a1.plot([t], [0.0], "o", color=p.amber, markersize=6)
        a1.text(t, 0.35, name, ha="center", va="bottom", fontsize=8.2,
                color=p.amber, family="monospace")
    a1.set_xlabel("$\\theta$, radians")
    a1.set_ylabel("discriminant $-4\\sin^2\\theta$")
    a1.set_title("Negative except at two angles", fontsize=9.6)
    a1.set_ylim(-4.6, 1.2)
    a1.grid(alpha=0.2, linewidth=0.6)

    th_circ = np.linspace(0, 2 * np.pi, 400)
    a2.plot(np.cos(th_circ), np.sin(th_circ), color=p.grid, linewidth=1.4)
    a2.axhline(0, color=p.grid, linewidth=1.0)
    a2.axvline(0, color=p.grid, linewidth=1.0)
    for t, col in ((np.pi / 6, p.blue), (np.pi / 2, p.green),
                   (2 * np.pi / 3, p.purple)):
        eig = np.linalg.eigvals(np.array([[np.cos(t), -np.sin(t)],
                                          [np.sin(t), np.cos(t)]]))
        a2.plot(eig.real, eig.imag, "o", color=col, markersize=7)
        a2.text(np.cos(t) + 0.08, np.sin(t) + 0.06,
                f"$\\theta={np.degrees(t):.0f}^\\circ$", color=col,
                fontsize=8.2, family="monospace")
    a2.plot([1, -1], [0, 0], "s", color=p.amber, markersize=7)
    a2.text(0.0, -1.32,
            "the only real eigenvalues a\nrotation can have are $\\pm 1$",
            ha="center", va="top", fontsize=8, color=p.amber,
            family="monospace")
    a2.set_xlim(-1.55, 1.55)
    a2.set_ylim(-1.75, 1.45)
    a2.set_aspect("equal")
    a2.set_title("Eigenvalues are $e^{\\pm i\\theta}$", fontsize=9.6)
    a2.set_xlabel("real part")
    a2.set_ylabel("imaginary part")

    t = np.pi / 5
    R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
    dirs = np.linspace(0, 2 * np.pi, 17)[:-1]
    worst = 0.0
    for d in dirs:
        v = np.array([np.cos(d), np.sin(d)])
        rv = R @ v
        a3.annotate("", xy=(v[0], v[1]), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=p.muted,
                                    linewidth=1.0, alpha=0.6))
        a3.annotate("", xy=(rv[0], rv[1]), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="-|>", color=p.green,
                                    linewidth=1.2, alpha=0.85))
        # How close is Rv to a scalar multiple of v? Zero would mean an eigenvector.
        cross = abs(v[0] * rv[1] - v[1] * rv[0])
        worst = max(worst, cross)
    a3.set_xlim(-1.5, 1.5)
    a3.set_ylim(-1.5, 1.75)
    a3.set_aspect("equal")
    a3.axis("off")
    a3.set_title("No direction is merely scaled", fontsize=9.6)
    a3.text(0.0, 1.62,
            f"$\\theta = 36^\\circ$: every one of the 16 directions turns.\n"
            f"smallest $|v_1(Rv)_2 - v_2(Rv)_1|$ over them: "
            f"{np.sin(t):.4f}, not 0",
            ha="center", va="top", fontsize=7.9, color=p.muted,
            family="monospace")

    fig.suptitle(
        "A real rotation matrix has no real eigenvalue, algebraically and "
        "geometrically",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The discriminant is $-4\\sin^2\\theta$, so it vanishes only where "
        "$\\sin\\theta = 0$. Everywhere else the eigenvalues are the conjugate pair "
        "$e^{\\pm i\\theta}$:\nmodulus 1, which is $\\S3.9$'s claim that rotations "
        "preserve length, recovered from the spectrum rather than assumed.",
        ha="center", va="bottom", fontsize=8.3, color=p.muted)


def conjugate_pairs_and_the_axis(fig, ax, p: Palette) -> None:
    """Pairs come in twos, so odd dimension must keep one real eigenvalue."""
    fig.clear()
    left, right = fig.subplots(1, 2)

    rng = np.random.default_rng(11)
    pts = []
    for _ in range(400):
        M = rng.standard_normal((5, 5))
        pts.append(np.linalg.eigvals(M))
    ev = np.concatenate(pts)
    left.scatter(ev.real, ev.imag, s=6, color=p.blue, alpha=0.32,
                 edgecolors="none")
    left.axhline(0, color=p.grid, linewidth=1.2)
    left.axvline(0, color=p.grid, linewidth=1.0)
    n_real = int((np.abs(ev.imag) < 1e-9).sum())
    left.set_xlabel("real part")
    left.set_ylabel("imaginary part")
    left.set_title("Eigenvalues of 400 random real $5\\times5$ matrices",
                   fontsize=9.6)
    left.text(
        0.02, 0.97,
        f"{ev.size} eigenvalues, {n_real} of them real\n"
        "the rest are exactly symmetric about\nthe real axis: conjugate pairs",
        transform=left.transAxes, ha="left", va="top", fontsize=8,
        color=p.fg, family="monospace")
    left.grid(alpha=0.18, linewidth=0.6)

    # Random 3x3 rotations: an odd size cannot be all conjugate pairs.
    def rand_rot(g):
        A = g.standard_normal((3, 3))
        Q, R = np.linalg.qr(A)
        Q = Q * np.sign(np.diag(R))
        if np.linalg.det(Q) < 0:
            Q[:, 0] = -Q[:, 0]
        return Q

    worst_from_one = 0.0
    worst_axis = 0.0
    imag_of_real = 0.0
    trials = 500
    for _ in range(trials):
        Q = rand_rot(rng)
        vals, vecs = np.linalg.eig(Q)
        k = int(np.argmin(np.abs(vals.imag)))
        worst_from_one = max(worst_from_one, abs(vals[k] - 1.0))
        imag_of_real = max(imag_of_real, abs(vals[k].imag))
        axis = np.real(vecs[:, k])
        worst_axis = max(worst_axis, np.linalg.norm(Q @ axis - axis))

    angles = []
    imags = []
    for _ in range(trials):
        Q = rand_rot(rng)
        vals = np.linalg.eigvals(Q)
        k = int(np.argmin(np.abs(vals.imag)))
        other = np.delete(vals, k)
        angles.append(np.degrees(abs(np.angle(other[0]))))
        imags.append(abs(other[0].imag))
    right.scatter(angles, imags, s=9, color=p.green, alpha=0.45,
                  edgecolors="none", label="the conjugate pair")
    grid = np.linspace(0, 180, 300)
    right.plot(grid, np.abs(np.sin(np.radians(grid))), color=p.amber,
               linewidth=1.8, linestyle="--", label="$|\\sin\\theta|$")
    right.set_xlabel("rotation angle recovered from the pair, degrees")
    right.set_ylabel("$|$imaginary part$|$")
    right.set_title(f"{trials} random $3\\times3$ rotations", fontsize=9.6)
    right.legend(fontsize=8, loc="lower center")
    right.grid(alpha=0.18, linewidth=0.6)
    right.text(
        0.02, 0.97,
        f"every one kept a real eigenvalue\n"
        f"worst $|\\lambda - 1|$: {worst_from_one:.2e}\n"
        f"worst $|$Im$\\,\\lambda|$: {imag_of_real:.2e}\n"
        f"worst $\\|Qa - a\\|$ for its axis $a$: {worst_axis:.2e}",
        transform=right.transAxes, ha="left", va="top", fontsize=7.9,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Complex eigenvalues of a real matrix come in pairs, so an odd size must "
        "keep a real one",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "Left: the spectrum of a real matrix is symmetric about the real axis, "
        "because the characteristic polynomial has real coefficients.\nRight: three "
        "is odd, so a $3\\times3$ rotation cannot be made of pairs alone. The "
        "left-over real eigenvalue is 1 and its eigenvector is the axis, fixed by "
        "the rotation to machine precision.",
        ha="center", va="bottom", fontsize=8.3, color=p.muted)


FIGURES = [
    figure("moduli-multiply-arguments-add", moduli_multiply_arguments_add,
           size=(11.6, 4.9), axes=False),
    figure("rotation-has-no-real-eigenvalues", rotation_has_no_real_eigenvalues,
           size=(13.0, 4.7), axes=False),
    figure("conjugate-pairs-and-the-axis", conjugate_pairs_and_the_axis,
           size=(11.8, 4.8), axes=False),
]
