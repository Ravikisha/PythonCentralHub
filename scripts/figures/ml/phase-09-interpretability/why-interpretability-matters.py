"""Figures for *Why Interpretability Matters*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import two_sites  # noqa: E402
from _style import Palette, figure  # noqa: E402


def accuracy_versus_transparency(fig, axes, p: Palette) -> None:
    """The trade-off is real but much smaller than its reputation.

    Accuracy is measured; the "parameters you can read" count is a property of
    each fitted model (coefficients, or nodes across the whole ensemble).
    """
    from sklearn.datasets import load_breast_cancer
    from sklearn.ensemble import (HistGradientBoostingClassifier,
                                  RandomForestClassifier)
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.tree import DecisionTreeClassifier

    X, y = load_breast_cancer(return_X_y=True)

    def tree_nodes(est):
        return int(est.tree_.node_count)

    def forest_nodes(est):
        return int(sum(t.tree_.node_count for t in est.estimators_))

    specs = [
        ("depth-2 tree", DecisionTreeClassifier(max_depth=2, random_state=0),
         tree_nodes),
        ("logistic\nregression",
         make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000)),
         lambda est: int(est[-1].coef_.size + 1)),
        ("depth-5 tree", DecisionTreeClassifier(max_depth=5, random_state=0),
         tree_nodes),
        ("random forest\n300 trees",
         RandomForestClassifier(n_estimators=300, random_state=0), forest_nodes),
        ("gradient\nboosting", HistGradientBoostingClassifier(random_state=0),
         None),
    ]

    names, accs, sizes = [], [], []
    for name, est, counter in specs:
        accs.append(cross_val_score(est, X, y, cv=5).mean())
        est.fit(X, y)
        names.append(name)
        sizes.append(counter(est) if counter else None)

    axs = fig.subplots(1, 2)

    cols = [p.green, p.green, p.amber, p.red, p.red]
    bars = axs[0].bar(range(len(names)), accs, color=cols)
    for b, v in zip(bars, accs):
        axs[0].annotate(f"{v:.4f}", (b.get_x() + b.get_width() / 2, v + 0.004),
                        ha="center", fontsize=9, color=p.muted)
    axs[0].set_xticks(range(len(names)))
    axs[0].set_xticklabels([n.replace("\n", " ") for n in names], fontsize=8,
                           rotation=24, ha="right")
    axs[0].set_ylim(0.85, 1.0)
    axs[0].set_ylabel("5-fold accuracy")
    spread = max(accs) - min(accs)
    axs[0].set_title(f"Accuracy spread: {spread:.4f}", fontsize=10.5)

    known = [(n, s, c) for n, s, c in zip(names, sizes, cols) if s is not None]
    axs[1].bar(range(len(known)), [s for _, s, _ in known],
               color=[c for _, _, c in known])
    for i, (_, s, _) in enumerate(known):
        axs[1].annotate(f"{s:,}", (i, s * 1.5), ha="center", fontsize=9,
                        color=p.muted)
    axs[1].set_xticks(range(len(known)))
    axs[1].set_xticklabels([n.replace("\n", " ") for n, _, _ in known],
                           fontsize=8, rotation=24, ha="right")
    axs[1].set_yscale("log")
    axs[1].set_ylim(1, max(s for _, s, _ in known) * 8)
    axs[1].set_ylabel("numbers you would have to read (log scale)")
    ratio = max(s for _, s, _ in known) / min(s for _, s, _ in known)
    axs[1].set_title(f"Transparency spread: {ratio:,.0f}x", fontsize=10.5)

    fig.suptitle(f"Accuracy varies by {spread:.4f}. How much you have to read "
                 f"varies by {ratio:,.0f}x.", fontsize=10.5, color=p.muted)


def global_versus_local(fig, axes, p: Palette) -> None:
    """Two different questions, and one cannot be derived from the other."""
    axes.axis("off")
    from matplotlib.patches import FancyBboxPatch

    boxes = [
        (0.03, 0.52, 0.44, "GLOBAL", p.blue,
         "How does the model behave\nin general?",
         "• permutation importance\n• partial dependence\n• mean |SHAP|",
         "Audits, documentation,\nfeature selection"),
        (0.53, 0.52, 0.44, "LOCAL", p.amber,
         "Why THIS row got THIS answer?",
         "• SHAP for one row\n• LIME\n• counterfactuals",
         "Appeals, debugging,\nregulated decisions"),
    ]
    for x0, y0, w, title, col, question, tools, use in boxes:
        axes.add_patch(FancyBboxPatch((x0, y0 - 0.42), w, 0.86,
                                      boxstyle="round,pad=0.012",
                                      facecolor=col, alpha=0.14,
                                      edgecolor=col, lw=2))
        axes.annotate(title, (x0 + w / 2, y0 + 0.34), ha="center", fontsize=12,
                      fontweight="bold", color=col)
        axes.annotate(question, (x0 + w / 2, y0 + 0.19), ha="center", fontsize=9.5,
                      color=p.fg)
        axes.annotate(tools, (x0 + 0.03, y0 - 0.02), fontsize=9, color=p.muted,
                      va="top")
        axes.annotate(use, (x0 + w / 2, y0 - 0.30), ha="center", fontsize=9,
                      color=col, style="italic")

    axes.annotate("A feature can be globally unimportant and decisive for one "
                  "individual.\nAveraging local explanations gives you the "
                  "global picture; the reverse is impossible.",
                  (0.5, 0.03), ha="center", fontsize=9.5, color=p.fg)
    axes.set_xlim(0, 1)
    axes.set_ylim(-0.02, 1.0)
    axes.set_title("Two questions interpretability answers")


def shortcut_feature(fig, axes, p: Palette) -> None:
    """A model that is 0.96 accurate for a reason that does not survive a move."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.inspection import permutation_importance
    from sklearn.model_selection import train_test_split

    X_a, y_a, X_b, y_b = two_sites()
    X_tr, X_te, y_tr, y_te = train_test_split(X_a, y_a, test_size=0.3,
                                              random_state=0)

    def forest():
        return RandomForestClassifier(n_estimators=300, min_samples_leaf=50,
                                      random_state=0)

    full = forest().fit(X_tr, y_tr)
    honest = forest().fit(X_tr[["marker"]], y_tr)

    axs = fig.subplots(1, 2)

    scores = [
        ("both features", full.score(X_te, y_te), full.score(X_b, y_b)),
        ("marker only", honest.score(X_te[["marker"]], y_te),
         honest.score(X_b[["marker"]], y_b)),
    ]
    idx = np.arange(len(scores))
    axs[0].bar(idx - 0.2, [s[1] for s in scores], 0.4, color=p.blue,
               label="training site, held out")
    axs[0].bar(idx + 0.2, [s[2] for s in scores], 0.4, color=p.amber,
               label="new site")
    for i, (_, a, b) in enumerate(scores):
        axs[0].annotate(f"{a:.4f}", (i - 0.2, a + 0.015), ha="center",
                        fontsize=9, color=p.blue)
        axs[0].annotate(f"{b:.4f}", (i + 0.2, b + 0.015), ha="center",
                        fontsize=9, color=p.amber)
    axs[0].axhline(0.5, color=p.red, lw=1.2, ls="--", label="coin flip")
    axs[0].set_xticks(idx)
    axs[0].set_xticklabels([s[0] for s in scores], fontsize=9.5)
    axs[0].set_ylim(0, 1.32)
    axs[0].set_ylabel("accuracy")
    axs[0].set_title("The worse model is the one that transfers", fontsize=10.5)
    axs[0].legend(loc="upper center", ncol=3, fontsize=8.5)

    pi = permutation_importance(full, X_te, y_te, n_repeats=30, random_state=0)
    order = np.argsort(pi.importances_mean)
    names = [X_a.columns[i] for i in order]
    axs[1].barh(range(len(names)), pi.importances_mean[order], height=0.42,
                xerr=pi.importances_std[order],
                color=[p.red if n == "scanner_id" else p.green for n in names],
                error_kw={"ecolor": p.muted, "lw": 1})
    for i, v in enumerate(pi.importances_mean[order]):
        axs[1].annotate(f"{v:+.4f}", (v + 0.015, i), va="center", fontsize=9,
                        color=p.muted)
    axs[1].set_yticks(range(len(names)))
    axs[1].set_yticklabels(names, fontsize=9.5)
    axs[1].set_ylim(-0.6, 1.6)
    axs[1].set_xlim(0, 0.62)
    axs[1].set_xlabel("drop in accuracy when shuffled")
    axs[1].set_title("One question would have caught it", fontsize=10.5)

    fig.suptitle("Accuracy said the model was ready. Importance said what it "
                 "was reading.", fontsize=10.5, color=p.muted)


FIGURES = [
    figure("accuracy-versus-transparency", accuracy_versus_transparency,
           size=(8.8, 3.8), axes=False),
    figure("shortcut-feature", shortcut_feature, size=(8.8, 3.8), axes=False),
    figure("global-versus-local", global_versus_local, size=(8.6, 3.4)),
]
