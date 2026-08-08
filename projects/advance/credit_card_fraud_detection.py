import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt

import os

import numpy as np


def sample_dataset(rows=20000, fraud_rate=0.0017, seed=0):
    """Stand in for the Kaggle credit-card dataset, which is not in this repo.

    The real file is ~150 MB and cannot be redistributed here, so this builds
    one with the property that actually matters for the lesson: fraud is rare.
    At 0.17% positives, a model that predicts "legitimate" every time scores
    99.83% accuracy -- which is why the classification report below, not the
    accuracy line, is the thing to read.
    """
    rng = np.random.default_rng(seed)
    frauds = int(rows * fraud_rate)
    labels = np.zeros(rows, dtype=int)
    labels[rng.choice(rows, frauds, replace=False)] = 1

    features = rng.normal(0, 1, (rows, 28))
    # Fraudulent rows differ on a handful of components, faintly.
    features[labels == 1, 3] += 2.2
    features[labels == 1, 11] -= 1.9
    features[labels == 1, 17] += 1.4

    frame = pd.DataFrame(features, columns=[f"V{i}" for i in range(1, 29)])
    frame["Time"] = rng.uniform(0, 172800, rows)
    frame["Amount"] = np.abs(rng.lognormal(3.0, 1.2, rows)).round(2)
    frame["Class"] = labels
    return frame


# Load dataset (replace with your dataset path)
if os.path.exists("creditcard.csv"):
    data = pd.read_csv("creditcard.csv")
else:
    data = sample_dataset()
    print(f"creditcard.csv not found, so a synthetic set was generated: "
          f"{len(data):,} rows, {int(data['Class'].sum())} frauds "
          f"({data['Class'].mean():.4%})")
    print("the real dataset is on Kaggle; the imbalance is what matters here\n")

baseline = 1 - data["Class"].mean()
print(f"always predicting 'legitimate' would score {baseline:.4%}")
print("so accuracy alone cannot tell you whether the model learned anything\n")

# Features and target
y = data['Class']
X = data.drop(['Class', 'Time'], axis=1)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluation
print('Accuracy:', accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred, zero_division=0))

# The line above is the point of the whole project. Read the recall on class 1.
caught = int(((y_pred == 1) & (y_test == 1)).sum())
total_fraud = int((y_test == 1).sum())
print(f"frauds in the test set : {total_fraud}")
print(f"frauds the model caught: {caught}")
print(f"accuracy               : {accuracy_score(y_test, y_pred):.4f}")
print()
print("a model that catches none of the fraud still scores about 99.8%,")
print("because 99.8% of the rows are not fraud. Accuracy is the wrong metric")
print("for a rare event; recall on the positive class is the one that moves.")
print("Fixing it means class weights, resampling, or a threshold chosen from")
print("the precision-recall curve -- not a bigger forest.")

# Feature importance plot
importances = model.feature_importances_
features = X.columns
plt.figure(figsize=(10,6))
plt.barh(features, importances)
plt.xlabel('Importance')
plt.title('Feature Importances')
plt.tight_layout()
plt.savefig("credit_card_fraud_detection.png", dpi=120, bbox_inches="tight")
print("saved credit_card_fraud_detection.png")
plt.show()
