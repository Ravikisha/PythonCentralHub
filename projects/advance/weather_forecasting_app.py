"""Weather forecasting, against the baseline that is famously hard to beat.

The version this replaces fitted a straight line to synthetic data and
printed "Weather forecasting model trained." Weather does not trend upwards
in a straight line, and nothing was forecast.

The baseline here is persistence: tomorrow will be like today. It is the
oldest forecast there is and it is genuinely hard to beat at short range,
which is why every serious forecast is scored against it. Climatology --
"tomorrow will be like this date usually is" -- takes over at longer range,
and the crossover between the two is measured below.

    python weather_forecasting_app.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DAYS = 365 * 3


def make_weather(seed=20260809):
    """Daily temperature: an annual cycle, day-to-day persistence, noise.

    The autoregressive term is what makes persistence work: today's anomaly
    carries into tomorrow. Without it the series would be seasonal mean plus
    independent noise, and persistence would be no better than climatology.
    """
    rng = np.random.default_rng(seed)
    day = np.arange(DAYS)
    seasonal = 11.0 - 9.5 * np.cos(2 * np.pi * (day + 10) / 365.25)
    anomaly = np.zeros(DAYS)
    for i in range(1, DAYS):
        anomaly[i] = 0.72 * anomaly[i - 1] + rng.normal(0, 2.4)
    return seasonal + anomaly, seasonal


def climatology(series, day_of_year, history_end):
    """The mean of this calendar day over every year seen so far."""
    days = np.arange(history_end) % 365
    matching = series[:history_end][np.abs(days - day_of_year) <= 5]
    return float(matching.mean()) if len(matching) else float(
        series[:history_end].mean())


def evaluate(series, horizon, warmup=730):
    """Score three forecasts at a given lead time, on unseen days only."""
    persistence, climate, blended, actual = [], [], [], []
    for i in range(warmup, DAYS - horizon):
        target = series[i + horizon]
        persistence.append(series[i])
        climate.append(climatology(series, (i + horizon) % 365, i))
        # Damped persistence: the anomaly decays towards climatology as the
        # lead time grows, which is what a real short-range model does.
        weight = 0.72 ** horizon
        blended.append(weight * series[i] + (1 - weight) * climate[-1])
        actual.append(target)

    actual = np.array(actual)
    return {
        "persistence": float(np.abs(np.array(persistence) - actual).mean()),
        "climatology": float(np.abs(np.array(climate) - actual).mean()),
        "damped": float(np.abs(np.array(blended) - actual).mean()),
    }


def main():
    print("Weather Forecasting App")
    series, seasonal = make_weather()
    print(f"  days simulated     : {DAYS:,} ({DAYS / 365.25:.1f} years)")
    print(f"  temperature range  : {series.min():.1f} to {series.max():.1f} C")
    print(f"  seasonal swing     : {seasonal.max() - seasonal.min():.1f} C")
    print(f"  day-to-day change  : "
          f"{np.abs(np.diff(series)).mean():.2f} C on average")

    print(f"\n  mean absolute error at each lead time, "
          f"scored on {DAYS - 730} unseen days:\n")
    print(f"{'lead (days)':>12} {'persistence':>13} {'climatology':>13} "
          f"{'damped':>9}  {'best':>13}")
    print("  " + "-" * 68)
    rows = []
    for horizon in (1, 2, 3, 5, 7, 10, 14, 30):
        scores = evaluate(series, horizon)
        best = min(scores, key=scores.get)
        rows.append((horizon, scores, best))
        print(f"{horizon:>12} {scores['persistence']:>13.3f} "
              f"{scores['climatology']:>13.3f} {scores['damped']:>9.3f}  "
              f"{best:>13}")

    crossover = next((h for h, s, _ in rows
                      if s["climatology"] < s["persistence"]), None)
    print(f"\n  Persistence wins at short range and climatology takes over "
          f"from day {crossover}.")
    print("  That crossover is the whole shape of short-range forecasting:")
    print("  today's weather tells you about tomorrow and almost nothing")
    print("  about next month, at which point the calendar is a better guide.")

    day_one = rows[0][1]
    print(f"\n  At one day ahead, persistence scores "
          f"{day_one['persistence']:.3f} C and climatology")
    print(f"  {day_one['climatology']:.3f} C -- "
          f"{day_one['climatology'] / day_one['persistence']:.1f}x worse. "
          f"A forecast that beats")
    print("  climatology at day 1 has done nothing; the bar is persistence.")

    damped_wins = [h for h, sc, b in rows if b == "damped"]
    if len(damped_wins) == len(rows):
        print(f"\n  Damped persistence is best at every lead time tested. It "
              f"fits nothing:")
        print("  it is the two baselines blended by how fast the anomaly")
        print("  decays, and one number -- the decay rate -- is the entire")
        print("  model. Beating both baselines everywhere with no fitting is")
        print("  the reason it is the standard reference forecast rather than")
        print("  persistence alone.")
    else:
        print(f"\n  Damped persistence is best at lead times {damped_wins}.")

    day_one_best = rows[0][1][rows[0][2]]
    print(f"\n  So the bar for a real model at one day ahead is "
          f"{day_one_best:.3f} C, not the")
    print(f"  {day_one['climatology']:.3f} C that climatology gives away. "
          f"Published forecast skill is")
    print("  reported against these baselines for exactly that reason: a")
    print("  number with no baseline beside it cannot be judged.")

    figure, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    window = slice(730, 730 + 365)
    axes[0].plot(series[window], lw=0.9, label="observed", color="#1a73e8")
    axes[0].plot(seasonal[window], lw=1.4, label="seasonal mean",
                 color="#d93025")
    axes[0].set_xlabel("day of year 3")
    axes[0].set_ylabel("temperature (C)")
    axes[0].set_title("one year of the simulated series")
    axes[0].legend(fontsize=8)

    horizons = [r[0] for r in rows]
    for key, style in (("persistence", "o-"), ("climatology", "s--"),
                       ("damped", "^-")):
        axes[1].plot(horizons, [r[1][key] for r in rows], style, label=key)
    axes[1].set_xlabel("lead time (days)")
    axes[1].set_ylabel("mean absolute error (C)")
    axes[1].set_title("where each baseline stops being the best one")
    axes[1].legend(fontsize=8)
    figure.tight_layout()
    figure.savefig("weather_forecasting_app.png", dpi=120,
                   bbox_inches="tight")
    print("\nsaved weather_forecasting_app.png")


if __name__ == "__main__":
    main()
