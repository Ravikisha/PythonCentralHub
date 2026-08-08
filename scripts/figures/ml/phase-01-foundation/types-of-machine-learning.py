"""Figures for *Types of Machine Learning (Supervised, Unsupervised, Reinforcement)*."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _style import Palette, figure  # noqa: E402


def three_paradigms(fig, axes, p: Palette) -> None:
    """The same 2-D points under supervision, without it, and with a reward."""
    from sklearn.cluster import KMeans
    from sklearn.datasets import make_blobs
    from sklearn.linear_model import LogisticRegression

    X, y = make_blobs(n_samples=300, centers=3, cluster_std=1.1, random_state=8)
    axs = fig.subplots(1, 3, sharex=True, sharey=True)
    cols = [p.blue, p.amber, p.green]

    # supervised: labels given, learn the boundary
    clf = LogisticRegression(max_iter=1000).fit(X, y)
    xx, yy = np.meshgrid(np.linspace(X[:, 0].min() - 1, X[:, 0].max() + 1, 300),
                         np.linspace(X[:, 1].min() - 1, X[:, 1].max() + 1, 300))
    from matplotlib.colors import ListedColormap

    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
    axs[0].contourf(xx, yy, Z, alpha=0.13, cmap=ListedColormap(cols),
                    levels=[-0.5, 0.5, 1.5, 2.5])
    for c in range(3):
        axs[0].scatter(X[y == c, 0], X[y == c, 1], s=11, c=cols[c],
                       edgecolors="none")
    axs[0].set_title(f"Supervised\nlabels given · accuracy {clf.score(X, y):.3f}",
                     fontsize=10)

    # unsupervised: no labels, find groups
    lab = KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(X)
    from sklearn.metrics import adjusted_rand_score

    for c in range(3):
        axs[1].scatter(X[lab == c, 0], X[lab == c, 1], s=11, c=cols[c],
                       edgecolors="none")
    axs[1].set_title("Unsupervised\nno labels · ARI "
                     f"{adjusted_rand_score(y, lab):.3f}", fontsize=10)

    # reinforcement: no labels, only a reward for the trajectory taken
    rng = np.random.default_rng(0)
    axs[2].scatter(X[:, 0], X[:, 1], s=9, c=p.muted, alpha=0.35,
                   edgecolors="none")
    pos = np.array([X[:, 0].min(), X[:, 1].min()])
    goal = X.mean(axis=0)
    path = [pos.copy()]
    for _ in range(26):
        step = (goal - pos) * 0.16 + rng.normal(0, 0.55, 2)
        pos = pos + step
        path.append(pos.copy())
    path = np.array(path)
    axs[2].plot(path[:, 0], path[:, 1], "-", color=p.red, lw=1.8)
    axs[2].scatter(*path[0], s=60, marker="s", c=p.red, zorder=5)
    axs[2].scatter(*goal, s=110, marker="*", c=p.amber, zorder=5)
    axs[2].set_title("Reinforcement\nno labels · only a reward signal",
                     fontsize=10)

    for ax in axs:
        ax.set_xticks([])
        ax.set_yticks([])


def batch_vs_online(fig, axes, p: Palette) -> None:
    """Online learning tracks a shifting distribution; a frozen batch model does not."""
    from sklearn.linear_model import SGDClassifier
    from sklearn.linear_model import LogisticRegression

    rng = np.random.default_rng(0)
    n_chunks, per_chunk = 30, 200

    def chunk(i):
        """The decision boundary rotates a little more with every chunk."""
        angle = np.radians(3.2 * i)
        X = rng.normal(0, 1, (per_chunk, 2))
        w = np.array([np.cos(angle), np.sin(angle)])
        y = (X @ w > 0).astype(int)
        return X, y

    X0, y0 = chunk(0)
    batch = LogisticRegression().fit(X0, y0)
    online = SGDClassifier(loss="log_loss", random_state=0)
    online.partial_fit(X0, y0, classes=np.array([0, 1]))

    batch_scores, online_scores, xs = [], [], []
    for i in range(1, n_chunks):
        Xi, yi = chunk(i)
        batch_scores.append(batch.score(Xi, yi))
        online_scores.append(online.score(Xi, yi))   # score BEFORE updating
        online.partial_fit(Xi, yi)
        xs.append(i)

    axes.plot(xs, batch_scores, "o-", color=p.blue,
              label=f"batch model, trained once (mean {np.mean(batch_scores):.3f})")
    axes.plot(xs, online_scores, "o-", color=p.amber,
              label=f"online model, partial_fit (mean {np.mean(online_scores):.3f})")
    axes.set_xlabel("data chunk (the true boundary rotates 3.2° per chunk)")
    axes.set_ylabel("accuracy on the NEXT chunk, before seeing it")
    axes.set_title("When the world drifts, only one of these keeps up")
    axes.legend(loc="lower left")


def instance_vs_model(fig, axes, p: Palette) -> None:
    """Two ways to predict: remember the neighbours, or fit a rule."""
    from sklearn.linear_model import LinearRegression
    from sklearn.neighbors import KNeighborsRegressor

    rng = np.random.default_rng(1)
    X = rng.uniform(-2.6, 2.6, (26, 1))
    y = 0.75 * X.ravel() + rng.normal(0, 0.45, 26)
    grid = np.linspace(-3, 3, 400).reshape(-1, 1)

    lin = LinearRegression().fit(X, y)
    knn = KNeighborsRegressor(n_neighbors=3).fit(X, y)

    axes.scatter(X, y, s=34, c=p.muted, label="training data", zorder=3)
    sign = "+" if lin.intercept_ >= 0 else "−"
    axes.plot(grid, lin.predict(grid), color=p.amber, lw=2.4,
              label=f"model-based: y = {lin.coef_[0]:.3f}x {sign} "
                    f"{abs(lin.intercept_):.3f}")
    axes.plot(grid, knn.predict(grid), color=p.blue, lw=2,
              label="instance-based: 3-NN (a step function)")
    axes.set_xlabel("x")
    axes.set_ylabel("y")
    axes.set_title("Two numbers stored, or all 26 rows stored")
    axes.legend(loc="upper left", fontsize=9)


def semi_supervised(fig, axes, p: Palette) -> None:
    """What 10% of the labels buys when the geometry is informative."""
    from sklearn.datasets import make_moons
    from sklearn.linear_model import LogisticRegression
    from sklearn.semi_supervised import LabelSpreading
    from sklearn.svm import SVC

    X, y = make_moons(n_samples=600, noise=0.08, random_state=0)
    rng = np.random.default_rng(0)
    labelled = rng.choice(len(X), size=20, replace=False)
    partial = np.full(len(X), -1)
    partial[labelled] = y[labelled]

    sup_lr = LogisticRegression().fit(X[labelled], y[labelled])
    sup_svc = SVC(gamma=2.0).fit(X[labelled], y[labelled])
    ls = LabelSpreading(kernel="knn", n_neighbors=8).fit(X, partial)

    results = [
        ("Logistic\n20 labels only", sup_lr.score(X, y)),
        ("RBF SVM\n20 labels only", sup_svc.score(X, y)),
        ("Label spreading\n20 labels + 580 unlabelled", ls.score(X, y)),
    ]

    axs = fig.subplots(1, 2, gridspec_kw={"width_ratios": [1.25, 1]})
    axs[0].scatter(X[:, 0], X[:, 1], s=8, c=p.muted, alpha=0.35,
                   edgecolors="none")
    for c, col in ((0, p.blue), (1, p.amber)):
        m = labelled[y[labelled] == c]
        axs[0].scatter(X[m, 0], X[m, 1], s=70, c=col, edgecolors="black",
                       linewidths=0.6, zorder=5)
    axs[0].set_title("20 labelled points among 600", fontsize=10)
    axs[0].set_xticks([])
    axs[0].set_yticks([])

    # reverse so the first result sits at the top, keeping colour with its row
    rows = [(name, val, col) for (name, val), col
            in zip(results, (p.red, p.blue, p.green))][::-1]
    bars = axs[1].barh([r[0] for r in rows], [r[1] for r in rows],
                       color=[r[2] for r in rows])
    for b, (_, v, _) in zip(bars, rows):
        axs[1].annotate(f"{v:.4f}", (v + 0.01, b.get_y() + b.get_height() / 2),
                        va="center", fontsize=9, color=p.fg)
    axs[1].set_xlim(0, 1.18)
    axs[1].set_xlabel("accuracy on all 600 points")
    axs[1].set_title("Twenty labels are plenty — if the model\n"
                     "can express the shape", fontsize=10)


FIGURES = [
    figure("three-paradigms", three_paradigms, size=(9.0, 3.2), axes=False),
    figure("batch-vs-online", batch_vs_online, size=(7.8, 4.0)),
    figure("instance-vs-model", instance_vs_model, size=(7.4, 4.0)),
    figure("semi-supervised", semi_supervised, size=(8.6, 3.6), axes=False),
]
