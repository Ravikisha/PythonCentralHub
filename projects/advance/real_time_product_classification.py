"""Real-time product classification.

Products arrive as a stream, so the classifier is trained with `partial_fit`
and scored **before** each batch is used for training -- prequential
evaluation, which is the only honest way to score a model that learns as it
goes. Halfway through, the catalogue shifts and a new category appears, so the
accuracy curve shows both learning and forgetting.
"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import SGDClassifier

FEATURES = 12
CATEGORIES = ("tools", "clothing", "grocery", "electronics")


def product_stream(batches=60, batch=40, seed=0, drift_at=30):
    """Feature vectors per category, with a fourth category appearing later."""
    rng = np.random.default_rng(seed)
    centres = rng.normal(0, 2.0, (len(CATEGORIES), FEATURES))
    for index in range(batches):
        active = 3 if index < drift_at else 4
        labels = rng.integers(0, active, batch)
        rows = centres[labels] + rng.normal(0, 1.0, (batch, FEATURES))
        yield index, rows.astype("float32"), labels


class StreamingClassifier:
    def __init__(self):
        self.model = SGDClassifier(loss="log_loss", random_state=0)
        self.started = False

    def predict(self, rows):
        if not self.started:
            return np.zeros(len(rows), dtype=int)
        return self.model.predict(rows)

    def learn(self, rows, labels):
        self.model.partial_fit(rows, labels,
                               classes=np.arange(len(CATEGORIES)))
        self.started = True


def main():
    classifier = StreamingClassifier()
    accuracies, seen, drift_at = [], 0, 30

    for index, rows, labels in product_stream(drift_at=drift_at):
        # Score before training on this batch: the model has not seen it yet.
        predicted = classifier.predict(rows)
        accuracies.append(float((predicted == labels).mean()))
        classifier.learn(rows, labels)
        seen += len(rows)

    accuracies = np.asarray(accuracies)
    warm = accuracies[5:drift_at]
    after = accuracies[drift_at:drift_at + 5]
    recovered = accuracies[-5:]

    print("Real-Time Product Classification")
    print(f"  products seen              : {seen:,}")
    print(f"  batches                    : {len(accuracies)}")
    print(f"  prequential accuracy, warm : {warm.mean():.4f}")
    print(f"  first 5 batches after drift: {after.mean():.4f}")
    print(f"  final 5 batches            : {recovered.mean():.4f}")
    print(f"  drop when a new category appeared: "
          f"{warm.mean() - after.mean():.4f}")
    print(f"  recovered to within "
          f"{abs(warm.mean() - recovered.mean()):.4f} of the pre-drift rate")
    print("\n  every score above was taken BEFORE the batch was trained on,")
    print("  so nothing here is measured on data the model had already seen")

    plt.figure(figsize=(9, 3.4))
    plt.plot(accuracies, linewidth=1.3, label="prequential accuracy")
    plt.axvline(drift_at, linestyle="--", linewidth=1.2,
                label="4th category appears")
    plt.axhline(warm.mean(), linestyle=":", linewidth=1.0,
                label=f"pre-drift mean {warm.mean():.3f}")
    plt.xlabel("batch")
    plt.ylabel("accuracy on unseen batch")
    plt.title("learning, then forgetting, then relearning")
    plt.legend(fontsize=8)
    plt.savefig("real_time_product_classification.png", dpi=120,
                bbox_inches="tight")
    print("saved real_time_product_classification.png")


if __name__ == "__main__":
    main()
