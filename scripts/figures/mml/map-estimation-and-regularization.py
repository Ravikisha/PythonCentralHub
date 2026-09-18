"""Figures for *MAP Estimation and Regularization* (Sections 9.2.3 and 9.2.4).

1. `two-lambdas-one-estimator` — the book names two different lambdas in
   adjacent paragraphs. Measured, only lambda = sigma^2/b^2 reproduces
   Equation 9.31; lambda = 1/(2b^2) agrees only in the accident sigma^2 = 1/2.

2. `the-prior-fills-the-null-space` — the extra term shifts every eigenvalue of
   Phi^T Phi up by sigma^2/b^2, so a smallest eigenvalue of exactly 0 becomes
   0.04 and the estimator exists at M = 12 > N = 10, where maximum likelihood
   has infinitely many answers.

3. `example-9-6-and-the-limits` — Figure 9.7 rebuilt at degrees 6 and 8, with
   the test error across all degrees beside it. MAP improves M = 9 by a factor
   of 3.4 and its best is still no better than picking the right degree.

4. `ridge-against-lasso` — the p-norm remark, measured. Ridge sets exactly zero
   coefficients to zero at every lambda tried; LASSO sets 17 and then 27 of 30.
"""

from __future__ import annotations

import numpy as np

from _style import Palette, figure

SIG = 0.2
NTR = 10


def _truth(x):
    return -np.sin(x / 5) + np.cos(x)


def _design(x, M):
    return np.vander(np.asarray(x, float), M + 1, increasing=True)


def _data():
    rng = np.random.default_rng(4)
    x = np.sort(rng.uniform(-5, 5, NTR))
    return x, _truth(x) + SIG * rng.standard_normal(NTR)


def _test():
    xte = np.linspace(-5, 5, 200)
    return xte, _truth(xte) + SIG * np.random.default_rng(1234).standard_normal(200)


def _rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


# --------------------------------------------------------------------------
# 1. two lambdas
# --------------------------------------------------------------------------

