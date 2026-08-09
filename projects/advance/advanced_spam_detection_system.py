"""Spam detection, scored the way a mail filter has to be scored.

The version this replaces trained a Naive Bayes classifier on a handful of
strings and printed a label for one message. It never reported accuracy,
never held anything out, and never faced the asymmetry that defines the
problem: a spam message in the inbox is an annoyance, and a real message in
the spam folder can be a missed job offer.

That asymmetry is the whole design. A filter is tuned for precision on the
spam class -- almost nothing legitimate should be caught -- and recall is
whatever is left over. This file measures both, at several thresholds, and
then measures what happens when the spammer adapts.

    python advanced_spam_detection_system.py
"""

import re

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

SPAM_TEMPLATES = [
    "WINNER! You have been selected for a {prize} prize. Claim now at {url}",
    "Congratulations, your account qualifies for a free {prize}. Reply YES",
    "URGENT: verify your account at {url} or it will be closed within 24 hours",
    "Cheap {product} online, no prescription needed, discreet delivery",
    "Make ${amount} a week working from home. No experience. Click {url}",
    "Your parcel is held at customs. Pay the {amount} fee at {url}",
    "Limited offer: {product} at 90% off today only. Buy now {url}",
    "You have unclaimed funds of ${amount}. Send your bank details to claim",
    # The hard cases: spam that reads like ordinary business mail. Without
    # these the classes share no vocabulary and every model scores 1.0000,
    # which measures the corpus rather than the classifier.
    "Hi {name}, please review the attached {document} and confirm the "
    "{amount} payment by Friday",
    "Reminder: your {product} subscription renews next week. Update details "
    "at {url}",
    "{name}, the invoice for last month is overdue. Settle {amount} here: "
    "{url}",
    "Following up on our {meeting} -- the {document} is ready for your "
    "signature at {url}",
]
HAM_TEMPLATES = [
    "Hi {name}, can we move the {meeting} to Thursday afternoon?",
    "Please find the {document} attached for review before Friday",
    "The build failed on main, looks like the {module} tests are flaky",
    "Thanks for lunch yesterday. I will send the {document} over tonight",
    "Reminder: {meeting} at 10am, room 4. Agenda attached",
    "Could you review my pull request when you get a chance, {name}?",
    "The invoice for last month is attached. Let me know if anything is off",
    "I am out on Friday, {name} is covering the {meeting}",
    # Legitimate mail that uses the vocabulary spam filters look for.
    "URGENT: production is down, joining the {meeting} now",
    "Your {product} licence renews on the 3rd, invoice for {amount} attached",
    "{name}, please confirm the {amount} refund went through today",
    "Congratulations on the promotion! Drinks after the {meeting}?",
    "Click {url} for the {document} -- sharepoint link, expires in 7 days",
]

FILLERS = {
    "prize": ["cash", "iPhone", "holiday", "gift card"],
    "url": ["http://bit.ly/x1", "www.claim-now.biz", "http://secure-verify.co"],
    "product": ["watches", "pills", "software", "handbags"],
    "amount": ["500", "1,200", "97", "3,000"],
    "name": ["Sam", "Priya", "Alex", "Jordan"],
    "meeting": ["standup", "retro", "planning call", "one to one"],
    "document": ["report", "spec", "invoice", "slides"],
    "module": ["auth", "billing", "search", "upload"],
}


def build_corpus(n_spam=400, n_ham=1600, seed=20260809):
    """Imbalanced on purpose: most mail is not spam."""
    import random
    rng = random.Random(seed)

    def fill(template):
        out = template
        for key, options in FILLERS.items():
            out = out.replace("{" + key + "}", rng.choice(options))
        return out

    texts = [fill(rng.choice(SPAM_TEMPLATES)) for _ in range(n_spam)]
    texts += [fill(rng.choice(HAM_TEMPLATES)) for _ in range(n_ham)]
    labels = [1] * n_spam + [0] * n_ham
    return texts, labels


