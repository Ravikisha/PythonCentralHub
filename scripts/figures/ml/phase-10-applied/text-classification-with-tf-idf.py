"""Figures for *Text Classification with TF-IDF*."""

import functools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _data import support_tickets  # noqa: E402
from _style import Palette, figure  # noqa: E402


@functools.lru_cache(maxsize=1)
def setup():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split

    docs, y, names = support_tickets()
    d_tr, d_te, y_tr, y_te = train_test_split(docs, y, test_size=0.3,
                                              random_state=0, stratify=y)
    tfidf = TfidfVectorizer()
    X_tr = tfidf.fit_transform(d_tr)
    X_te = tfidf.transform(d_te)
    model = LogisticRegression(max_iter=2000).fit(X_tr, y_tr)
    return {"d_tr": d_tr, "d_te": d_te, "y_tr": y_tr, "y_te": y_te,
            "names": names, "tfidf": tfidf, "X_tr": X_tr, "X_te": X_te,
            "model": model, "vocab": tfidf.get_feature_names_out()}


def sparse_matrix(fig, axes, p: Palette) -> None:
    """What a document-term matrix actually looks like."""
    d = setup()
    X = d["X_tr"]
    rows, cols = 60, 120
    block = X[:rows, :cols].toarray()

    axs = fig.subplots(1, 2, width_ratios=[1.5, 1])

    axs[0].imshow(block > 0, cmap="Blues", aspect="auto", vmin=0, vmax=1.4)
    axs[0].set_xlabel("first 120 vocabulary columns")
    axs[0].set_ylabel("first 60 documents")
    filled = float((block > 0).mean())
    axs[0].grid(False)
    axs[0].set_title(f"A 60x120 corner: {filled:.1%} of cells are non-zero",
                     fontsize=10.5)

    cells = X.shape[0] * X.shape[1]
    ident = sum(1 for w in d["vocab"] if w.startswith("case"))
    df = np.asarray((X > 0).sum(axis=0)).ravel()

    facts = [
        ("documents", f"{X.shape[0]:,}"),
        ("vocabulary", f"{X.shape[1]:,}"),
        ("of which identifiers", f"{ident:,}"),
        ("real words", f"{X.shape[1] - ident:,}"),
        ("cells", f"{cells:,}"),
        ("non-zero cells", f"{X.nnz:,}"),
        ("sparsity", f"{100 * (1 - X.nnz / cells):.2f}%"),
        ("tokens in exactly 1 doc", f"{int((df == 1).sum()):,} "
                                    f"({(df == 1).mean():.1%})"),
    ]
    axes_off = axs[1]
    axes_off.axis("off")
    for i, (label, value) in enumerate(facts):
        yy = 0.94 - i * 0.115
        axes_off.annotate(label, (0.02, yy), fontsize=10, color=p.muted)
        axes_off.annotate(value, (0.98, yy), fontsize=10.5, color=p.fg,
                          ha="right", fontweight="bold")
    axes_off.set_xlim(0, 1)
    axes_off.set_ylim(0, 1)
    axes_off.set_title("The matrix in numbers", fontsize=10.5)

    fig.suptitle("6,000 tickets of about 22 words each produce a 2,447-column "
                 "matrix that is 99.17% zeros.", fontsize=10.5, color=p.muted)


def idf_and_zipf(fig, axes, p: Palette) -> None:
    """Document frequency falls like a power law; idf is its mirror."""
    d = setup()
    X, vocab, tfidf = d["X_tr"], d["vocab"], d["tfidf"]
    df = np.asarray((X > 0).sum(axis=0)).ravel()
    order = np.argsort(df)[::-1]

    axs = fig.subplots(1, 2)

    axs[0].plot(np.arange(1, len(df) + 1), df[order], color=p.blue, lw=1.8)
    axs[0].set_xscale("log")
    axs[0].set_yscale("log")
    axs[0].set_xlabel("token rank (log)")
    axs[0].set_ylabel("documents containing it (log)")
    axs[0].set_title("Document frequency, ranked", fontsize=10.5)
    for word, colour, offset in (("case00000", p.red, (12, 6)),
                                 ("my", p.amber, (14, -8)),
                                 ("refund", p.green, (12, 8))):
        idx = int(np.flatnonzero(vocab == word)[0])
        rank = int(np.flatnonzero(order == idx)[0]) + 1
        axs[0].scatter([rank], [df[idx]], color=colour, s=55, zorder=5)
        axs[0].annotate(f"{word}  df {df[idx]}", (rank, df[idx]),
                        textcoords="offset points", xytext=offset,
                        fontsize=9, color=colour)

    picks = ["my", "the", "ref_bill", "charge", "refund", "error", "case00000"]
    idfs = [(w, float(tfidf.idf_[tfidf.vocabulary_[w]])) for w in picks]
    idfs.sort(key=lambda t: t[1])
    idx = np.arange(len(idfs))
    axs[1].barh(idx, [v for _, v in idfs], color=p.purple, height=0.55)
    for i, (w, v) in enumerate(idfs):
        axs[1].annotate(f"{v:.4f}", (v + 0.06, i), va="center", fontsize=9,
                        color=p.muted)
    axs[1].set_yticks(idx)
    axs[1].set_yticklabels([w for w, _ in idfs], fontsize=9.5)
    axs[1].set_xlim(0, max(v for _, v in idfs) * 1.22)
    axs[1].set_xlabel("idf = log((1+n)/(1+df)) + 1")
    axs[1].set_title("Rare tokens get the loud weights", fontsize=10.5)

    fig.suptitle("43% of the vocabulary appears in exactly one document, and idf "
                 "hands those tokens the largest weights.",
                 fontsize=10.5, color=p.muted)


