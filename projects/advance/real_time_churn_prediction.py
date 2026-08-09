"""Churn prediction, and the question a churn model is actually asked.

The version this replaces trained a logistic regression on `np.random.rand`
features against `np.random.randint` labels. There was no relationship
between them to learn, so the model could only score chance -- and it printed
the predictions without scoring anything, so nobody would have noticed.

The question a retention team asks is not "is this model accurate". It is:
if I can call 200 customers this month, which 200, and how many of them
would have left anyway? That is a ranking problem with a budget, and it is
what the lift table below measures.

    python real_time_churn_prediction.py
"""

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FEATURES = ("tenure (months)", "logins last month", "support tickets",
            "monthly spend", "days since last login")


def make_customers(n=8000, seed=20260809):
    """Customers whose churn probability depends on their behaviour.

    The relationship is real but noisy, which is the case worth modelling.
    Perfectly separable data would make every metric 1.0 and teach nothing.
    """
    rng = np.random.default_rng(seed)
    tenure = rng.gamma(2.0, 9.0, n)
    logins = rng.poisson(np.clip(12 - 0.15 * rng.gamma(2, 3, n), 0.4, None))
    tickets = rng.poisson(0.6, n)
    spend = rng.lognormal(3.2, 0.6, n)
    idle = rng.exponential(9.0, n)

    # Log-odds of churning. Idle time and tickets push it up, tenure and
    # logins pull it down.
    logit = (-2.4
             - 0.030 * tenure
             - 0.090 * logins
             + 0.380 * tickets
             + 0.085 * idle
             - 0.004 * spend)
    probability = 1 / (1 + np.exp(-logit))
    churned = rng.random(n) < probability
    features = np.column_stack([tenure, logins, tickets, spend, idle])
    return features, churned.astype(int), probability


def lift_table(probabilities, actual, deciles=10):
    """Sort by predicted risk, then report what each tenth actually did.

    This is the table a retention team reads. It answers the only question
    they can act on: if we contact the top 10%, what fraction of the people
    who were going to leave do we reach?
    """
    order = np.argsort(-probabilities)
    ranked = actual[order]
    size = len(ranked) // deciles
    base_rate = actual.mean()
    rows, captured = [], 0
    for index in range(deciles):
        chunk = ranked[index * size:(index + 1) * size]
        captured += chunk.sum()
        rows.append({
            "decile": index + 1,
            "rate": chunk.mean(),
            "lift": chunk.mean() / base_rate if base_rate else 0.0,
            "cumulative_capture": captured / ranked.sum(),
        })
    return rows


def main():
    print("Real-Time Churn Prediction")
    X, y, true_probability = make_customers()
    print(f"  customers          : {len(X):,}")
    print(f"  churn rate         : {y.mean():.2%}")
    print(f"  features           : {', '.join(FEATURES)}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=0, stratify=y)
    scaler = StandardScaler().fit(X_train)
    model = LogisticRegression(max_iter=1000).fit(scaler.transform(X_train),
                                                  y_train)
    probabilities = model.predict_proba(scaler.transform(X_test))[:, 1]

    predicted = (probabilities >= 0.5).astype(int)
    majority = 1 - y_test.mean()
    print(f"\n  accuracy at threshold 0.5 : {(predicted == y_test).mean():.4f}")
    print(f"  accuracy of 'nobody churns': {majority:.4f}")
    print(f"  ROC AUC                    : "
          f"{roc_auc_score(y_test, probabilities):.4f}")
    gap = (predicted == y_test).mean() - majority
    print(f"  The model is {gap:+.4f} accuracy above 'nobody ever leaves' -- "
          f"a gain of")
    print(f"  {gap * len(y_test):.0f} correct labels out of {len(y_test):,}. "
          f"On an imbalanced problem")
    print("  accuracy is mostly a measurement of the imbalance, and it stays")
    print("  high whether or not the model has found anything.")
    print("  AUC says the ranking carries information; it does not say what")
    print("  to do about it, which is what the lift table below is for.")

    print(f"\n  what the model learned (coefficients on scaled features):")
    for name, weight in sorted(zip(FEATURES, model.coef_[0]),
                               key=lambda pair: -abs(pair[1])):
        direction = "raises" if weight > 0 else "lowers"
        print(f"    {name:>22} {weight:>7.3f}  {direction} churn risk")

    rows = lift_table(probabilities, y_test)
    print(f"\n  lift table -- customers sorted by predicted risk:")
    print(f"    {'decile':>7} {'churn rate':>11} {'lift':>7} "
          f"{'churners reached':>17}")
    for row in rows:
        print(f"    {row['decile']:>7} {row['rate']:>11.2%} "
              f"{row['lift']:>7.2f} {row['cumulative_capture']:>17.1%}")

    top = rows[0]
    print(f"\n  Contacting the riskiest 10% reaches "
          f"{top['cumulative_capture']:.1%} of everyone who")
    print(f"  churned -- {top['lift']:.2f}x what calling 10% at random would "
          f"reach.")
    print(f"  The top 30% reaches {rows[2]['cumulative_capture']:.1%}. "
          f"That is the number a")
    print("  retention budget is planned against, and no single accuracy or")
    print("  AUC figure contains it.")

    # Calibration: are the probabilities meaningful, or only the ordering?
    fraction, mean_predicted = calibration_curve(y_test, probabilities,
                                                 n_bins=8, strategy="quantile")
    print(f"\n  calibration -- predicted risk against observed rate:")
    print(f"    {'predicted':>10} {'observed':>10} {'gap':>8}")
    for predicted_p, observed in zip(mean_predicted, fraction):
        print(f"    {predicted_p:>10.3f} {observed:>10.3f} "
              f"{observed - predicted_p:>+8.3f}")
    error = float(np.mean(np.abs(fraction - mean_predicted)))
    print(f"    mean absolute calibration error: {error:.4f}")
    print("    A calibrated model can be multiplied by a customer's value to")
    print("    get an expected loss. An uncalibrated one can only be sorted,")
    print("    and 'this customer is 30% likely to leave' would be a")
    print("    statement about nothing.")

    figure, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].bar([r["decile"] for r in rows], [r["lift"] for r in rows],
                color="#1a73e8")
    axes[0].axhline(1.0, ls="--", c="#d93025", label="calling at random")
    axes[0].set_xlabel("decile of predicted risk")
    axes[0].set_ylabel("lift over the base rate")
    axes[0].set_title("who to call first")
    axes[0].legend(fontsize=8)

    axes[1].plot([0, 1], [0, 1], ls="--", c="#9aa0a6", label="perfect")
    axes[1].plot(mean_predicted, fraction, "o-", color="#1a73e8",
                 label="this model")
    axes[1].set_xlabel("predicted probability")
    axes[1].set_ylabel("observed churn rate")
    axes[1].set_title(f"calibration (mean error {error:.4f})")
    axes[1].legend(fontsize=8)
    figure.tight_layout()
    figure.savefig("real_time_churn_prediction.png", dpi=120,
                   bbox_inches="tight")
    print("\nsaved real_time_churn_prediction.png")


if __name__ == "__main__":
    main()
