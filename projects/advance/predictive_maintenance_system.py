"""Predictive maintenance: how much warning, at what false-alarm cost.

The version this replaces fitted a straight line to a straight line plus
noise, printed "Predictive maintenance model trained." and plotted the fit.
It could not have been wrong, because nothing was predicted and nothing was
scored.

The question a maintenance team asks is not "what is the R-squared". It is:
if I act on this alarm, how much warning do I get before the machine fails,
and how often will I take a machine offline that was fine? Those two move in
opposite directions and the whole job is choosing where to sit.

    python predictive_maintenance_system.py
"""

import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FAILURE_THRESHOLD = 100.0     # vibration level at which the machine is down
INSPECTION_INTERVAL = 5       # cycles between readings being checked
CYCLES = 400


def make_machine(rng, degrades=True):
    """One machine's vibration history, cycle by cycle.

    Degradation is exponential rather than linear, which is what makes this
    non-trivial: early readings look flat, so a linear extrapolation from
    them predicts failure far too late. Half the fleet never degrades at all,
    which is where the false alarms come from.
    """
    noise = rng.normal(0, 1.8, CYCLES)
    if not degrades:
        return 20 + noise, None
    onset = rng.integers(80, 220)
    rate = rng.uniform(0.020, 0.035)
    cycles = np.arange(CYCLES)
    growth = np.where(cycles < onset, 0.0,
                      np.exp(rate * (cycles - onset)) - 1.0)
    signal = 20 + growth + noise
    failed = np.argmax(signal >= FAILURE_THRESHOLD)
    return signal, (int(failed) if signal.max() >= FAILURE_THRESHOLD
                    else None)


def predict_failure_cycle(history, window=40):
    """Extrapolate the recent trend to the failure threshold.

    Fitted on the log of the reading, because the degradation is exponential
    and a linear fit on the raw values consistently predicts failure later
    than it happens -- which is the expensive direction to be wrong in.
    """
    if len(history) < window:
        return None
    recent = history[-window:]
    if recent.min() <= 0:
        return None
    # Closed-form least squares rather than sklearn: this is called tens of
    # thousands of times across the fleet sweep, and a LinearRegression object
    # per call took the whole run past a 45-second budget.
    x = np.arange(len(history) - window, len(history), dtype=float)
    y = np.log(recent)
    x_mean, y_mean = x.mean(), y.mean()
    denominator = ((x - x_mean) ** 2).sum()
    if denominator == 0:
        return None
    slope = ((x - x_mean) * (y - y_mean)).sum() / denominator
    if slope <= 1e-4:                      # not trending up: no prediction
        return None
    intercept = y_mean - slope * x_mean
    return float((np.log(FAILURE_THRESHOLD) - intercept) / slope)


def evaluate(threshold_cycles, machines, window=40):
    """Alarm when predicted failure is within `threshold_cycles`.

    Returns lead time on the machines that really failed, and how many
    healthy machines were pulled offline for nothing.
    """
    lead_times, missed, false_alarms, healthy = [], 0, 0, 0
    for history, failure in machines:
        if failure is None:
            healthy += 1
        alarmed_at = None
        # Machines are inspected on a cadence, not continuously. Checking
        # every cycle would also be 5x the work for a lead time that cannot
        # be acted on any sooner than the next inspection anyway.
        for cycle in range(window, len(history), INSPECTION_INTERVAL):
            predicted = predict_failure_cycle(history[:cycle], window)
            if predicted is not None and predicted - cycle <= threshold_cycles:
                alarmed_at = cycle
                break
        if failure is None:
            false_alarms += alarmed_at is not None
        elif alarmed_at is None or alarmed_at >= failure:
            missed += 1
        else:
            lead_times.append(failure - alarmed_at)
    return {
        "alarms_on_failing": len(lead_times),
        "missed": missed,
        "false_alarms": false_alarms,
        "healthy": healthy,
        "median_lead": float(np.median(lead_times)) if lead_times else 0.0,
        "min_lead": int(min(lead_times)) if lead_times else 0,
    }


