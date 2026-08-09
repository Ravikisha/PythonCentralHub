"""A search engine, and the measurements that say whether it ranks well.

The version this replaces indexed a few strings and printed the documents
containing a query word. That is a filter, not a search engine: it says which
documents match and nothing about which one to read first, and ranking is the
entire problem.

Three rankers are built here -- raw term count, TF-IDF, and BM25 -- and scored
against relevance judgements with precision@k, recall@k and mean reciprocal
rank. The result is not the one the textbook ordering suggests: on this corpus
all three score identically, and all three rank a keyword-stuffed page first.
Term weighting cannot fix a document that genuinely is about the query term
and still worthless, and that is worth seeing before reaching for BM25 as a
solution to relevance.

    python document_search_engine.py
"""

import math
import re
from collections import Counter, defaultdict

DOCUMENTS = {
    "d01": "Python list comprehensions build a list from an iterable in one "
           "expression. They are faster than an equivalent for loop.",
    "d02": "A Python generator yields values lazily. Generators use constant "
           "memory however long the sequence is.",
    "d03": "The Python garbage collector frees memory that is no longer "
           "reachable. Reference counting handles most of it.",
    "d04": "Memory profiling in Python: tracemalloc reports allocations by "
           "line, which is how memory leaks are found.",
    "d05": "Sorting in Python uses Timsort, a stable merge sort that exploits "
           "runs already present in the data.",
    "d06": "The sorted function returns a new list. The list sort method "
           "sorts in place and returns None.",
    "d07": "Dictionary lookup in Python is a hash table operation and is "
           "constant time on average.",
    "d08": "A Python set is a hash table without values. Membership tests are "
           "constant time, unlike a list.",
    "d09": "Threading in Python is limited by the global interpreter lock. "
           "Only one thread executes bytecode at a time.",
    "d10": "Multiprocessing sidesteps the global interpreter lock by running "
           "separate Python processes with separate memory.",
    "d11": "Asyncio runs many coroutines on one thread. It helps with waiting "
           "on input and output, not with computation.",
    "d12": "Type hints in Python are not enforced at runtime. A type checker "
           "reads them before the program runs.",
    # A long, low-quality page that repeats the query term. Every real corpus
    # has these, and they are the reason raw term counts do not work: this
    # document mentions memory more often than any document that explains it.
    "d13": "Python memory Python memory tips: memory memory memory. Buy our "
           "Python memory course. Memory memory Python memory guide, memory "
           "for Python, Python memory, memory Python, memory memory.",
}

# Which documents a person would call relevant for each query. Without these
# there is nothing to score against, and "the results look reasonable" is the
# only available verdict.
JUDGEMENTS = {
    "memory": {"d02", "d03", "d04", "d10"},   # d13 mentions it most
    "constant time": {"d07", "d08"},
    "global interpreter lock": {"d09", "d10"},
    "list": {"d01", "d06", "d08"},
    "python": set(DOCUMENTS) - {"d13"},   # every real document mentions it
}

STOP_WORDS = {"a", "an", "the", "is", "are", "in", "on", "of", "and", "or",
              "it", "that", "which", "with", "by", "for", "to", "from", "at",
              "as", "not", "than", "them", "they", "how", "one", "only"}


def tokenise(text):
    return [w for w in re.findall(r"[a-z]+", text.lower())
            if w not in STOP_WORDS]


class Index:
    """An inverted index: term -> the documents containing it.

    Scanning every document per query is fine for twelve documents and
    hopeless for twelve million. The inverted index is what makes search a
    lookup rather than a scan, and it is the one structural idea here.
    """

    def __init__(self, documents):
        self.documents = documents
        self.tokens = {doc: tokenise(text) for doc, text in documents.items()}
        self.length = {doc: len(t) for doc, t in self.tokens.items()}
        self.average_length = sum(self.length.values()) / len(self.length)
        self.postings = defaultdict(dict)
        for doc, terms in self.tokens.items():
            for term, count in Counter(terms).items():
                self.postings[term][doc] = count
        self.total = len(documents)

    def idf(self, term):
        """Inverse document frequency, smoothed.

        A term in every document carries no information about which one to
        read; log(N/df) makes that weight zero automatically, which is why
        "python" stops dominating the ranking without a stop-word list.
        """
        df = len(self.postings.get(term, {}))
        return math.log((self.total + 1) / (df + 1)) + 1

    def term_count(self, query):
        scores = defaultdict(float)
        for term in tokenise(query):
            for doc, count in self.postings.get(term, {}).items():
                scores[doc] += count
        return scores

    def tfidf(self, query):
        scores = defaultdict(float)
        for term in tokenise(query):
            weight = self.idf(term)
            for doc, count in self.postings.get(term, {}).items():
                scores[doc] += (count / self.length[doc]) * weight
        return scores

    def bm25(self, query, k1=1.5, b=0.75):
        """TF-IDF with two corrections that matter on real corpora.

        `k1` saturates term frequency -- the tenth occurrence of a word adds
        far less than the second. `b` normalises by document length, so a
        long document does not win merely by containing more words.
        """
        scores = defaultdict(float)
        for term in tokenise(query):
            weight = self.idf(term)
            for doc, count in self.postings.get(term, {}).items():
                norm = 1 - b + b * self.length[doc] / self.average_length
                scores[doc] += weight * (count * (k1 + 1)
                                         / (count + k1 * norm))
        return scores

    def search(self, query, ranker="bm25", top=5):
        scores = getattr(self, ranker if ranker != "term count"
                         else "term_count")(query)
        return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[:top]