def obfuscate(text):
    """What a spammer does the day after a filter starts working.

    Character substitutions defeat word-level features completely: `v1agra`
    and `viagra` share no token, so a model that learned the second has never
    seen the first.
    """
    swaps = {"a": "@", "i": "1", "o": "0", "e": "3", "s": "$"}
    return "".join(swaps.get(c, c) for c in text)


def score(model, vectorizer, texts, labels, threshold=0.5):
    probabilities = model.predict_proba(vectorizer.transform(texts))[:, 1]
    predicted = (probabilities >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predicted, average="binary", zero_division=0)
    caught_ham = int(((predicted == 1) & (labels == 0)).sum())
    return {"precision": precision, "recall": recall, "f1": f1,
            "ham_lost": caught_ham}


def main():
    print("Advanced Spam Detection System")
    import numpy as np

    texts, labels = build_corpus()
    labels = np.array(labels)
    print(f"  messages           : {len(texts):,} "
          f"({labels.sum()} spam, {labels.mean():.1%})")

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.3, random_state=0, stratify=labels)
    print(f"  train / test       : {len(X_train):,} / {len(X_test):,}")

    print(f"\n{'features':>26} {'precision':>10} {'recall':>8} {'F1':>7} "
          f"{'real mail lost':>15}")
    print("  " + "-" * 70)
    fitted = {}
    for name, vectorizer in (
            ("word counts", CountVectorizer()),
            ("word tf-idf", TfidfVectorizer()),
            ("char 3-5 grams tf-idf",
             TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5)))):
        model = MultinomialNB()
        model.fit(vectorizer.fit_transform(X_train), y_train)
        fitted[name] = (model, vectorizer)
        result = score(model, vectorizer, X_test, y_test)
        print(f"  {name:>24} {result['precision']:>10.4f} "
              f"{result['recall']:>8.4f} {result['f1']:>7.4f} "
              f"{result['ham_lost']:>15}")

    model, vectorizer = fitted["word tf-idf"]
    print(f"\n  the same word tf-idf model at different thresholds:")
    print(f"    {'threshold':>10} {'precision':>10} {'recall':>8} "
          f"{'real mail lost':>15}")
    for threshold in (0.5, 0.7, 0.9, 0.99):
        result = score(model, vectorizer, X_test, y_test, threshold)
        print(f"    {threshold:>10.2f} {result['precision']:>10.4f} "
              f"{result['recall']:>8.4f} {result['ham_lost']:>15}")
    print("    A mail filter is tuned on this table, not on F1. Losing one")
    print("    real message is worse than passing a hundred spam, so the")
    print("    right-hand column is the constraint and recall is whatever")
    print("    remains once it is satisfied.")

    # And what happens when the spammer adapts.
    spam_texts = [t for t, l in zip(X_test, y_test) if l == 1]
    obfuscated = [obfuscate(t) for t in spam_texts]
    print(f"\n  the spammer substitutes characters (v1agra for viagra):")
    print(f"    {'features':>24} {'spam caught before':>19} "
          f"{'after':>8}")
    for name, (model, vectorizer) in fitted.items():
        before = model.predict(vectorizer.transform(spam_texts)).mean()
        after = model.predict(vectorizer.transform(obfuscated)).mean()
        print(f"    {name:>24} {before:>19.1%} {after:>8.1%}")
    print("    `claim` and `cl@1m` share no token, so every substituted word")
    print("    is a word the model has never seen. What survives for the word")
    print("    models is the untouched text -- capitals, numbers, punctuation")
    print("    -- which is why they degrade rather than collapse.")
    print("    The character model loses least: its features span the")
    print("    substitutions, so `cl@1m` still shares n-grams with `claim`.")

    print(f"\n  example messages and what the word model says:")
    for text in (spam_texts[0], obfuscate(spam_texts[0]),
                 [t for t, l in zip(X_test, y_test) if l == 0][0]):
        model, vectorizer = fitted["word tf-idf"]
        p = model.predict_proba(vectorizer.transform([text]))[0, 1]
        print(f"    P(spam)={p:.3f}  {text[:58]}")


if __name__ == "__main__":
    main()
