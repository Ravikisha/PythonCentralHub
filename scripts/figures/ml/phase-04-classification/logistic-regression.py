"""Figures for *Logistic Regression (Binary vs Multiclass)*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import decision_surface, iris_two_features  # noqa: E402
from _style import Palette, figure  # noqa: E402


def sigmoid_and_logloss(fig, axes, p: Palette) -> None:
    """The squashing function, and the price of being confidently wrong."""
    axs = fig.subplots(1, 2)

    t = np.linspace(-8, 8, 400)
    sig = 1 / (1 + np.exp(-t))
    axs[0].plot(t, sig, color=p.blue, linewidth=2.2)
    axs[0].axhline(0.5, color=p.muted, linestyle="--", linewidth=1.1)
    axs[0].axvline(0, color=p.muted, linestyle="--", linewidth=1.1)
    axs[0].annotate("decision threshold", (-7.6, 0.53), fontsize=8.5, color=p.muted)
    axs[0].set_xlabel("logit  $t = \\mathbf{w}^\\top\\mathbf{x} + b$")
    axs[0].set_ylabel("$\\sigma(t)$  —  estimated probability")
    axs[0].set_title("The sigmoid maps any real number into (0, 1)", fontsize=10)

    q = np.linspace(0.001, 0.999, 400)
    axs[1].plot(q, -np.log(q), color=p.green, label="cost when $y = 1$")
    axs[1].plot(q, -np.log(1 - q), color=p.red, label="cost when $y = 0$")
    axs[1].set_ylim(0, 6)
    axs[1].set_xlabel("predicted probability of class 1")
    axs[1].set_ylabel("log loss")
    axs[1].set_title("Confidently wrong is punished without limit", fontsize=10)
    axs[1].legend(loc="upper center", fontsize=8.5)

    fig.suptitle("Two halves of logistic regression: the link and the loss",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def iris_boundary(fig, ax, p: Palette) -> None:
    """Softmax regression on three iris classes, two features."""
    from sklearn.linear_model import LogisticRegression

    X, y, names = iris_two_features()
    model = LogisticRegression(C=10, max_iter=1000).fit(X, y)
    decision_surface(ax, model, X, y, p)

    handles, _ = ax.get_legend_handles_labels()
    ax.legend(handles, [n.replace("_", " ") for n in names], loc="upper left", fontsize=8.5)
    ax.set_xlabel("petal length (cm)")
    ax.set_ylabel("petal width (cm)")
    ax.set_title(f"Softmax regression, three classes — training accuracy {model.score(X, y):.2f}")


def threshold_sweep(fig, ax, p: Palette) -> None:
    """Moving the threshold trades precision against recall, continuously."""
    from sklearn.datasets import load_breast_cancer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import precision_score, recall_score, f1_score
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X, y = load_breast_cancer(return_X_y=True)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0,
                                              stratify=y)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000))
    model.fit(X_tr, y_tr)
    proba = model.predict_proba(X_te)[:, 1]

    thresholds = np.linspace(0.02, 0.98, 97)
    prec, rec, f1s = [], [], []
    for t in thresholds:
        pred = (proba >= t).astype(int)
        prec.append(precision_score(y_te, pred, zero_division=1))
        rec.append(recall_score(y_te, pred, zero_division=0))
        f1s.append(f1_score(y_te, pred, zero_division=0))

    ax.plot(thresholds, prec, color=p.blue, label="precision")
    ax.plot(thresholds, rec, color=p.amber, label="recall")
    ax.plot(thresholds, f1s, color=p.green, linestyle="--", label="F1")
    ax.axvline(0.5, color=p.muted, linestyle=":", linewidth=1.3,
               label="default threshold 0.5")

    ax.set_xlabel("decision threshold")
    ax.set_ylabel("score")
    ax.set_ylim(0, 1.03)
    ax.set_title("The threshold is a free parameter you are choosing whether you know it or not")
    ax.legend(loc="lower center", fontsize=8.5, ncol=2)


FIGURES = [
    figure("sigmoid-and-logloss", sigmoid_and_logloss, size=(8.6, 3.8), axes=False),
    figure("iris-boundary", iris_boundary, size=(7.4, 4.8)),
    figure("threshold-sweep", threshold_sweep, size=(8.0, 4.4)),
]
