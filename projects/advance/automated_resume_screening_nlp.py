"""Resume screening by keyword, and what that actually selects for.

The version this replaces counted how many keywords from a list appeared in
each file and ranked by the total. That is what most screening tools do, and
this file measures what it costs rather than assuming it works.

Three things are measured against hand-written ground truth: how often the
keyword score agrees with a human judgement, how much of the score is
recoverable by simply writing longer, and how many qualified candidates are
rejected for using a synonym. None of these needs a large model to
demonstrate, and all three are reasons real screening systems get audited.

    python automated_resume_screening_nlp.py
"""

import re
from collections import Counter

KEYWORDS = ["python", "sql", "docker", "kubernetes", "aws", "testing",
            "ci", "postgres", "api", "linux"]

# Synonyms a person reads as equivalent and a keyword matcher does not.
SYNONYMS = {
    "python": {"python3", "cpython"},
    "sql": {"postgresql", "mysql", "sqlite", "queries"},
    "docker": {"containers", "containerised", "containerized", "podman"},
    "kubernetes": {"k8s", "eks", "gke"},
    "aws": {"amazon", "ec2", "s3", "lambda"},
    "testing": {"pytest", "unittest", "tdd", "test"},
    "ci": {"jenkins", "buildkite", "actions", "pipeline"},
    "postgres": {"postgresql", "psql"},
    "api": {"rest", "endpoint", "endpoints", "graphql"},
    "linux": {"ubuntu", "debian", "unix", "bash"},
}

# (name, resume text, what an experienced reviewer said)
CANDIDATES = [
    ("A. strong, plain words",
     "Five years building Python services on AWS. Docker in production, "
     "Kubernetes for orchestration, SQL for reporting, testing with CI on "
     "every merge. Linux throughout. Designed the API.", 5),
    ("B. strong, uses synonyms",
     "Five years of backend work: python3 microservices on EC2 and S3, "
     "shipped in containers orchestrated with k8s, PostgreSQL for storage, "
     "pytest and a Buildkite pipeline, Ubuntu servers, REST endpoints.", 5),
    ("C. keyword stuffed, thin",
     "Python SQL Docker Kubernetes AWS testing CI Postgres API Linux. "
     "Python SQL Docker Kubernetes AWS. Keen to learn. No commercial "
     "experience yet.", 1),
    ("D. genuinely junior",
     "Recent graduate. Coursework in Python and some SQL. Built a small "
     "web API for a final project. Familiar with Linux.", 2),
    ("E. strong, very long",
     "Extensive experience across the stack. " + ("Delivered projects using "
     "Python and SQL with Docker and testing. " * 8) +
     "Led the platform team for three years.", 4),
    ("F. wrong field, right words",
     "Marketing manager. Ran campaigns for a Python conference, an AWS "
     "partner and a Docker meetup. Wrote copy about Kubernetes and SQL "
     "for our API product blog.", 1),
]


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def keyword_score(text, keywords=KEYWORDS):
    """What the original did: count keyword occurrences."""
    counts = Counter(tokens(text))
    return sum(counts[k] for k in keywords)


def coverage_score(text, keywords=KEYWORDS):
    """How many distinct keywords appear, regardless of repetition."""
    present = set(tokens(text))
    return sum(k in present for k in keywords)


def synonym_coverage(text, keywords=KEYWORDS):
    """Coverage, counting a synonym as the keyword it stands for."""
    present = set(tokens(text))
    hits = 0
    for keyword in keywords:
        if keyword in present or (SYNONYMS.get(keyword, set()) & present):
            hits += 1
    return hits


def density_score(text, keywords=KEYWORDS):
    """Coverage per hundred words -- resistant to padding, not to stuffing."""
    words = tokens(text)
    return coverage_score(text) / max(len(words), 1) * 100