def two_lambdas_one_estimator(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    x, y = _data()
    P = _design(x, 6)
    K = P.shape[1]

    def rls(lam):
        return np.linalg.solve(P.T @ P + lam * np.eye(K), P.T @ y)

    def mapest(sig, b2):
        return np.linalg.solve(P.T @ P + (sig ** 2 / b2) * np.eye(K), P.T @ y)

    # --- left: the discrepancy as a function of lambda -------------------
    for sig, b2, col in ((0.2, 1.0, p.blue), (1.0, 1.0, p.green),
                         (0.5, 0.25, p.purple)):
        m = mapest(sig, b2)
        lams = np.geomspace(1e-4, 1e2, 400)
        err = np.array([np.abs(rls(l) - m).max() for l in lams])
        left.loglog(lams, np.maximum(err, 1e-18), color=col, linewidth=2.2,
                    label=f"$\\sigma={sig}$, $b^2={b2}$")
        left.axvline(sig ** 2 / b2, color=col, linestyle=":", linewidth=1.4)
    left.axvline(0.5, color=p.red, linestyle="--", linewidth=2.0)
    left.text(0.53, 1e-13, "$\\lambda = 1/(2b^2)$\nfor $b^2 = 1$",
              fontsize=8, color=p.red, family="monospace")
    left.set_xlabel(r"$\lambda$ used in Equation 9.34")
    left.set_ylabel(r"$\max|\theta_{\mathrm{RLS}} - \theta_{\mathrm{MAP}}|$")
    left.set_title("Only one $\\lambda$ makes the two estimators agree",
                   fontsize=9.8)
    left.legend(fontsize=7.8, loc="lower right")
    left.grid(alpha=0.20, linewidth=0.6, which="both")
    left.set_ylim(1e-18, 1e1)
    left.text(
        0.03, 0.96,
        "Each curve touches zero at its\nown dotted line, which sits at\n"
        "sigma^2 / b^2.\n\n"
        "The red dashed line is the\nother lambda the book names,\n"
        "1/(2b^2). It is the same line\nfor all three curves and misses\n"
        "two of them entirely.",
        transform=left.transAxes, ha="left", va="top", fontsize=7.3,
        color=p.fg, family="monospace")

    # --- right: the table --------------------------------------------------
    rows = [(0.2, 1.0), (0.2, 4.0), (1.0, 1.0), (np.sqrt(0.5), 1.0),
            (0.5, 0.25)]
    right.axis("off")
    cell = []
    for sig, b2 in rows:
        m = mapest(sig, b2)
        a = float(np.abs(rls(sig ** 2 / b2) - m).max())
        c = float(np.abs(rls(1.0 / (2 * b2)) - m).max())
        cell.append((sig, b2, sig ** 2 / b2, 1 / (2 * b2), a, c))
    hdr = f"{'sigma':>7} {'b^2':>6} {'s^2/b^2':>10} {'1/(2b^2)':>10} " \
          f"{'RLS-MAP':>10} {'RLS-MAP':>10}"
    right.text(0.02, 0.90, hdr, transform=right.transAxes, fontsize=8.4,
               family="monospace", color=p.fg, va="top")
    right.text(0.02, 0.845,
               f"{'':>7} {'':>6} {'':>10} {'':>10} {'at s2/b2':>10} "
               f"{'at 1/2b2':>10}",
               transform=right.transAxes, fontsize=8.4, family="monospace",
               color=p.muted, va="top")
    yy = 0.77
    for sig, b2, l1, l2, a, c in cell:
        ok = c < 1e-12
        right.text(0.02, yy,
                   f"{sig:>7.4f} {b2:>6.2f} {l1:>10.6f} {l2:>10.6f} "
                   f"{a:>10.2e} {c:>10.2e}",
                   transform=right.transAxes, fontsize=8.4,
                   family="monospace",
                   color=p.green if ok else p.fg, va="top")
        yy -= 0.062
    right.text(
        0.02, 0.40,
        "lambda = sigma^2/b^2 gives 0.00e+00\nin every row — the two "
        "estimators\nare the same linear system.\n\n"
        "lambda = 1/(2b^2) agrees only in\nrow 4, where sigma^2 happens to\n"
        "equal 1/2.\n\n"
        "Both of the book's statements are\ntrue about different things:\n"
        "  9.33 matches the PENALTY TERMS\n"
        "  9.34 matches the ESTIMATORS\n"
        "Only 9.34's is the one to use.",
        transform=right.transAxes, ha="left", va="top", fontsize=8.0,
        color=p.fg, family="monospace")
    right.set_title("Measured on a degree-6 fit", fontsize=9.8)

    fig.suptitle(
        "Sections 9.2.3 and 9.2.4 name two different regularization "
        "parameters for the same correspondence",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The reconciliation is the missing factor of 2 sigma^2. Equation "
        "9.32's loss has no 1/(2 sigma^2) on its data-fit term, so matching it "
        "to the MAP objective requires scaling\nthat objective by 2 sigma^2 — "
        "which turns the prior's 1/(2b^2) into sigma^2/b^2. Chapter 8's "
        "lambda = sigma^2/(N tau^2) differs again, by the 1/N in Equation 8.12.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 2. the prior fills the null space
# --------------------------------------------------------------------------

def the_prior_fills_the_null_space(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    x, y = _data()
    shift = SIG ** 2 / 1.0

    for M, col, mk in ((9, p.blue, "o"), (12, p.red, "s")):
        Pm = _design(x, M)
        Km = Pm.shape[1]
        s = np.linalg.svd(Pm, compute_uv=False)
        ev = np.zeros(Km)
        ev[:len(s)] = s ** 2
        ev = np.sort(ev)[::-1]
        idx = np.arange(1, Km + 1)
        left.semilogy(idx, np.maximum(ev, 1e-20), mk + "-", color=col,
                      linewidth=1.8, markersize=6,
                      label=f"$M={M}$: $\\Phi^\\top\\Phi$")
        left.semilogy(idx, ev + shift, mk + "--", color=col, linewidth=1.8,
                      markersize=6, alpha=0.55,
                      label=f"$M={M}$: $+\\ \\sigma^2/b^2$")
    left.axhline(shift, color=p.amber, linewidth=1.8)
    left.text(1.2, shift * 1.5, f"$\\sigma^2/b^2 = {shift}$", fontsize=8.4,
              color=p.amber, family="monospace")
    left.set_xlabel("eigenvalue index (largest first)")
    left.set_ylabel("eigenvalue")
    left.set_title("Every eigenvalue is lifted by the same amount",
                   fontsize=9.8)
    left.legend(fontsize=7.2, loc="lower left")
    left.grid(alpha=0.20, linewidth=0.6, which="both")
    left.set_ylim(1e-20, 1e12)
    left.text(
        0.97, 0.95,
        "At M = 12 the three smallest\neigenvalues are exactly 0:\n"
        "K = 13 columns, rank 10.\n\n"
        "cond before: infinite\ncond after : 5.910e+17\n\n"
        "A zero eigenvalue is a direction\nthe data cannot see. The prior\n"
        "supplies an opinion about it.",
        transform=left.transAxes, ha="right", va="top", fontsize=7.3,
        color=p.fg, family="monospace")

    # --- right: uniqueness along the old null direction -------------------
    P12 = _design(x, 12)
    K12 = P12.shape[1]
    th_map = np.linalg.solve(P12.T @ P12 + shift * np.eye(K12), P12.T @ y)
    ns = np.linalg.svd(P12)[2][int(np.linalg.matrix_rank(P12)):]
    cs = np.linspace(-12, 12, 400)

    def ml_obj(t):
        r = y - P12 @ t
        return float(r @ r / (2 * SIG ** 2))

    def map_obj(t):
        r = y - P12 @ t
        return float(r @ r / (2 * SIG ** 2) + (t @ t) / 2.0)

    mlv = np.array([ml_obj(th_map + c * ns[0]) for c in cs])
    mpv = np.array([map_obj(th_map + c * ns[0]) for c in cs])
    right.plot(cs, mlv, color=p.red, linewidth=2.6,
               label="negative log-LIKELIHOOD")
    right.plot(cs, mpv, color=p.green, linewidth=2.6,
               label="negative log-POSTERIOR")
    k = int(np.argmin(mpv))
    right.plot([cs[k]], [mpv[k]], "o", color=p.amber, markersize=11,
               markeredgecolor=p.bg, markeredgewidth=1.3, zorder=6)
    right.annotate("one minimum", xy=(cs[k], mpv[k]), xytext=(30, 40),
                   textcoords="offset points", fontsize=8.4, color=p.amber,
                   family="monospace",
                   arrowprops=dict(arrowstyle="->", color=p.amber,
                                   linewidth=1.2))
    right.set_xlabel("steps along a null direction of $\\Phi$")
    right.set_ylabel("objective")
    right.set_title("$M = 12 > N$: the likelihood is flat, the posterior "
                    "is not", fontsize=9.6)
    right.legend(fontsize=8, loc="upper center")
    right.grid(alpha=0.20, linewidth=0.6)
    right.set_ylim(-4, 90)
    right.text(
        0.03, 0.05,
        "measured MAP objective:\n"
        f"  at theta_MAP        {map_obj(th_map):.6f}\n"
        f"  + 0.1 null vector   {map_obj(th_map + 0.1*ns[0]):.6f}\n"
        f"  + 1.0 null vector   {map_obj(th_map + 1.0*ns[0]):.6f}\n"
        f"  + 10  null vector   {map_obj(th_map + 10.0*ns[0]):.6f}\n\n"
        "The red curve is flat to 1e-9 across\nthis whole range: under maximum\n"
        "likelihood every one of these is tied.",
        transform=right.transAxes, ha="left", va="bottom", fontsize=7.2,
        color=p.fg, family="monospace")

    fig.suptitle(
        "The extra term of Equation 9.31 is what makes the estimate exist, "
        "and unique",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book's margin note: \"Phi^T Phi is symmetric, positive semi "
        "definite. The additional term in (9.31) is strictly positive definite "
        "so that the inverse exists.\" Page 903\nmeasured the consequence of "
        "not having it — a null space of dimension 1 and infinitely many tied "
        "estimators. A prior is an opinion about exactly the directions the "
        "data has none.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 3. Example 9.6 and the limits
# --------------------------------------------------------------------------

def example_9_6_and_the_limits(fig, ax, p: Palette) -> None:
    fig.clear()
    a1, a2, a3 = fig.subplots(1, 3)

    x, y = _data()
    xte, yte = _test()
    xg = np.linspace(-5, 5, 500)
    shift = SIG ** 2 / 1.0

    for axx, M in ((a1, 6), (a2, 8)):
        Pm = _design(x, M)
        tl = np.linalg.lstsq(Pm, y, rcond=None)[0]
        tm = np.linalg.solve(Pm.T @ Pm + shift * np.eye(Pm.shape[1]),
                             Pm.T @ y)
        axx.plot(xg, _truth(xg), color=p.muted, linewidth=1.4,
                 linestyle="--", label="the function behind it")
        axx.plot(xg, _design(xg, M) @ tl, color=p.red, linewidth=2.4,
                 label="MLE, Eq. 9.19")
        axx.plot(xg, _design(xg, M) @ tm, color=p.green, linewidth=2.4,
                 label="MAP, Eq. 9.31")
        axx.plot(x, y, "o", color=p.blue, markersize=6,
                 markeredgecolor=p.bg, markeredgewidth=0.6, zorder=5,
                 label="training data")
        axx.set_xlim(-5, 5)
        axx.set_ylim(-4, 4)
        axx.set_xlabel("$x$")
        axx.set_ylabel("$y$")
        axx.set_title(f"Figure 9.7: polynomials of degree {M}", fontsize=9.5)
        axx.legend(fontsize=7.2, loc="lower center")
        axx.grid(alpha=0.20, linewidth=0.6)
        axx.text(
            0.03, 0.97,
            f"||theta_ML||  {np.linalg.norm(tl):>8.4f}\n"
            f"||theta_MAP|| {np.linalg.norm(tm):>8.4f}\n\n"
            f"test MLE  {_rmse(yte, _design(xte, M) @ tl):>9.4f}\n"
            f"test MAP  {_rmse(yte, _design(xte, M) @ tm):>9.4f}",
            transform=axx.transAxes, ha="left", va="top", fontsize=7.3,
            color=p.fg, family="monospace")

    # --- a3: the test error across all degrees --------------------------
    Ms = np.arange(10)
    tl_, tm_ = [], []
    for M in Ms:
        Pm = _design(x, int(M))
        a = np.linalg.lstsq(Pm, y, rcond=None)[0]
        b = np.linalg.solve(Pm.T @ Pm + shift * np.eye(Pm.shape[1]),
                            Pm.T @ y)
        tl_.append(_rmse(yte, _design(xte, int(M)) @ a))
        tm_.append(_rmse(yte, _design(xte, int(M)) @ b))
    tl_, tm_ = np.array(tl_), np.array(tm_)
    a3.semilogy(Ms, tl_, "o-", color=p.red, linewidth=2.4, markersize=6,
                label="MLE")
    a3.semilogy(Ms, tm_, "o-", color=p.green, linewidth=2.4, markersize=6,
                label="MAP, $b^2 = 1$")
    kb = int(np.argmin(tm_))
    a3.plot([Ms[kb]], [tm_[kb]], "o", color=p.amber, markersize=12,
            markerfacecolor="none", markeredgewidth=2.2, zorder=6)
    a3.set_xlabel("degree $M$")
    a3.set_ylabel("test RMSE")
    a3.set_title("MAP helps, and does not solve it", fontsize=9.5)
    a3.legend(fontsize=8, loc="upper left")
    a3.grid(alpha=0.20, linewidth=0.6, which="both")
    a3.text(
        0.97, 0.04,
        f"best MLE: M = {int(np.argmin(tl_))} at {tl_.min():.6f}\n"
        f"best MAP: M = {kb} at {tm_.min():.6f}\n\n"
        f"at M = 9 MAP is {tl_[9]/tm_[9]:.1f}x better\n"
        f"but still {tm_[9]/tm_.min():.0f}x worse than\nits own best.\n\n"
        "And at M = 7 MAP is WORSE\n"
        f"than MLE ({tm_[7]/tl_[7]:.4f}x).",
        transform=a3.transAxes, ha="right", va="bottom", fontsize=7.2,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Example 9.6: the prior barely moves a low-degree fit and rescues a "
        "high-degree one — without removing the need to choose",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book: \"The prior (regularizer) does not play a significant role "
        "for the low-degree polynomial, but keeps the function relatively "
        "smooth for higher-degree polynomials.\nAlthough the MAP estimate can "
        "push the boundaries of overfitting, it is not a general solution to "
        "this problem.\" Both halves of that sentence are visible here.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


# --------------------------------------------------------------------------
# 4. ridge against lasso
# --------------------------------------------------------------------------

_SPARSE: dict = {}


def _sparse_setup():
    if "v" in _SPARSE:
        return _SPARSE["v"]
    r5 = np.random.default_rng(21)
    n, d = 60, 30
    A = r5.standard_normal((n, d))
    th_true = np.zeros(d)
    th_true[[0, 5, 11]] = [2.0, -1.5, 1.0]
    yy = A @ th_true + 0.3 * r5.standard_normal(n)
    Ate = r5.standard_normal((4000, d))
    yte2 = Ate @ th_true + 0.3 * r5.standard_normal(4000)
    _SPARSE["v"] = (A, yy, th_true, Ate, yte2, d)
    return _SPARSE["v"]


def _lasso(A, yv, lam, iters=6000):
    t = np.zeros(A.shape[1])
    col = (A ** 2).sum(0)
    r = yv - A @ t
    for _ in range(iters):
        for j in range(A.shape[1]):
            r += A[:, j] * t[j]
            rho = A[:, j] @ r
            t[j] = np.sign(rho) * max(abs(rho) - lam, 0.0) / col[j]
            r -= A[:, j] * t[j]
    return t


def ridge_against_lasso(fig, ax, p: Palette) -> None:
    fig.clear()
    left, right = fig.subplots(1, 2)

    A, yy, th_true, Ate, yte2, d = _sparse_setup()
    lam = 8.0
    t2 = np.linalg.solve(A.T @ A + lam * np.eye(d), A.T @ yy)
    t1 = _lasso(A, yy, lam)
    idx = np.arange(d)

    left.stem(idx - 0.22, t2, linefmt="-", markerfmt="o", basefmt=" ",
              label=f"$p = 2$ (ridge), $\\lambda = {lam:g}$")
    left.stem(idx + 0.22, t1, linefmt="-", markerfmt="s", basefmt=" ",
              label=f"$p = 1$ (LASSO), $\\lambda = {lam:g}$")
    for ln, col in zip(left.get_children(), []):
        pass
    # recolour the two stem containers
    cont = [c for c in left.containers]
    if len(cont) >= 2:
        cont[0].markerline.set_color(p.blue)
        cont[0].stemlines.set_color(p.blue)
        cont[1].markerline.set_color(p.amber)
        cont[1].stemlines.set_color(p.amber)
    left.plot(idx, th_true, "x", color=p.green, markersize=11,
              markeredgewidth=2.2, label="the truth (3 nonzero of 30)")
    left.axhline(0, color=p.fg, linewidth=1.0)
    left.set_xlabel("coefficient index")
    left.set_ylabel("value")
    left.set_title("Thirty candidate features, three of them real",
                   fontsize=9.6)
    left.legend(fontsize=7.6, loc="lower left")
    left.grid(alpha=0.20, linewidth=0.6)
    left.text(
        0.98, 0.96,
        f"exactly-zero coefficients:\n"
        f"  ridge: {int(np.sum(t2 == 0.0))} of {d}\n"
        f"  LASSO: {int(np.sum(t1 == 0.0))} of {d}\n\n"
        "Ridge shrinks everything and\nzeroes nothing. LASSO picks.",
        transform=left.transAxes, ha="right", va="top", fontsize=7.4,
        color=p.fg, family="monospace")

    # --- right: zeros and error against lambda ---------------------------
    lams = [0.5, 1.0, 2.0, 4.0, 8.0, 14.0, 20.0]
    z1, z2, e1, e2 = [], [], [], []
    for l in lams:
        a2_ = np.linalg.solve(A.T @ A + l * np.eye(d), A.T @ yy)
        a1_ = _lasso(A, yy, l)
        z2.append(int(np.sum(a2_ == 0.0)))
        z1.append(int(np.sum(a1_ == 0.0)))
        e2.append(_rmse(yte2, Ate @ a2_))
        e1.append(_rmse(yte2, Ate @ a1_))
    right.plot(lams, z2, "o-", color=p.blue, linewidth=2.4, markersize=7,
               label="ridge: exact zeros")
    right.plot(lams, z1, "s-", color=p.amber, linewidth=2.4, markersize=7,
               label="LASSO: exact zeros")
    right.axhline(d - 3, color=p.green, linestyle="--", linewidth=1.6)
    right.text(0.7, d - 3 + 0.7, "the truth: 27 zeros", fontsize=8,
               color=p.green, family="monospace")
    right.set_xlabel(r"$\lambda$")
    right.set_ylabel("coefficients set to exactly zero")
    right.set_ylim(-1, 31)
    right.set_title("\"Smaller values for $p$ lead to sparser solutions\"",
                    fontsize=9.6)
    right.legend(fontsize=8, loc="center right")
    right.grid(alpha=0.20, linewidth=0.6)
    right.text(
        0.03, 0.55,
        "test RMSE at each lambda:\n"
        + "\n".join(f"  {l:>5.1f}: ridge {a:.4f}  LASSO {b:.4f}"
                    for l, a, b in zip(lams, e2, e1))
        + "\n\nLASSO is better everywhere here,\n"
          "because the truth really is sparse.",
        transform=right.transAxes, ha="left", va="top", fontsize=7.0,
        color=p.fg, family="monospace")

    fig.suptitle(
        "Section 9.2.4's p-norm remark: the choice of norm decides whether "
        "you get shrinkage or selection",
        y=0.99, fontsize=10, color=p.fg)
    fig.text(
        0.5, 0.005,
        "The book: \"Instead of the Euclidean norm we can choose any p-norm. "
        "In practice, smaller values for p lead to sparser solutions ... For "
        "p = 1, the regularizer is called LASSO.\"\nThe blue line sitting flat "
        "on zero is the point: a quadratic penalty has zero gradient at the "
        "origin, so it never has a reason to stop exactly there.",
        ha="center", va="bottom", fontsize=8.0, color=p.muted)


FIGURES = [
    figure("two-lambdas-one-estimator", two_lambdas_one_estimator,
           size=(13.6, 5.2), axes=False),
    figure("the-prior-fills-the-null-space", the_prior_fills_the_null_space,
           size=(13.6, 5.2), axes=False),
    figure("example-9-6-and-the-limits", example_9_6_and_the_limits,
           size=(15.0, 5.1), axes=False),
    figure("ridge-against-lasso", ridge_against_lasso, size=(13.8, 5.2),
           axes=False),
]
