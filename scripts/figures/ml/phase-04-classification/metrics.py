"""Figures shared by the four evaluation pages of Phase 04.

Confusion matrix, precision/recall trade-off, ROC and PR curves all come from one
fitted model so the numbers on those pages agree with each other exactly.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _style import Palette, figure  # noqa: E402


def _cancer_model():
    """Logistic regression on breast cancer, with class 1 = malignant.

    sklearn ships this dataset with 0 = malignant, which makes every metric read
    backwards on a page about catching disease. Flipping it once here keeps the
    prose honest: the positive class is the one you are trying to catch.
    """
    from sklearn.datasets import load_breast_cancer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X, y = load_breast_cancer(return_X_y=True)
    y = 1 - y                       # 1 = malignant
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.3, random_state=0, stratify=y
    )
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000))
    model.fit(X_tr, y_tr)
    return model, X_te, y_te, model.predict_proba(X_te)[:, 1]


def _draw_matrix(ax, matrix, labels, p: Palette, title, cmap_color):
    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list("pch", [p.bg, cmap_color])
    ax.imshow(matrix, cmap=cmap, vmin=0, vmax=matrix.max())
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.set_xlabel("predicted")
    ax.set_ylabel("actual")
    ax.set_title(title, fontsize=10)
    ax.grid(False)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            value = matrix[i, j]
            ax.annotate(f"{value}", (j, i), ha="center", va="center",
                        color=p.bg if value > matrix.max() * 0.55 else p.fg,
                        fontsize=11, fontweight="bold")


def confusion_matrices(fig, axes, p: Palette) -> None:
    """The binary matrix with its four named cells, beside a 10-class one."""
    from sklearn.datasets import load_digits
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import confusion_matrix
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    axs = fig.subplots(1, 2, width_ratios=[1, 1.25])

    _, _, y_te, proba = _cancer_model()
    cm = confusion_matrix(y_te, (proba >= 0.5).astype(int))
    _draw_matrix(axs[0], cm, ["benign", "malignant"], p,
                 "Binary: TN, FP on top; FN, TP below", p.blue)
    for (i, j), name in {(0, 0): "TN", (0, 1): "FP", (1, 0): "FN", (1, 1): "TP"}.items():
        axs[0].annotate(name, (j, i - 0.28), ha="center", va="center",
                        color=p.amber, fontsize=9, fontweight="bold")

    digits = load_digits()
    X_tr, X_te, y_tr, y_te2 = train_test_split(
        digits.data, digits.target, test_size=0.3, random_state=0, stratify=digits.target
    )
    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000)).fit(X_tr, y_tr)
    cm10 = confusion_matrix(y_te2, clf.predict(X_te))
    _draw_matrix(axs[1], cm10, list(range(10)), p,
                 f"Ten classes — accuracy {clf.score(X_te, y_te2):.3f}", p.green)
    for label in axs[1].texts:
        label.set_fontsize(6.5)

    fig.suptitle("Every classification metric is a ratio of cells in this table",
                 fontsize=11.5, fontweight="bold", color=p.fg)


def precision_recall_tradeoff(fig, axes, p: Palette) -> None:
    """Scores against threshold, and the resulting precision-recall curve."""
    from sklearn.metrics import precision_recall_curve, average_precision_score

    _, _, y_te, proba = _cancer_model()
    precision, recall, thresholds = precision_recall_curve(y_te, proba)

    axs = fig.subplots(1, 2)
    axs[0].plot(thresholds, precision[:-1], color=p.blue, label="precision")
    axs[0].plot(thresholds, recall[:-1], color=p.amber, label="recall")
    axs[0].axvline(0.5, color=p.muted, linestyle=":", linewidth=1.3, label="threshold 0.5")
    axs[0].set_xlabel("decision threshold")
    axs[0].set_ylabel("score")
    axs[0].set_ylim(0, 1.03)
    axs[0].set_title("Raise the threshold: precision up, recall down", fontsize=10)
    axs[0].legend(loc="lower center", fontsize=8.5)

    ap = average_precision_score(y_te, proba)
    axs[1].plot(recall, precision, color=p.green, linewidth=2.0)
    axs[1].fill_between(recall, precision, alpha=0.14, color=p.green)
    axs[1].axhline((y_te == 1).mean(), color=p.muted, linestyle="--", linewidth=1.2,
                   label=f"baseline = positive rate {(y_te == 1).mean():.2f}")
    axs[1].set_xlabel("recall")
    axs[1].set_ylabel("precision")
    axs[1].set_ylim(0, 1.03)
    axs[1].set_title(f"Precision-recall curve  ·  AP = {ap:.3f}", fontsize=10)
    axs[1].legend(loc="lower left", fontsize=8.5)

    fig.suptitle("One model, one set of scores, one dial", fontsize=11.5,
                 fontweight="bold", color=p.fg)


def roc_curves(fig, axes, p: Palette) -> None:
    """ROC for three models, and why ROC flatters a model on imbalanced data."""
    from sklearn.datasets import load_breast_cancer
    from sklearn.dummy import DummyClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (average_precision_score, precision_recall_curve,
                                 roc_auc_score, roc_curve)
    from sklearn.model_selection import train_test_split
    from sklearn.naive_bayes import GaussianNB
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    axs = fig.subplots(1, 2)

    X, y = load_breast_cancer(return_X_y=True)
    y = 1 - y
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=0,
                                              stratify=y)
    models = [
        ("Logistic Regression", make_pipeline(StandardScaler(),
                                              LogisticRegression(max_iter=5000)), p.blue),
        ("Gaussian Naive Bayes", GaussianNB(), p.amber),
        ("Always 'benign'", DummyClassifier(strategy="stratified", random_state=0), p.red),
    ]
    for name, model, color in models:
        model.fit(X_tr, y_tr)
        scores = model.predict_proba(X_te)[:, 1]
        fpr, tpr, _ = roc_curve(y_te, scores)
        axs[0].plot(fpr, tpr, color=color,
                    label=f"{name}  ·  AUC {roc_auc_score(y_te, scores):.3f}")
    axs[0].plot([0, 1], [0, 1], color=p.muted, linestyle="--", linewidth=1.2)
    axs[0].set_xlabel("false positive rate")
    axs[0].set_ylabel("true positive rate (recall)")
    axs[0].set_title("ROC: three models on a balanced-ish problem", fontsize=10)
    axs[0].legend(loc="lower right", fontsize=8)

    # Severe imbalance: ROC stays optimistic while PR collapses
    rng = np.random.default_rng(2)
    n = 4000
    y_imb = (rng.random(n) < 0.01).astype(int)
    scores_imb = rng.normal(loc=y_imb * 1.6, scale=1.0)
    fpr, tpr, _ = roc_curve(y_imb, scores_imb)
    prec, rec, _ = precision_recall_curve(y_imb, scores_imb)

    axs[1].plot(fpr, tpr, color=p.blue,
                label=f"ROC  ·  AUC {roc_auc_score(y_imb, scores_imb):.3f}")
    axs[1].plot(rec, prec, color=p.amber,
                label=f"PR  ·  AP {average_precision_score(y_imb, scores_imb):.3f}")
    axs[1].plot([0, 1], [0, 1], color=p.muted, linestyle="--", linewidth=1.1)
    axs[1].set_xlabel("FPR (ROC)  /  recall (PR)")
    axs[1].set_ylabel("TPR (ROC)  /  precision (PR)")
    axs[1].set_ylim(0, 1.03)
    axs[1].set_title("At a 1% positive rate, the same model looks\ngreat by ROC and poor by PR",
                     fontsize=10)
    axs[1].legend(loc="upper right", fontsize=8)

    fig.suptitle("ROC answers 'can it rank?'; PR answers 'is a positive prediction worth anything?'",
                 fontsize=11.5, fontweight="bold", color=p.fg)


FIGURES = [
    figure("confusion-matrices", confusion_matrices, size=(9.0, 4.2), axes=False),
    figure("precision-recall-tradeoff", precision_recall_tradeoff, size=(8.8, 4.0), axes=False),
    figure("roc-curves", roc_curves, size=(9.0, 4.2), axes=False),
]