def model_comparison(fig, axes, p: Palette) -> None:
    """Sparse linear models win; dense pipelines do not."""
    from sklearn.decomposition import TruncatedSVD
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score
    from sklearn.naive_bayes import ComplementNB, MultinomialNB
    from sklearn.svm import LinearSVC

    d = setup()
    X_tr, X_te, y_tr, y_te = d["X_tr"], d["X_te"], d["y_tr"], d["y_te"]

    results = []
    for name, clf in (("multinomial NB", MultinomialNB()),
                      ("complement NB", ComplementNB()),
                      ("logistic (tf-idf)", LogisticRegression(max_iter=2000)),
                      ("linear SVC", LinearSVC())):
        clf.fit(X_tr, y_tr)
        results.append((name, accuracy_score(y_te, clf.predict(X_te)), p.blue))

    counts = CountVectorizer()
    A, B = counts.fit_transform(d["d_tr"]), counts.transform(d["d_te"])
    clf = LogisticRegression(max_iter=2000).fit(A, y_tr)
    results.append(("logistic (raw counts)",
                    accuracy_score(y_te, clf.predict(B)), p.muted))

    svd = TruncatedSVD(n_components=120, random_state=0)
    Z, Zt = svd.fit_transform(X_tr), svd.transform(X_te)
    results.append(("SVD-120 + logistic",
                    accuracy_score(y_te, LogisticRegression(max_iter=3000)
                                   .fit(Z, y_tr).predict(Zt)), p.amber))
    results.append(("SVD-120 + boosting",
                    accuracy_score(y_te, HistGradientBoostingClassifier(
                        random_state=0).fit(Z, y_tr).predict(Zt)), p.red))

    results.sort(key=lambda r: r[1])
    idx = np.arange(len(results))
    axes.barh(idx, [r[1] for r in results], color=[r[2] for r in results],
              height=0.6)
    for i, r in enumerate(results):
        axes.annotate(f"{r[1]:.4f}", (r[1] + 0.004, i), va="center", fontsize=9.5,
                      color=p.muted)
    axes.set_yticks(idx)
    axes.set_yticklabels([r[0] for r in results], fontsize=9.5)
    axes.set_xlim(0.75, max(r[1] for r in results) + 0.03)
    axes.set_xlabel("test accuracy")
    axes.set_title("Naive Bayes on tf-idf beats a 120-component boosting "
                   "pipeline by 0.06")


