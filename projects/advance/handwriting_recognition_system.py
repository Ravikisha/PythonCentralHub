"""Handwriting recognition on the digits dataset, scored properly.

The version this replaces printed one number -- "Test accuracy: 0.99" -- from
an unseeded split, and then plotted a *training* image chosen by index, which
had nothing to do with the result. Two things were missing: any account of
where the remaining 1% goes, and any reason to believe the number would
repeat.

Both are fixed here. The split is seeded, the score comes with a confidence
interval, the per-digit recall shows which digits are actually hard, and the
figure shows the errors rather than a random input.

    python handwriting_recognition_system.py
"""

import numpy as np
from sklearn.datasets import load_digits
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    print("Handwriting Recognition System")
    digits = load_digits()
    X, y = digits.data, digits.target
    print(f"  samples      : {len(X):,} of 8x8 grayscale, "
          f"{len(np.unique(y))} classes")
    print(f"  pixel range  : {X.min():.0f} to {X.max():.0f}")

    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, np.arange(len(X)), test_size=0.2, random_state=20260809,
        stratify=y)
    print(f"  train / test : {len(X_train):,} / {len(X_test):,} "
          f"(stratified, seeded)")

    # Scaling matters for an RBF SVM: the kernel is a function of Euclidean
    # distance, so a feature with a wider range dominates it. The comparison
    # below is the measurement rather than the claim.
    print(f"\n{'model':34} {'test accuracy':>14} {'5-fold CV':>18}")
    print("  " + "-" * 64)
    models = {
        "SVC(), raw pixels": SVC(random_state=0),
        "SVC() + StandardScaler": make_pipeline(StandardScaler(),
                                                SVC(random_state=0)),
        "SVC(kernel='linear')": SVC(kernel="linear", random_state=0),
        "SVC(gamma=0.001)": SVC(gamma=0.001, random_state=0),
    }
    best_name, best_model, best_score = None, None, -1.0
    for name, model in models.items():
        model.fit(X_train, y_train)
        accuracy = model.score(X_test, y_test)
        folds = cross_val_score(model, X_train, y_train, cv=5)
        print(f"  {name:32} {accuracy:>14.4f} "
              f"{folds.mean():>10.4f} +- {folds.std():.4f}")
        if accuracy > best_score:
            best_name, best_model, best_score = name, model, accuracy

    # An accuracy without an interval invites reading precision that is not
    # there. On 360 test samples, one extra mistake moves the score by 0.28%.
    n = len(X_test)
    errors = int(round((1 - best_score) * n))
    standard_error = np.sqrt(best_score * (1 - best_score) / n)
    print(f"\n  best: {best_name} at {best_score:.4f}")
    print(f"  that is {errors} mistake{'' if errors == 1 else 's'} out of "
          f"{n}; one more or fewer moves the score by {1 / n:.4f}")
    print(f"  95% interval: {best_score - 1.96 * standard_error:.4f} to "
          f"{min(1.0, best_score + 1.96 * standard_error):.4f}")

    predictions = best_model.predict(X_test)
    matrix = confusion_matrix(y_test, predictions)
    print("\n  per-digit recall:")
    for digit in range(10):
        support = matrix[digit].sum()
        recall = matrix[digit, digit] / support
        bar = "#" * int(round(recall * 30))
        print(f"    {digit}  {recall:6.3f}  ({matrix[digit, digit]:>2}/"
              f"{support:>2})  {bar}")

    confusions = [(matrix[i, j], i, j) for i in range(10) for j in range(10)
                  if i != j and matrix[i, j]]
    confusions.sort(reverse=True)
    if confusions:
        print("\n  what it actually confuses:")
        for count, true_digit, predicted in confusions[:5]:
            print(f"    {true_digit} read as {predicted}: {count} time(s)")
    else:
        print("\n  no confusions at all on this split")

    wrong = np.flatnonzero(predictions != y_test)
    print(f"\n  {len(wrong)} misclassified image(s); the figure shows them, "
          f"which is\n  the only part of the test set worth looking at.")

    figure, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    show = wrong[:8] if len(wrong) else np.arange(8)
    grid = np.zeros((8 * 2, 8 * 4))
    for position, index in enumerate(show):
        row, column = divmod(position, 4)
        grid[row * 8:(row + 1) * 8, column * 8:(column + 1) * 8] = \
            digits.images[idx_test[index]]
    axes[0].imshow(grid, cmap="gray_r")
    axes[0].set_xticks([])
    axes[0].set_yticks([])
    labels = ", ".join(f"{y_test[i]}->{predictions[i]}" for i in show)
    axes[0].set_title(f"misclassified: {labels}", fontsize=8)

    image = axes[1].imshow(matrix, cmap="Blues")
    axes[1].set_xlabel("predicted")
    axes[1].set_ylabel("true")
    axes[1].set_xticks(range(10))
    axes[1].set_yticks(range(10))
    axes[1].set_title("confusion matrix")
    figure.colorbar(image, ax=axes[1], fraction=0.046)
    figure.tight_layout()
    figure.savefig("handwriting_recognition_system.png", dpi=120,
                   bbox_inches="tight")
    print("\nsaved handwriting_recognition_system.png")


if __name__ == "__main__":
    main()
