"""Figures for *The Power of Ensembles* and *Stacking and Voting*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _style import Palette, figure  # noqa: E402


def condorcet(fig, ax, p: Palette) -> None:
    """Majority vote accuracy against ensemble size, for several member accuracies."""
    from scipy.stats import binom

    sizes = np.arange(1, 102, 2)
    for member_acc, color in ((0.45, p.red), (0.51, p.amber),
                              (0.60, p.blue), (0.70, p.green)):
        # P(more than half correct)
        acc = [1 - binom.cdf(n // 2, n, member_acc) for n in sizes]
        ax.plot(sizes, acc, color=color, label=f"each member {member_acc:.2f}")

    ax.axhline(0.5, color=p.muted, linestyle="--", linewidth=1.2)
    ax.set_xlabel("number of independent voters")
    ax.set_ylabel("majority-vote accuracy")
    ax.set_ylim(0, 1.02)
    ax.set_title("Condorcet: 51% voters reach 84% by 101 of them — if they are independent")
    ax.legend(loc="center right", fontsize=8.5)


def correlation_penalty(fig, ax, p: Palette) -> None:
    """The variance of an average, as a function of how correlated the members are."""
    n_values = [5, 20, 100]
    rho = np.linspace(0, 1, 200)

    for n, color in zip(n_values, (p.blue, p.amber, p.green)):
        variance = rho + (1 - rho) / n          # in units of a single model's variance
        ax.plot(rho, variance, color=color, label=f"{n} models")

    ax.axhline(1.0, color=p.muted, linestyle="--", linewidth=1.2,
               label="a single model")
    ax.annotate("correlation puts a floor\nunder the variance", (0.55, 0.62),
                fontsize=9, color=p.fg)

    ax.set_xlabel("average pairwise correlation between members")
    ax.set_ylabel("ensemble variance (single model = 1)")
    ax.set_ylim(0, 1.08)
    ax.set_title("Averaging only helps to the extent the members disagree")
    ax.legend(loc="lower right", fontsize=8.5)


def diverse_boundaries(fig, axes, p: Palette) -> None:
    """Three different model families, and what their vote looks like."""
    from sklearn.datasets import make_moons
    from sklearn.ensemble import VotingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import GaussianNB
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.tree import DecisionTreeClassifier

    X, y = make_moons(n_samples=300, noise=0.3, random_state=1)
    members = [
        ("logistic", make_pipeline(StandardScaler(), LogisticRegression())),
        ("tree", DecisionTreeClassifier(max_depth=4, random_state=0)),
        ("naive bayes", GaussianNB()),
    ]
    ensemble = VotingClassifier(members, voting="soft")

    axs = fig.subplots(1, 4, sharey=True)
    pad = 0.6
    xx, yy = np.meshgrid(
        np.linspace(X[:, 0].min() - pad, X[:, 0].max() + pad, 260),
        np.linspace(X[:, 1].min() - pad, X[:, 1].max() + pad, 260),
    )
    grid = np.c_[xx.ravel(), yy.ravel()]

    for ax, (name, model) in zip(axs, members + [("soft vote", ensemble)]):
        model.fit(X, y)
        zz = model.predict(grid).reshape(xx.shape)
        ax.contourf(xx, yy, zz, levels=1, colors=[p.blue, p.amber], alpha=0.22)
        ax.contour(xx, yy, zz, levels=1, colors=[p.fg], linewidths=1.1)
        ax.scatter(X[y == 0, 0], X[y == 0, 1], color=p.blue, s=10, edgecolor="none")
        ax.scatter(X[y == 1, 0], X[y == 1, 1], color=p.amber, s=10, edgecolor="none")
        ax.set_title(f"{name}\n{model.score(X, y):.3f}", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("Three mediocre and dissimilar models, and the boundary they agree on",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def voting_and_stacking(fig, ax, p: Palette) -> None:
    """Members against hard vote, soft vote and a stacked blender."""
    from sklearn.datasets import make_moons
    from sklearn.ensemble import StackingClassifier, VotingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.naive_bayes import GaussianNB
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.tree import DecisionTreeClassifier

    X, y = make_moons(n_samples=500, noise=0.3, random_state=1)
    members = [
        ("logistic", make_pipeline(StandardScaler(), LogisticRegression())),
        ("tree", DecisionTreeClassifier(max_depth=4, random_state=0)),
        ("knn", make_pipeline(StandardScaler(), KNeighborsClassifier(15))),
        ("nb", GaussianNB()),
    ]

    names, scores, colors = [], [], []
    for name, model in members:
        names.append(name)
        scores.append(cross_val_score(model, X, y, cv=5).mean())
        colors.append(p.muted)

    for label, model, color in [
        ("hard vote", VotingClassifier(members, voting="hard"), p.blue),
        ("soft vote", VotingClassifier(members, voting="soft"), p.green),
        ("stacking", StackingClassifier(members, final_estimator=LogisticRegression(),
                                        cv=5), p.amber),
    ]:
        names.append(label)
        scores.append(cross_val_score(model, X, y, cv=5).mean())
        colors.append(color)

    bars = ax.bar(names, scores, color=colors, width=0.62)
    best_member = max(scores[:4])
    ax.axhline(best_member, color=p.red, linestyle="--", linewidth=1.4,
               label=f"best single member {best_member:.4f}")
    for bar, v in zip(bars, scores):
        ax.annotate(f"{v:.4f}", (bar.get_x() + bar.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8)

    ax.set_ylim(min(scores) - 0.02, max(scores) + 0.015)
    ax.set_ylabel("5-fold CV accuracy")
    ax.set_title("Four members and three ways of combining them")
    ax.legend(loc="lower right", fontsize=8.5)


FIGURES = [
    figure("condorcet", condorcet, size=(8.2, 4.4)),
    figure("correlation-penalty", correlation_penalty, size=(8.2, 4.4)),
    figure("diverse-boundaries", diverse_boundaries, size=(9.4, 3.2), axes=False),
    figure("voting-and-stacking", voting_and_stacking, size=(8.4, 4.6)),
]
