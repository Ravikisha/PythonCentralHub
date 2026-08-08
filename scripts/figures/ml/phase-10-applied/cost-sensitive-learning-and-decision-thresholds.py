"""Figures for *Cost-Sensitive Learning and Decision Thresholds*."""

import functools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import amounts_for, fraud, smote  # noqa: E402
from _style import Palette, figure  # noqa: E402

C_FP = 5.0          # euros to review one flagged transaction
C_FN = 500.0        # euros lost to one missed fraud (flat case)
GRID = np.geomspace(1e-5, 0.999, 600)


def cost_of(pred, y_true, c_fn):
    """Total euros: review cost for false alerts plus the loss of what got through."""
    fp = int(((pred == 1) & (y_true == 0)).sum())
    missed = (pred == 0) & (y_true == 1)
    loss = (float(np.asarray(c_fn)[missed].sum()) if np.ndim(c_fn)
            else int(missed.sum()) * c_fn)
    return fp * C_FP + loss, fp, int(missed.sum())


@functools.lru_cache(maxsize=2)
def setup(n=20000, seed=0, amount_seed=5):
    """Fit on 50%, tune thresholds on 20%, report on the remaining 30%."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X, y, _ = fraud(n=n, seed=seed)
    amount = amounts_for(X, seed=amount_seed)

    X_fit, X_rest, y_fit, y_rest, a_fit, a_rest = train_test_split(
        X, y, amount, test_size=0.5, random_state=0, stratify=y)
    X_val, X_te, y_val, y_te, a_val, a_te = train_test_split(
        X_rest, y_rest, a_rest, test_size=0.6, random_state=0, stratify=y_rest)

    model = make_pipeline(StandardScaler(),
                          LogisticRegression(max_iter=3000)).fit(X_fit, y_fit)

    X_sm, y_sm = smote(X_fit.to_numpy(), y_fit, seed=1)
    resampled = make_pipeline(StandardScaler(),
                              LogisticRegression(max_iter=3000)).fit(X_sm, y_sm)

    return {
        "p_val": model.predict_proba(X_val)[:, 1],
        "p_test": model.predict_proba(X_te)[:, 1],
        "p_test_smote": resampled.predict_proba(X_te.to_numpy())[:, 1],
        "y_val": np.asarray(y_val), "y_test": np.asarray(y_te),
        "a_val": np.asarray(a_val), "a_test": np.asarray(a_te),
        "mean_amount": float(np.mean(a_fit)),
        "counts": (len(y_fit), int(y_fit.sum()), len(y_val), int(y_val.sum()),
                   len(y_te), int(y_te.sum())),
    }


def tuned_threshold(p, y, c_fn):
    costs = np.array([cost_of((p >= t).astype(int), y, c_fn)[0] for t in GRID])
    return float(GRID[int(np.argmin(costs))])


def cost_versus_threshold(fig, axes, p: Palette) -> None:
    """One U-shaped curve, and three ways of picking a point on it."""
    d = setup()
    y_te, p_te = d["y_test"], d["p_test"]
    curve = np.array([cost_of((p_te >= t).astype(int), y_te, C_FN)[0]
                      for t in GRID])

    t_star = C_FP / (C_FP + C_FN)
    t_tuned = tuned_threshold(d["p_val"], d["y_val"], C_FN)
    best = int(np.argmin(curve))

    axes.plot(GRID, curve, color=p.amber, lw=2.4)

    # Theory and the validation-tuned threshold land almost on top of each
    # other, so the readout goes in the legend rather than on the curve.
    c_star = cost_of((p_te >= t_star).astype(int), y_te, C_FN)[0]
    c_tuned = cost_of((p_te >= t_tuned).astype(int), y_te, C_FN)[0]
    c_default = cost_of((p_te >= 0.5).astype(int), y_te, C_FN)[0]

    axes.scatter([0.5], [c_default], color=p.red, s=70, zorder=6,
                 label=f"default 0.50 — EUR {c_default:,.0f}")
    axes.scatter([t_star], [c_star], color=p.green, s=70, zorder=6,
                 label=f"theory t* = {t_star:.4f} — EUR {c_star:,.0f}")
    axes.scatter([t_tuned], [c_tuned], color=p.amber, s=70, zorder=7,
                 marker="D", label=f"tuned on validation {t_tuned:.4f} — "
                                   f"EUR {c_tuned:,.0f}")
    axes.scatter([GRID[best]], [curve[best]], color=p.blue, s=70, zorder=6,
                 label=f"test-set optimum {GRID[best]:.4f} — "
                       f"EUR {curve[best]:,.0f}")
    axes.legend(loc="upper right", fontsize=9)
    axes.set_xscale("log")
    axes.set_xlabel("threshold (log scale)")
    axes.set_ylabel("total cost on the test set (EUR)")
    axes.set_ylim(0, curve.max() * 1.12)
    axes.set_title(f"Cost = {C_FP:.0f} EUR per review + {C_FN:.0f} EUR per "
                   f"missed fraud")


def cost_decomposition(fig, axes, p: Palette) -> None:
    """Where the money goes under four policies."""
    d = setup()
    y_te, p_te = d["y_test"], d["p_test"]
    t_star = C_FP / (C_FP + C_FN)

    policies = [
        ("review\nnothing", np.zeros(len(y_te), dtype=int)),
        ("review\neverything", np.ones(len(y_te), dtype=int)),
        ("threshold\n0.50", (p_te >= 0.5).astype(int)),
        (f"threshold\n{t_star:.4f}", (p_te >= t_star).astype(int)),
    ]

    review, missed, totals = [], [], []
    for _, pred in policies:
        total, fp, fn = cost_of(pred, y_te, C_FN)
        review.append(fp * C_FP)
        missed.append(fn * C_FN)
        totals.append(total)

    idx = np.arange(len(policies))
    axes.bar(idx, review, color=p.blue, label="reviews (5 EUR each)")
    axes.bar(idx, missed, bottom=review, color=p.red,
             label="fraud that got through (500 EUR each)")
    for i, total in enumerate(totals):
        axes.annotate(f"EUR {total:,.0f}", (i, total + 900), ha="center",
                      fontsize=10, color=p.muted)
    axes.set_xticks(idx)
    axes.set_xticklabels([n for n, _ in policies], fontsize=9.5)
    axes.set_ylim(0, max(totals) * 1.22)
    axes.set_ylabel("cost (EUR)")
    axes.set_title(f"Spending EUR {review[-1]:,.0f} on reviews avoids "
                   f"EUR {missed[0] - missed[-1]:,.0f} of losses")
    axes.legend(loc="upper right", fontsize=9)


def miscalibration_penalty(fig, axes, p: Palette) -> None:
    """The closed-form threshold is only valid for a calibrated model."""
    d = setup()
    y_te = d["y_test"]
    t_star = C_FP / (C_FP + C_FN)

    axs = fig.subplots(1, 2)

    for ax, (name, pr, col) in zip(axs, (("plain model", d["p_test"], p.blue),
                                         ("after SMOTE", d["p_test_smote"],
                                          p.red))):
        curve = np.array([cost_of((pr >= t).astype(int), y_te, C_FN)[0]
                          for t in GRID])
        own = int(np.argmin(curve))
        at_star = cost_of((pr >= t_star).astype(int), y_te, C_FN)[0]

        ax.plot(GRID, curve, color=col, lw=2.2)
        ax.scatter([t_star], [at_star], color=p.amber, s=70, zorder=6,
                   label=f"t* = {t_star:.4f} — EUR {at_star:,.0f}")
        ax.scatter([GRID[own]], [curve[own]], color=p.green, s=70, zorder=6,
                   label=f"its own optimum {GRID[own]:.4f} — "
                         f"EUR {curve[own]:,.0f}")
        ax.set_xscale("log")
        ax.set_xlabel("threshold (log scale)")
        ax.set_ylim(0, max(curve.max(), at_star) * 1.32)
        ax.set_title(f"{name} — mean p {pr.mean():.4f}", fontsize=10.5)
        ax.legend(loc="upper center", fontsize=8.5)

    axs[0].set_ylabel("total cost (EUR)")
    fig.suptitle("Same rule, same costs. On the resampled model the rule points "
                 "at the wrong threshold.", fontsize=10.5, color=p.muted)


def ratio_sensitivity(fig, axes, p: Palette) -> None:
    """Being roughly right about the cost ratio is enough."""
    d = setup()
    y_te, p_te = d["y_test"], d["p_test"]
    best = min(cost_of((p_te >= t).astype(int), y_te, C_FN)[0] for t in GRID)

    ratios = np.geomspace(2, 5000, 120)
    costs = np.array([cost_of((p_te >= 1 / (1 + r)).astype(int), y_te, C_FN)[0]
                      for r in ratios])

    axes.plot(ratios, costs / best, color=p.blue, lw=2.4)
    axes.axhline(1.0, color=p.green, lw=1.2, ls="--",
                 label="best achievable on this test set")
    axes.axvline(C_FN / C_FP, color=p.amber, lw=1.4,
                 label=f"true ratio {C_FN / C_FP:.0f}")
    inside = ratios[(costs / best) <= 1.4]
    axes.axvspan(inside.min(), inside.max(), color=p.green, alpha=0.10)
    axes.annotate(f"within 1.4x of optimal for any assumed ratio\n"
                  f"between {inside.min():.0f} and {inside.max():.0f}",
                  (inside.min() * 1.1, 2.1), fontsize=9.5, color=p.green)
    axes.set_xscale("log")
    axes.set_xlabel("assumed cost ratio $C_{FN}/C_{FP}$ (log scale)")
    axes.set_ylabel("cost, relative to the best possible")
    axes.set_ylim(0.9, max(3.0, float((costs / best).max()) * 1.05))
    axes.set_title("Guessing the cost ratio within an order of magnitude is "
                   "enough")
    axes.legend(loc="upper center", fontsize=9)


def per_row_thresholds(fig, axes, p: Palette) -> None:
    """When the loss is the amount, every row gets its own threshold."""
    small = setup()
    large = setup(n=400000, seed=3, amount_seed=9)

    axs = fig.subplots(1, 2)

    a_te, p_te, y_te = small["a_test"], small["p_test"], small["y_test"]
    t_row = C_FP / (C_FP + a_te)
    order = np.argsort(a_te)
    axs[0].plot(a_te[order], t_row[order], color=p.amber, lw=2.2,
                label="$t^*_i = C_{FP} / (C_{FP} + \\mathrm{amount}_i)$")
    axs[0].scatter(a_te[y_te == 1], p_te[y_te == 1], s=26, color=p.red,
                   label="fraud, predicted probability")
    axs[0].scatter(a_te[y_te == 0][::40], p_te[y_te == 0][::40], s=6,
                   color=p.muted, alpha=0.5, label="legitimate (1 in 40 shown)")
    axs[0].set_xscale("log")
    axs[0].set_yscale("log")
    axs[0].set_xlabel("transaction amount (EUR, log scale)")
    axs[0].set_ylabel("probability / threshold (log scale)")
    axs[0].set_title("A row is flagged when its dot sits above the line",
                     fontsize=10.5)
    axs[0].legend(loc="lower left", fontsize=8)

    rows = []
    for label, d in (("test set\n26 frauds", small),
                     ("test set\n598 frauds", large)):
        y, pr, a = d["y_test"], d["p_test"], d["a_test"]
        per_row = cost_of((pr >= C_FP / (C_FP + a)).astype(int), y, a)[0]
        t_tuned = tuned_threshold(d["p_val"], d["y_val"], d["a_val"])
        single = cost_of((pr >= t_tuned).astype(int), y, a)[0]
        rows.append((label, per_row / len(y) * 1000, single / len(y) * 1000))

    idx = np.arange(len(rows))
    axs[1].bar(idx - 0.2, [r[1] for r in rows], 0.4, color=p.green,
               label="per-row thresholds")
    axs[1].bar(idx + 0.2, [r[2] for r in rows], 0.4, color=p.blue,
               label="one tuned threshold")
    for i, r in enumerate(rows):
        axs[1].annotate(f"{r[1]:.1f}", (i - 0.2, r[1] + 0.4), ha="center",
                        fontsize=9, color=p.green)
        axs[1].annotate(f"{r[2]:.1f}", (i + 0.2, r[2] + 0.4), ha="center",
                        fontsize=9, color=p.blue)
    axs[1].set_xticks(idx)
    axs[1].set_xticklabels([r[0] for r in rows], fontsize=9.5)
    axs[1].set_ylim(0, max(max(r[1], r[2]) for r in rows) * 1.3)
    axs[1].set_ylabel("cost per 1,000 transactions (EUR)")
    axs[1].set_title("The gain is real but needs enough frauds to see",
                     fontsize=10.5)
    axs[1].legend(loc="upper left", fontsize=8.5)

    fig.suptitle("Per-row thresholds lose on 26 positives and win by 17.8% on "
                 "598.", fontsize=10.5, color=p.muted)


FIGURES = [
    figure("cost-versus-threshold", cost_versus_threshold, size=(8.2, 4.2)),
    figure("cost-decomposition", cost_decomposition, size=(7.8, 4.0)),
    figure("miscalibration-penalty", miscalibration_penalty, size=(8.8, 3.9),
           axes=False),
    figure("ratio-sensitivity", ratio_sensitivity, size=(8.0, 4.0)),
    figure("per-row-thresholds", per_row_thresholds, size=(8.8, 4.0), axes=False),
]
