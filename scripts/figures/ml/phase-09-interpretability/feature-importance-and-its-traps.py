"""Figures for *Feature Importance and Its Traps*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import duplicated_feature, noisy_signal  # noqa: E402
from _style import Palette, figure  # noqa: E402


def impurity_vs_permutation(fig, axes, p: Palette) -> None:
    """Three importance methods on one model. Two of them rank noise first."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.inspection import permutation_importance
    from sklearn.model_selection import train_test_split

    X, y = noisy_signal()
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3,
                                              random_state=0, stratify=y)
    model = RandomForestClassifier(n_estimators=300, random_state=0).fit(X_tr, y_tr)

    impurity = model.feature_importances_
    perm_tr = permutation_importance(model, X_tr, y_tr, n_repeats=30,
                                     random_state=0)
    perm_te = permutation_importance(model, X_te, y_te, n_repeats=30,
                                     random_state=0)

    panels = [
        ("Impurity", impurity, None),
        ("Permutation, TRAIN", perm_tr.importances_mean, perm_tr.importances_std),
        ("Permutation, TEST", perm_te.importances_mean, perm_te.importances_std),
    ]
    axs = fig.subplots(1, 3)
    names = list(X.columns)
    noise_idx = {names.index("random_continuous"), names.index("random_binary")}

    ci = names.index("random_continuous")
    for ax, (title, values, err) in zip(axs, panels):
        order = np.argsort(values)
        cols = [p.red if i in noise_idx else p.blue for i in order]
        ax.barh(range(len(order)), values[order], color=cols,
                xerr=None if err is None else err[order],
                error_kw={"ecolor": p.muted, "elinewidth": 1})
        ax.set_yticks(range(len(order)))
        ax.set_yticklabels([names[i] for i in order], fontsize=8.5)

        # Judge the method by what it says about the pure-noise column, not by
        # whether it happened to get the top feature right.
        rank = int((values > values[ci]).sum()) + 1
        ax.set_title(f"{title}\nnoise: {values[ci]:+.4f}  (rank {rank}/5)",
                     fontsize=10)
        ax.axvline(0, color=p.muted, lw=1)

    fig.suptitle(f"Same forest, train accuracy "
                 f"{model.score(X_tr, y_tr):.4f}, test accuracy "
                 f"{model.score(X_te, y_te):.4f} — red bars are pure noise",
                 fontsize=10, color=p.muted)


def correlated_credit_split(fig, axes, p: Palette) -> None:
    """Two near-duplicate columns each look half as important as they are."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.inspection import permutation_importance
    from sklearn.model_selection import train_test_split

    X, y = duplicated_feature()
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3,
                                              random_state=0, stratify=y)
    with_dup = RandomForestClassifier(n_estimators=300,
                                      random_state=0).fit(X_tr, y_tr)
    imp_with = permutation_importance(with_dup, X_te, y_te, n_repeats=30,
                                      random_state=0).importances_mean

    X2 = X.drop(columns=["income_copy"])
    X2_tr, X2_te, _, _ = train_test_split(X2, y, test_size=0.3, random_state=0,
                                          stratify=y)
    without = RandomForestClassifier(n_estimators=300,
                                     random_state=0).fit(X2_tr, y_tr)
    imp_without = permutation_importance(without, X2_te, y_te, n_repeats=30,
                                         random_state=0).importances_mean

    axs = fig.subplots(1, 2, sharex=True)
    names = list(X.columns)
    axs[0].barh(names[::-1], imp_with[::-1],
                color=[p.blue, p.amber, p.blue][::-1])
    for i, (nm, v) in enumerate(zip(names[::-1], imp_with[::-1])):
        axs[0].annotate(f"{v:+.4f}", (v + 0.008, i), va="center", fontsize=9,
                        color=p.fg)
    axs[0].set_title("Both columns present", fontsize=11)

    names2 = list(X2.columns)
    axs[1].barh(names2[::-1], imp_without[::-1], color=[p.blue, p.green][::-1])
    for i, (nm, v) in enumerate(zip(names2[::-1], imp_without[::-1])):
        axs[1].annotate(f"{v:+.4f}", (v + 0.008, i), va="center", fontsize=9,
                        color=p.fg)
    axs[1].set_title("income_copy dropped", fontsize=11)

    for ax in axs:
        ax.set_xlim(0, max(imp_without.max(), imp_with.max()) * 1.35)
        ax.set_xlabel("permutation importance")

    total = imp_with[0] + imp_with[1]
    fig.suptitle(f"Split credit: {imp_with[0]:.4f} + {imp_with[1]:.4f} = "
                 f"{total:.4f}, and income alone scores {imp_without[0]:.4f}",
                 fontsize=10, color=p.muted)


FIGURES = [
    figure("impurity-vs-permutation", impurity_vs_permutation, size=(9.4, 3.6),
           axes=False),
    figure("correlated-credit-split", correlated_credit_split, size=(8.8, 3.2),
           axes=False),
]