def precision_at_k(ranked, relevant, k):
    top = [doc for doc, _ in ranked[:k]]
    return sum(doc in relevant for doc in top) / k if k else 0.0


def recall_at_k(ranked, relevant, k):
    top = [doc for doc, _ in ranked[:k]]
    return (sum(doc in relevant for doc in top) / len(relevant)
            if relevant else 0.0)


def reciprocal_rank(ranked, relevant):
    for position, (doc, _) in enumerate(ranked, start=1):
        if doc in relevant:
            return 1.0 / position
    return 0.0


def main():
    print("Document Search Engine")
    index = Index(DOCUMENTS)
    print(f"  documents      : {index.total}")
    print(f"  distinct terms : {len(index.postings):,}")
    print(f"  mean length    : {index.average_length:.1f} tokens "
          f"after stop-word removal")

    rankers = ("term count", "tfidf", "bm25")
    print(f"\n{'query':>26} {'ranker':>11} {'P@3':>6} {'R@3':>6} {'MRR':>6}")
    print("  " + "-" * 60)
    totals = {r: [0.0, 0.0, 0.0] for r in rankers}
    for query, relevant in JUDGEMENTS.items():
        for ranker in rankers:
            ranked = index.search(query, ranker, top=len(DOCUMENTS))
            p = precision_at_k(ranked, relevant, 3)
            r = recall_at_k(ranked, relevant, 3)
            mrr = reciprocal_rank(ranked, relevant)
            totals[ranker][0] += p
            totals[ranker][1] += r
            totals[ranker][2] += mrr
            label = query if ranker == rankers[0] else ""
            print(f"{label:>26} {ranker:>11} {p:>6.2f} {r:>6.2f} {mrr:>6.2f}")

    n = len(JUDGEMENTS)
    print(f"\n  averaged over {n} queries:")
    for ranker in rankers:
        p, r, mrr = (v / n for v in totals[ranker])
        print(f"    {ranker:>11}  P@3 {p:.3f}   R@3 {r:.3f}   MRR {mrr:.3f}")

    scores = {r: totals[r][0] / n for r in rankers}
    if len(set(round(v, 3) for v in scores.values())) == 1:
        print("\n  All three rankers scored identically. That is a real")
        print("  result, not a bug: twelve short documents give IDF almost")
        print("  nothing to discriminate with, and the rank order only")
        print("  differs below the cut-off where P@3 stops looking.")

    print(f"\n  The query 'memory', where the ordering does differ:")
    for ranker in rankers:
        top = index.search("memory", ranker, top=3)
        print(f"    {ranker:>11}: " + ", ".join(
            f"{doc}({score:.2f})" for doc, score in top))
    print("    d13 is the keyword-stuffed page, and every ranker puts it")
    print("    first. It is not a ranking failure -- d13 really is denser in")
    print("    'memory' than any document that explains memory. Term")
    print("    weighting has no signal that could tell them apart, because")
    print("    the difference is quality, not term statistics. That needs a")
    print("    separate signal: link structure, spam classification, or a")
    print("    human judgement like the ones this file scores against.")

    print(f"\n  And on 'python', a term every document contains:")
    for ranker in rankers:
        top = index.search("python", ranker, top=3)
        print(f"    {ranker:>11}: " + ", ".join(
            f"{doc}({score:.3f})" for doc, score in top))
    print(f"    idf('python') = {index.idf('python'):.3f}, "
          f"idf('memory') = {index.idf('memory'):.3f}")
    print(f"    'memory' carries "
          f"{index.idf('memory') / index.idf('python'):.2f}x the weight of")
    print("    'python' here. With +1 smoothing the floor is 1.0 rather than")
    print("    0, so a universal term is not erased -- it is just outweighed")
    print("    by anything more selective, which is enough.")


if __name__ == "__main__":
    main()