def min_df_pruning(fig, axes, p: Palette) -> None:
    """Most of a text vocabulary is dead weight."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score

    d = setup()
    rows = []
    for min_df in (1, 2, 3, 5, 10, 20, 50):
        vec = TfidfVectorizer(min_df=min_df)
        A = vec.fit_transform(d["d_tr"])
        B = vec.transform(d["d_te"])
        model = LogisticRegression(max_iter=2000).fit(A, d["y_tr"])
        rows.append((min_df, A.shape[1],
                     accuracy_score(d["y_te"], model.predict(B))))

    sizes = [r[1] for r in rows]
    accs = [r[2] for r in rows]

    axes.plot(sizes, accs, "o-", color=p.blue, lw=2.2)
    for min_df, size, acc in rows:
        axes.annotate(f"min_df={min_df}\n{size:,} features\n{acc:.4f}",
                      (size, acc), textcoords="offset points",
                      xytext=(0, 14 if min_df in (1, 3, 10, 50) else -34),
                      ha="center", fontsize=8.5, color=p.muted)
    axes.set_xscale("log")
    axes.set_xlabel("vocabulary size (log scale)")
    axes.set_ylabel("test accuracy")
    axes.set_ylim(min(accs) - 0.012, max(accs) + 0.016)
    axes.set_title(f"{sizes[0]:,} features and {sizes[-1]:,} features score "
                   f"within {max(accs) - min(accs):.4f}")


def leak_and_typos(fig, axes, p: Palette) -> None:
    """One template token, and what happens when the template changes."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score

    d = setup()
    model, tfidf, y_te = d["model"], d["tfidf"], d["y_te"]
    has = np.array(["ref_bill" in doc.split() for doc in d["d_te"]])
    stripped = [" ".join(w for w in doc.split() if w != "ref_bill")
                for doc in d["d_te"]]

    pred_now = model.predict(tfidf.transform(d["d_te"]))
    pred_after = model.predict(tfidf.transform(stripped))

    axs = fig.subplots(1, 2)

    bars = [
        ("template\npresent", accuracy_score(y_te[has], pred_now[has]), p.green),
        ("template\nremoved", accuracy_score(y_te[has], pred_after[has]), p.red),
    ]
    idx = np.arange(len(bars))
    axs[0].bar(idx, [b[1] for b in bars], color=[b[2] for b in bars], width=0.5)
    for i, b in enumerate(bars):
        axs[0].annotate(f"{b[1]:.4f}", (i, b[1] + 0.012), ha="center",
                        fontsize=10.5, color=p.muted)
    coef = float(model.coef_[0][tfidf.vocabulary_["ref_bill"]])
    axs[0].set_xticks(idx)
    axs[0].set_xticklabels([b[0] for b in bars], fontsize=9.5)
    axs[0].set_ylim(0, 1.12)
    axs[0].set_ylabel(f"accuracy on the {int(has.sum())} tickets carrying it")
    axs[0].set_title(f"'ref_bill' has coefficient {coef:+.3f}", fontsize=10.5)

    def typo(doc, rng, rate=0.25):
        out = []
        for word in doc.split():
            if len(word) > 4 and rng.random() < rate:
                j = int(rng.integers(1, len(word) - 1))
                word = word[:j] + word[j + 1:]
            out.append(word)
        return " ".join(out)

    rng = np.random.default_rng(0)
    typoed = [typo(doc, rng) for doc in d["d_te"]]

    char_vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2)
    A = char_vec.fit_transform(d["d_tr"])
    char_model = LogisticRegression(max_iter=3000).fit(A, d["y_tr"])

    series = [
        ("word tf-idf", p.blue,
         accuracy_score(y_te, pred_now),
         accuracy_score(y_te, model.predict(tfidf.transform(typoed)))),
        ("char 3-5 grams", p.amber,
         accuracy_score(y_te, char_model.predict(char_vec.transform(d["d_te"]))),
         accuracy_score(y_te, char_model.predict(char_vec.transform(typoed)))),
    ]
    idx = np.arange(2)
    for offset, (label, colour, clean, dirty) in zip((-0.2, 0.2), series):
        axs[1].bar(idx + offset, [clean, dirty], 0.4, color=colour, label=label)
        for i, v in enumerate((clean, dirty)):
            axs[1].annotate(f"{v:.4f}", (i + offset, v + 0.008), ha="center",
                            fontsize=9, color=colour)
    axs[1].set_xticks(idx)
    axs[1].set_xticklabels(["clean text", "25% of long words\nmissing a letter"],
                           fontsize=9.5)
    axs[1].set_ylim(0.75, 0.97)
    axs[1].set_ylabel("test accuracy")
    axs[1].set_title("Character n-grams survive typos", fontsize=10.5)
    axs[1].legend(loc="upper center", ncol=2, fontsize=8.5)

    fig.suptitle("Two failure modes that no cross-validation on clean, "
                 "same-template data can show you.",
                 fontsize=10.5, color=p.muted)


FIGURES = [
    figure("sparse-matrix", sparse_matrix, size=(8.8, 3.9), axes=False),
    figure("idf-and-zipf", idf_and_zipf, size=(8.8, 3.9), axes=False),
    figure("model-comparison", model_comparison, size=(8.2, 4.0)),
    figure("min-df-pruning", min_df_pruning, size=(8.2, 4.2)),
    figure("leak-and-typos", leak_and_typos, size=(8.8, 3.9), axes=False),
]