def spearman(a, b):
    """Rank correlation, written out: n is 6 and scipy is a big dependency."""
    def ranks(values):
        order = sorted(range(len(values)), key=lambda i: -values[i])
        out = [0.0] * len(values)
        for position, index in enumerate(order):
            out[index] = position + 1
        return out

    ra, rb = ranks(a), ranks(b)
    n = len(a)
    d2 = sum((x - y) ** 2 for x, y in zip(ra, rb))
    return 1 - 6 * d2 / (n * (n * n - 1))


def main():
    print("Automated Resume Screening")
    print(f"  candidates : {len(CANDIDATES)}")
    print(f"  keywords   : {len(KEYWORDS)}")

    truth = [c[2] for c in CANDIDATES]
    scorers = (("keyword count", keyword_score),
               ("distinct coverage", coverage_score),
               ("coverage + synonyms", synonym_coverage),
               ("coverage per 100 words", density_score))

    print(f"\n{'candidate':>26} {'words':>6} {'reviewer':>9} " +
          " ".join(f"{name.split()[0][:9]:>10}" for name, _ in scorers))
    print("  " + "-" * 76)
    columns = {name: [] for name, _ in scorers}
    for name, text, rating in CANDIDATES:
        row = []
        for label, scorer in scorers:
            value = scorer(text)
            columns[label].append(value)
            row.append(value)
        print(f"{name:>26} {len(tokens(text)):>6} {rating:>9} " +
              " ".join(f"{v:>10.2f}" for v in row))

    print(f"\n  agreement with the reviewer (Spearman rank correlation):")
    for label, _ in scorers:
        print(f"    {label:>24} {spearman(truth, columns[label]):>7.3f}")

    counts = columns["keyword count"]
    stuffed = counts[2]
    genuine = counts[1]
    print(f"\n  Candidate C is keyword-stuffed and unqualified; the reviewer")
    print(f"  scored it 1 of 5. Its keyword count is {stuffed}, against "
          f"{genuine} for")
    print(f"  candidate B, who is qualified and wrote in synonyms.")
    print(f"  A keyword counter ranks the worst candidate "
          f"{'above' if stuffed > genuine else 'below'} the best one.")

    print(f"\n  what synonyms cost candidate B:")
    print(f"    exact keywords matched  : {coverage_score(CANDIDATES[1][1])} "
          f"of {len(KEYWORDS)}")
    print(f"    with synonyms accepted  : "
          f"{synonym_coverage(CANDIDATES[1][1])} of {len(KEYWORDS)}")
    print("    Same person, same experience, described in the words their")
    print("    last employer used. Every unmatched keyword here is a real")
    print("    skill the filter did not see.")

    print(f"\n  what padding buys candidate E:")
    short = "Delivered projects using Python and SQL with Docker and testing."
    padded = short + " " + short * 8
    print(f"    {len(tokens(short)):>3} words: keyword count "
          f"{keyword_score(short):>3}, density "
          f"{density_score(short):>5.2f}")
    print(f"    {len(tokens(padded)):>3} words: keyword count "
          f"{keyword_score(padded):>3}, density "
          f"{density_score(padded):>5.2f}")
    print("    Repeating one sentence nine times multiplied the keyword count")
    print("    nine-fold and divided the density by nine. The two scores move")
    print("    in opposite directions on the same edit, so they cannot both")
    print("    be measuring the candidate.")
    print("    Neither is safe on its own: counting rewards padding, and")
    print("    density rewards a terse resume that lists ten keywords and")
    print("    nothing else -- which is candidate C, rated 1 of 5.")

    print(f"\n  Candidate F is in the wrong field entirely and mentions every")
    print(f"  keyword in context: keyword count {counts[5]}, reviewer rating "
          f"{truth[5]}.")
    print("  No bag-of-words method can separate 'wrote copy about Kubernetes'")
    print("  from 'ran Kubernetes'. That needs the sentence, not the word,")
    print("  and it is the reason keyword screening has to be a filter that")
    print("  a person reviews rather than a decision.")


if __name__ == "__main__":
    main()