def main():
    print("Predictive Maintenance System")
    rng = np.random.default_rng(20260809)

    fleet = []
    for index in range(60):
        history, failure = make_machine(rng, degrades=index % 2 == 0)
        fleet.append((history, failure))

    failing = [m for m in fleet if m[1] is not None]
    print(f"  machines            : {len(fleet)}")
    print(f"  that reach failure  : {len(failing)}")
    print(f"  failure threshold   : vibration {FAILURE_THRESHOLD:.0f}")
    print(f"  median failure cycle: "
          f"{np.median([m[1] for m in failing]):.0f} of {CYCLES}")

    print(f"\n{'alarm horizon':>14} {'caught':>7} {'missed':>7} "
          f"{'false':>6} {'median lead':>12} {'worst lead':>11}")
    print("  " + "-" * 62)
    rows = []
    for horizon in (10, 25, 50, 100, 200):
        result = evaluate(horizon, fleet)
        rows.append((horizon, result))
        print(f"{horizon:>14} {result['alarms_on_failing']:>7} "
              f"{result['missed']:>7} {result['false_alarms']:>6} "
              f"{result['median_lead']:>12.0f} {result['min_lead']:>11}")

    tightest, widest = rows[0][1], rows[-1][1]
    print(f"\n  Widening the horizon from {rows[0][0]} to {rows[-1][0]} cycles "
          f"took the median lead")
    print(f"  time from {tightest['median_lead']:.0f} to "
          f"{widest['median_lead']:.0f} cycles, and the false alarms from "
          f"{tightest['false_alarms']} to {widest['false_alarms']}.")
    print(f"  The worst case is what scheduling has to survive: at a horizon "
          f"of {rows[-1][0]}")
    print(f"  the median warning is {widest['median_lead']:.0f} cycles and "
          f"the shortest in the fleet is {widest['min_lead']}.")

    # Why the log fit, in numbers.
    history, failure = failing[0]
    window = 40
    at = failure - 60
    recent = history[at - window:at]
    cycles = np.arange(at - window, at).reshape(-1, 1)
    linear = LinearRegression().fit(cycles, recent)
    linear_predicted = (FAILURE_THRESHOLD - linear.intercept_) / linear.coef_[0]
    log_predicted = predict_failure_cycle(history[:at], window)
    print(f"\n  one machine, predicting from cycle {at} "
          f"(it actually failed at {failure}):")
    print(f"    linear fit on the raw reading : {linear_predicted:>7.0f}  "
          f"({linear_predicted - failure:+.0f} cycles)")
    print(f"    linear fit on the log reading : {log_predicted:>7.0f}  "
          f"({log_predicted - failure:+.0f} cycles)")
    print("    Extrapolating an exponential with a straight line predicts")
    print("    failure late, which is the direction that costs a machine.")

    figure, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for history, fail in fleet[:14]:
        axes[0].plot(history, lw=0.8,
                     color="#d93025" if fail is not None else "#9aa0a6",
                     alpha=0.8)
    axes[0].axhline(FAILURE_THRESHOLD, ls="--", c="#202124", lw=1)
    axes[0].set_xlabel("cycle")
    axes[0].set_ylabel("vibration")
    axes[0].set_ylim(0, FAILURE_THRESHOLD * 1.3)
    axes[0].set_title("degrading (red) and healthy (grey) machines")

    axes[1].plot([r[0] for r in rows],
                 [r[1]["median_lead"] for r in rows], "o-",
                 label="median lead time (cycles)")
    twin = axes[1].twinx()
    twin.plot([r[0] for r in rows],
              [r[1]["false_alarms"] for r in rows], "s--", c="#d93025",
              label="false alarms")
    axes[1].set_xlabel("alarm horizon (cycles)")
    axes[1].set_ylabel("median lead time")
    twin.set_ylabel("false alarms")
    axes[1].set_title("warning bought, healthy machines paid")
    figure.tight_layout()
    figure.savefig("predictive_maintenance_system.png", dpi=120,
                   bbox_inches="tight")
    print("\nsaved predictive_maintenance_system.png")


if __name__ == "__main__":
    main()
