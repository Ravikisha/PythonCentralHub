"""Figures for *Rotations*.

1. `rotation-preserves` — the two properties in §3.9.4, measured rather than
   asserted. A point cloud is rotated through a full turn in one-degree steps
   and, at every step, the largest change in any pairwise distance and in any
   pairwise angle is recorded. Both stay at the level of floating-point noise,
   and the panel prints the worst value seen over all 360 rotations.

2. `rotations-do-not-commute` — the third property, and the one that costs
   people real bugs. The same two rotations are applied to a shape in both
   orders. In R^2 the two results coincide exactly; in R^3 they do not, and the
   figure measures how far apart they end up. The plane case is drawn beside the
   space case so the difference is attributable to dimension and nothing else.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure


def R2(theta: float) -> np.ndarray:
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s], [s, c]])


def R3_x(theta: float) -> np.ndarray:
    """Equation 3.77: rotation about e1."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def R3_z(theta: float) -> np.ndarray:
    """Equation 3.79: rotation about e3."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def _cloud(n: int = 40, seed: int = 31) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(size=(n, 2)) * np.array([1.4, 0.8])


def _angles(V: np.ndarray) -> np.ndarray:
    """All pairwise angles in a set of vectors, as a flat array."""
    N = V / np.linalg.norm(V, axis=1, keepdims=True)
    G = np.clip(N @ N.T, -1.0, 1.0)
    iu = np.triu_indices(len(V), 1)
    return np.arccos(G[iu])


def rotation_preserves(fig, ax, p: Palette) -> None:
    """Distances and angles under 360 successive rotations."""
    fig.clear()
    left, right = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.0, 1.25]})

    X = _cloud()
    iu = np.triu_indices(len(X), 1)
    d0 = np.linalg.norm(X[iu[0]] - X[iu[1]], axis=1)
    a0 = _angles(X)

    degrees = np.arange(0, 361)
    dist_err = []
    ang_err = []
    det_err = []
    for deg in degrees:
        R = R2(np.radians(float(deg)))
        Y = X @ R.T
        d = np.linalg.norm(Y[iu[0]] - Y[iu[1]], axis=1)
        dist_err.append(float(np.max(np.abs(d - d0))))
        ang_err.append(float(np.max(np.abs(_angles(Y) - a0))))
        det_err.append(abs(float(np.linalg.det(R)) - 1.0))

    for deg, colour, alpha in ((0, p.blue, 1.0), (35, p.green, 0.8), (112, p.amber, 0.8), (250, p.purple, 0.8)):
        Y = X @ R2(np.radians(float(deg))).T
        left.scatter(Y[:, 0], Y[:, 1], s=16, color=colour, alpha=alpha, label=f"{deg}°")
    left.axhline(0, color=p.grid, linewidth=0.9)
    left.axvline(0, color=p.grid, linewidth=0.9)
    left.set_aspect("equal")
    left.set_xlabel("$x_1$")
    left.set_ylabel("$x_2$")
    left.set_title("the same cloud, four rotations", fontsize=10.5)
    left.legend(loc="upper right", fontsize=8, ncol=2)

    right.plot(degrees, np.maximum(dist_err, 1e-18), color=p.blue, linewidth=1.8,
               label="largest change in any distance")
    right.plot(degrees, np.maximum(ang_err, 1e-18), color=p.amber, linewidth=1.8,
               label="largest change in any angle (rad)")
    right.plot(degrees, np.maximum(det_err, 1e-18), color=p.green, linewidth=1.4,
               label=r"$|\det R - 1|$")
    right.axhline(float(np.finfo(float).eps), color=p.muted, linewidth=1.0, linestyle=":")
    right.set_yscale("log")
    right.set_xlabel("rotation angle (degrees)")
    right.set_ylabel("deviation")
    right.set_title("nothing changes, to 15 digits", fontsize=10.5)
    right.legend(loc="lower right", fontsize=8)
    right.text(
        0.03,
        0.94,
        f"pairs measured: {len(d0)} per angle, {len(degrees)} angles\n"
        f"worst distance change: {max(dist_err):.3e}\n"
        f"worst angle change:    {max(ang_err):.3e}\n"
        f"machine epsilon:       {np.finfo(float).eps:.3e}",
        transform=right.transAxes,
        color=p.fg,
        fontsize=8.2,
        family="monospace",
        va="top",
    )


def rotations_do_not_commute(fig, ax, p: Palette) -> None:
    """Order matters in space and does not matter in the plane."""
    fig.clear()
    left = fig.add_subplot(1, 2, 1)
    right = fig.add_subplot(1, 2, 2, projection="3d")

    # -- The plane: the two orders coincide exactly. ------------------------- #
    square = np.array([[1.0, 0.4], [1.9, 0.4], [1.9, 1.1], [1.0, 1.1], [1.0, 0.4]])
    a, b = np.radians(35.0), np.radians(70.0)
    ab = square @ (R2(a) @ R2(b)).T
    ba = square @ (R2(b) @ R2(a)).T
    gap2 = float(np.max(np.linalg.norm(ab - ba, axis=1)))

    left.plot(square[:, 0], square[:, 1], color=p.muted, linewidth=1.6, label="original")
    left.plot(ab[:, 0], ab[:, 1], color=p.blue, linewidth=2.6, label=r"$R(35°)R(70°)\,x$")
    left.plot(ba[:, 0], ba[:, 1], color=p.amber, linewidth=1.6, linestyle="--",
              label=r"$R(70°)R(35°)\,x$")
    left.axhline(0, color=p.grid, linewidth=0.9)
    left.axvline(0, color=p.grid, linewidth=0.9)
    left.set_aspect("equal")
    left.set_xlim(-2.4, 2.4)
    left.set_ylim(-2.4, 2.4)
    left.set_xlabel("$x_1$")
    left.set_ylabel("$x_2$")
    left.set_title(f"in $\\mathbb{{R}}^2$: largest gap {gap2:.2e}", color=p.green, fontsize=10.5)
    left.legend(loc="lower left", fontsize=7.5)

    # -- Space: the two orders land somewhere different. --------------------- #
    box = np.array(
        [
            [1.0, 0.0, 0.0],
            [1.0, 0.8, 0.0],
            [1.0, 0.8, 0.6],
            [1.0, 0.0, 0.6],
            [1.0, 0.0, 0.0],
        ]
    )
    Rx = R3_x(a)
    Rz = R3_z(b)
    xz = box @ (Rx @ Rz).T
    zx = box @ (Rz @ Rx).T
    gap3 = float(np.max(np.linalg.norm(xz - zx, axis=1)))
    comm = float(np.linalg.norm(Rx @ Rz - Rz @ Rx))

    right.plot(box[:, 0], box[:, 1], box[:, 2], color=p.muted, linewidth=1.6, label="original")
    right.plot(xz[:, 0], xz[:, 1], xz[:, 2], color=p.blue, linewidth=2.6,
               label=r"$R_1 R_3\,x$")
    right.plot(zx[:, 0], zx[:, 1], zx[:, 2], color=p.amber, linewidth=2.0, linestyle="--",
               label=r"$R_3 R_1\,x$")
    for q, r in zip(xz, zx):
        right.plot([q[0], r[0]], [q[1], r[1]], [q[2], r[2]], color=p.red, linewidth=1.0)

    right.set_title(f"in $\\mathbb{{R}}^3$: largest gap {gap3:.4f}", color=p.red, fontsize=10.5)
    right.set_xlabel("$x_1$", fontsize=8)
    right.set_ylabel("$x_2$", fontsize=8)
    right.set_zlabel("$x_3$", fontsize=8)
    right.set_xlim(-1.4, 1.4)
    right.set_ylim(-1.4, 1.4)
    right.set_zlim(-1.4, 1.4)
    right.view_init(elev=22, azim=-62)
    right.set_facecolor(p.bg)
    for pane in (right.xaxis, right.yaxis, right.zaxis):
        pane.set_pane_color((0, 0, 0, 0))
        pane._axinfo["grid"]["color"] = p.grid
    right.tick_params(labelsize=7, colors=p.muted)
    right.legend(loc="upper left", fontsize=7.5)

    fig.text(
        0.5,
        0.02,
        f"$\\|R_1R_3 - R_3R_1\\|_F = {comm:.6f}$   —   "
        "planar rotations about one point commute; rotations about different axes do not",
        ha="center",
        color=p.muted,
        fontsize=8.5,
    )


FIGURES = [
    figure("rotation-preserves", rotation_preserves, size=(9.8, 4.2), axes=False),
    figure("rotations-do-not-commute", rotations_do_not_commute, size=(9.8, 4.6), axes=False),
]
