"""Extractive text summarisation with TextRank, written out.

The version this replaces imported `gensim.summarization.summarize`, which
gensim removed in version 4.0. The line had been broken for years and nobody
noticed, because nothing ran the file.

Rather than pinning an old gensim, the algorithm is here: TextRank is PageRank
over a graph of sentences, where the edge weight is how much two sentences
overlap. It is about forty lines and it is worth seeing, because "summarise"
is otherwise a black box that either works or does not.

Extractive means it *selects* sentences rather than writing new ones. Every
sentence in the output appeared verbatim in the input, which is a real
limitation and also the reason it cannot hallucinate.

    python nlp_text_summarizer.py
"""

import math
import re
from collections import Counter

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "of", "in", "on", "at", "to", "for",
    "with", "is", "are", "was", "were", "be", "been", "being", "it", "its",
    "this", "that", "these", "those", "as", "by", "from", "which", "such",
    "can", "has", "have", "had", "not", "they", "their", "them", "also",
}


def split_sentences(text: str) -> list[str]:
    """Split on sentence-ending punctuation followed by a capital letter.

    A real tokeniser handles abbreviations, decimals and quotes. This does
    not, and says so: the cost of getting it wrong here is one badly-cut
    sentence in the output rather than a wrong answer.
    """
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 20]


def words(sentence: str) -> list[str]:
    return [w for w in re.findall(r"[a-z']+", sentence.lower())
            if w not in STOP_WORDS and len(w) > 2]


def similarity(a: list[str], b: list[str]) -> float:
    """Overlap between two sentences, normalised by their lengths.

    The log normalisation is what stops long sentences dominating: without
    it, the longest sentence in any document shares words with everything and
    wins every ranking, regardless of what it says.
    """
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    if not common:
        return 0.0
    denominator = math.log(len(a) + 1) + math.log(len(b) + 1)
    return len(common) / denominator if denominator else 0.0


def textrank(sentences: list[str], damping=0.85, iterations=40):
    """PageRank over the sentence similarity graph."""
    tokens = [words(s) for s in sentences]
    n = len(sentences)
    if n == 0:
        return []
    weights = [[similarity(tokens[i], tokens[j]) if i != j else 0.0
                for j in range(n)] for i in range(n)]
    out_sum = [sum(row) or 1.0 for row in weights]

    scores = [1.0 / n] * n
    for _ in range(iterations):
        updated = []
        for i in range(n):
            incoming = sum(weights[j][i] / out_sum[j] * scores[j]
                           for j in range(n))
            updated.append((1 - damping) / n + damping * incoming)
        scores = updated
    return scores


def summarize(text: str, ratio: float = 0.35) -> list[str]:
    """Return the top-ranked sentences, in their original order.

    Reordering by score would produce a ranked list of sentences, not a
    summary: extractive summaries only read as text because the selected
    sentences keep the order the author put them in.
    """
    sentences = split_sentences(text)
    if len(sentences) < 3:
        return sentences
    scores = textrank(sentences)
    keep = max(1, round(len(sentences) * ratio))
    chosen = sorted(sorted(range(len(sentences)),
                           key=lambda i: -scores[i])[:keep])
    return [sentences[i] for i in chosen]


def frequency_baseline(text: str, ratio: float = 0.35) -> list[str]:
    """Score each sentence by the total frequency of the words in it.

    The baseline exists so the TextRank result has something to be compared
    against. It is much simpler and it is not obviously worse, which is worth
    knowing before reaching for the graph algorithm.
    """
    sentences = split_sentences(text)
    if len(sentences) < 3:
        return sentences
    counts = Counter(w for s in sentences for w in words(s))
    scores = [sum(counts[w] for w in words(s)) / max(len(words(s)), 1)
              for s in sentences]
    keep = max(1, round(len(sentences) * ratio))
    chosen = sorted(sorted(range(len(sentences)),
                           key=lambda i: -scores[i])[:keep])
    return [sentences[i] for i in chosen]


ARTICLE = """
Natural language processing is a field of artificial intelligence concerned
with the interaction between computers and human language. Its objective is
to let computers read, interpret and generate text in a way that is useful.
Early systems relied on hand-written grammar rules, which were precise and
brittle. A rule that covered one construction failed on the next, and the
rule sets grew faster than the coverage did. Statistical methods replaced
them by learning patterns from large collections of text instead. This
shifted the bottleneck from linguistic expertise to data and computation.
Neural language models extended that shift by learning representations
rather than features. A word is represented as a vector whose position
encodes how the word is used, so words used similarly end up nearby.
Transformer architectures then made it practical to train these models on
very large corpora. The resulting systems perform well on translation,
summarisation and question answering. They also fail in ways that are hard
to predict, because nothing in the training objective rewards being correct.
Evaluation therefore remains the difficult part of the field. A model that
scores well on a benchmark may still be unusable for the task the benchmark
was meant to represent.
"""


def main():
    print("NLP Text Summarizer")
    sentences = split_sentences(ARTICLE)
    original_words = len(ARTICLE.split())
    print(f"  input            : {len(sentences)} sentences, "
          f"{original_words} words")

    scores = textrank(sentences)
    ranked = sorted(range(len(sentences)), key=lambda i: -scores[i])
    print(f"\n  sentence ranking (TextRank score):")
    for rank, index in enumerate(ranked[:5], start=1):
        flat = " ".join(sentences[index].split())
        print(f"    {rank}. {scores[index]:.4f}  {flat[:62]}...")
    print(f"    ...")
    flat = " ".join(sentences[ranked[-1]].split())
    print(f"    lowest {scores[ranked[-1]]:.4f}  {flat[:62]}...")

    for name, function in (("TextRank", summarize),
                           ("word frequency", frequency_baseline)):
        chosen = function(ARTICLE)
        kept = sum(len(s.split()) for s in chosen)
        print(f"\n  {name}: {len(chosen)} of {len(sentences)} sentences, "
              f"{kept} of {original_words} words "
              f"({kept / original_words:.0%})")
        for sentence in chosen:
            print(f"    - {' '.join(sentence.split())[:72]}")

    overlap = set(summarize(ARTICLE)) & set(frequency_baseline(ARTICLE))
    print(f"\n  the two methods agree on {len(overlap)} of "
          f"{len(summarize(ARTICLE))} sentences")
    print("  TextRank is the more principled method and on a passage this")
    print("  short the simpler baseline picks much the same sentences. The")
    print("  gap opens up on longer documents, where frequency alone keeps")
    print("  selecting sentences about whatever the document says most.")

    print(f"\n  compression at several ratios:")
    for ratio in (0.2, 0.35, 0.5):
        chosen = summarize(ARTICLE, ratio)
        kept = sum(len(s.split()) for s in chosen)
        print(f"    ratio {ratio:.2f}: {len(chosen)} sentences, "
              f"{kept:>3} words, {kept / original_words:.0%} of the original")
    print("\n  Every sentence above is copied verbatim from the input. That")
    print("  is what extractive means: it cannot invent a claim, and it also")
    print("  cannot write a transition or resolve a pronoun whose antecedent")
    print("  was in a sentence it dropped.")


if __name__ == "__main__":
    main()
