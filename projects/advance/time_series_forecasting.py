"""Time series forecasting, evaluated the way a forecast has to be.

The version this replaces fitted a straight line to a straight line plus
noise and plotted the fit over the data it was fitted on. That picture always
looks good, and it says nothing: a model is judged on values it has not seen,
in the order they arrive.

This one backtests. Each forecast is made from data strictly before the point
being predicted, several methods are compared against the naive baselines
that are hard to beat, and the in-sample fit is shown next to the
out-of-sample error so the gap between them is visible.

    python time_series_forecasting.py
"""

import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEASON = 7


def make_series(n=365, seed=20260809):
    """Trend, weekly seasonality, and noise -- in that order of size."""
    rng = np.random.default_rng(seed)
    t = np.arange(n)
    weekly = np.array([0.88, 0.86, 0.89, 0.96, 1.05, 1.23, 1.14])
    level = 200 + 0.35 * t
    return level * weekly[t % SEASON] + rng.normal(0, 8, n)


# --- forecasters: each sees only `history` and returns the next value ------

def naive_last(history):
    return history[-1]


def naive_seasonal(history):
    return history[-SEASON] if len(history) >= SEASON else history[-1]


def drift(history):
    """Last value plus the average change so far -- the trend-aware naive."""
    if len(history) < 2:
        return history[-1]
    slope = (history[-1] - history[0]) / (len(history) - 1)
    return history[-1] + slope


def rolling_mean(history, window=SEASON):
    return history[-window:].mean()


def linear_trend(history):
    x = np.arange(len(history)).reshape(-1, 1)
    model = LinearRegression().fit(x, history)
    return float(model.predict([[len(history)]])[0])


def seasonal_linear(history):
    """Remove the weekly profile, fit the trend, put the profile back.

    The decomposition is the whole method: a straight line cannot represent a
    weekly cycle, so fitting one to seasonal data averages the cycle away and
    then predicts the average.
    """
    if len(history) < 3 * SEASON:
        return linear_trend(history)
    index = np.arange(len(history))
    overall = history.mean()
    profile = np.array([history[index % SEASON == s].mean() / overall
                        for s in range(SEASON)])
    deseasonalised = history / profile[index % SEASON]
    model = LinearRegression().fit(index.reshape(-1, 1), deseasonalised)
    base = float(model.predict([[len(history)]])[0])
    return base * profile[len(history) % SEASON]


METHODS = (
    ("naive (last value)", naive_last),
    ("seasonal naive (-7)", naive_seasonal),
    ("drift", drift),
    ("rolling mean (7)", rolling_mean),
    ("linear trend", linear_trend),
    ("seasonal + linear", seasonal_linear),
)


def backtest(series, method, warmup=60):
    """One-step-ahead forecasts, each made from data strictly before it."""
    errors = []
    predictions = np.full(len(series), np.nan)
    for i in range(warmup, len(series)):
        predicted = method(series[:i])
        predictions[i] = predicted
        errors.append(abs(predicted - series[i]))
    errors = np.array(errors)
    actual = series[warmup:]
    return {
        "mae": errors.mean(),
        "rmse": float(np.sqrt((errors ** 2).mean())),
        "mape": float((errors / np.abs(actual)).mean() * 100),
        "predictions": predictions,
    }


def main():
    print("Time Series Forecasting")
    series = make_series()
    warmup = 60
    print(f"  points               : {len(series)}")
    print(f"  scored forecasts     : {len(series) - warmup} "
          f"(the first {warmup} are warm-up and cannot be scored)")
    print(f"  series mean          : {series.mean():.1f}")

    print(f"\n{'method':>22} {'MAE':>8} {'RMSE':>8} {'MAPE':>7}  "
          f"{'vs seasonal naive':>18}")
    print("  " + "-" * 66)
    results = {}
    for name, method in METHODS:
        results[name] = backtest(series, method, warmup)
    reference = results["seasonal naive (-7)"]["mae"]
    for name, _ in METHODS:
        r = results[name]
        delta = (reference - r["mae"]) / reference
        print(f"{name:>22} {r['mae']:>8.3f} {r['rmse']:>8.3f} "
              f"{r['mape']:>6.2f}% {delta:>17.1%}")

    best = min(results, key=lambda k: results[k]["mae"])
    print(f"\n  best: {best} at MAE {results[best]['mae']:.3f}")
    print(f"  The baseline to beat is seasonal naive, not last-value: it")
    print(f"  already carries the weekly shape, so beating it is what the")
    print(f"  model adds on top of seasonality rather than the value of")
    print(f"  noticing seasonality at all.")

    # In-sample fit against out-of-sample error, on the same model.
    index = np.arange(len(series)).reshape(-1, 1)
    fitted = LinearRegression().fit(index, series)
    in_sample = float(fitted.score(index, series))
    in_sample_mae = float(np.abs(fitted.predict(index) - series).mean())
    print(f"\n  a straight line fitted to the WHOLE series:")
    print(f"    in-sample R^2      : {in_sample:.4f}")
    print(f"    in-sample MAE      : {in_sample_mae:.3f}")
    print(f"    backtested MAE     : {results['linear trend']['mae']:.3f}")
    print(f"  An R^2 of {in_sample:.4f} looks like a working model and the")
    print(f"  backtested MAE is {results['linear trend']['mae'] / results[best]['mae']:.1f}x the best method here. R^2 rewards")
    print(f"  explaining variance, and the trend really does explain some of")
    print(f"  it; what a line cannot do is represent the weekly cycle, so it")
    print(f"  averages the cycle away and is wrong by it every single day.")

    # What the noise floor is: nothing can beat it.
    noise_floor = 8 * np.sqrt(2 / np.pi)
    print(f"\n  the series carries N(0, 8) noise, so the best achievable MAE")
    print(f"  for a one-step forecast is about {noise_floor:.3f}. "
          f"{best} reaches")
    print(f"  {results[best]['mae']:.3f}, which is "
          f"{results[best]['mae'] / noise_floor:.2f}x the floor -- there is")
    print(f"  less room left than the table's spread suggests.")

    figure, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    window = slice(len(series) - 90, len(series))
    axes[0].plot(np.arange(len(series))[window], series[window], "k-", lw=1,
                 label="actual")
    for name in ("seasonal naive (-7)", "linear trend", "seasonal + linear"):
        axes[0].plot(np.arange(len(series))[window],
                     results[name]["predictions"][window], lw=1, label=name)
    axes[0].set_xlabel("day")
    axes[0].set_ylabel("value")
    axes[0].set_title("last 90 days, one-step-ahead forecasts")
    axes[0].legend(fontsize=7)

    names = [n for n, _ in METHODS]
    axes[1].barh(names, [results[n]["mae"] for n in names], color="#1a73e8")
    axes[1].axvline(noise_floor, ls="--", c="#d93025",
                    label=f"noise floor {noise_floor:.2f}")
    axes[1].set_xlabel("backtested MAE (lower is better)")
    axes[1].set_title("every forecast scored on unseen points")
    axes[1].legend(fontsize=8)
    figure.tight_layout()
    figure.savefig("time_series_forecasting.png", dpi=120,
                   bbox_inches="tight")
    print("\nsaved time_series_forecasting.png")


if __name__ == "__main__":
    main()
