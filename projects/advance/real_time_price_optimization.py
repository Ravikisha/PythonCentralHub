"""Real-time price optimization.

Demand falls as price rises, so profit is a curve with a peak rather than a
line to climb. The optimiser finds that peak, and the interesting part is what
happens when the elasticity it assumes is wrong -- which it always is, because
elasticity has to be estimated from noisy sales.
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize_scalar


class PriceOptimizer:
    """Constant-elasticity demand: quantity = base * (price / anchor) ** -e."""

    def __init__(self, cost, base=1000.0, anchor=20.0, elasticity=1.8):
        self.cost = cost
        self.base = base
        self.anchor = anchor
        self.elasticity = elasticity

    def demand(self, price):
        return self.base * (price / self.anchor) ** -self.elasticity

    def profit(self, price):
        return (price - self.cost) * self.demand(price)

    def best_price(self):
        result = minimize_scalar(lambda p: -self.profit(p),
                                 bounds=(self.cost + 0.01, self.anchor * 5),
                                 method="bounded")
        return float(result.x)

    def estimate_elasticity(self, prices, quantities):
        """Fit the elasticity from observed sales, in log space."""
        slope, _ = np.polyfit(np.log(prices), np.log(quantities), 1)
        return float(-slope)


def observed_sales(truth, seed=0, points=12, noise=0.08):
    rng = np.random.default_rng(seed)
    prices = np.linspace(truth.cost * 1.2, truth.anchor * 2.2, points)
    quantities = truth.demand(prices) * rng.lognormal(0, noise, points)
    return prices, quantities


def main():
    truth = PriceOptimizer(cost=8.0, elasticity=1.8)
    optimal = truth.best_price()
    print("Real-Time Price Optimization")
    print(f"  unit cost               : {truth.cost:.2f}")
    print(f"  true elasticity         : {truth.elasticity:.2f}")
    print(f"  profit-maximising price : {optimal:.2f}")
    print(f"  profit at that price    : {truth.profit(optimal):,.0f}")
    print(f"  profit at cost + 50%    : {truth.profit(truth.cost * 1.5):,.0f}")

    print(f"\n  {'assumed elasticity':>19} {'chosen price':>13} "
          f"{'true profit':>13} {'lost vs best':>13}")
    assumed_rows = []
    for elasticity in (1.2, 1.5, 1.8, 2.2, 3.0):
        assumed = PriceOptimizer(cost=truth.cost, elasticity=elasticity)
        price = assumed.best_price()
        realised = truth.profit(price)
        assumed_rows.append((elasticity, price, realised))
        print(f"  {elasticity:>19.2f} {price:>13.2f} {realised:>13,.0f} "
              f"{truth.profit(optimal) - realised:>13,.0f}")

    prices, quantities = observed_sales(truth)
    estimated = truth.estimate_elasticity(prices, quantities)
    fitted = PriceOptimizer(cost=truth.cost, elasticity=estimated)
    fitted_price = fitted.best_price()
    print(f"\n  elasticity estimated from 12 noisy observations: {estimated:.3f}"
          f" (true {truth.elasticity:.2f})")
    print(f"  price it recommends: {fitted_price:.2f} against the true "
          f"optimum {optimal:.2f}")
    gap = truth.profit(optimal) - truth.profit(fitted_price)
    print(f"  profit given up by that error: {gap:,.0f} "
          f"({gap / truth.profit(optimal):.2%})")

    grid = np.linspace(truth.cost + 0.5, truth.anchor * 3, 300)
    figure, axes = plt.subplots(1, 2, figsize=(9.5, 3.6))
    axes[0].plot(grid, truth.profit(grid), linewidth=1.6)
    axes[0].axvline(optimal, linestyle="--", linewidth=1.2,
                    label=f"optimum {optimal:.2f}")
    axes[0].axvline(fitted_price, linestyle=":", linewidth=1.2,
                    label=f"from estimate {fitted_price:.2f}")
    axes[0].set_xlabel("price")
    axes[0].set_ylabel("profit")
    axes[0].set_title("profit peaks, it does not climb")
    axes[0].legend(fontsize=8)

    axes[1].scatter(prices, quantities, s=18, label="observed sales")
    axes[1].plot(grid, truth.demand(grid), linewidth=1.2, label="true demand")
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("price (log)")
    axes[1].set_ylabel("quantity (log)")
    axes[1].set_title(f"elasticity is the slope here: {estimated:.2f}")
    axes[1].legend(fontsize=8)
    figure.tight_layout()
    plt.savefig("real_time_price_optimization.png", dpi=120,
                bbox_inches="tight")
    print("saved real_time_price_optimization.png")


if __name__ == "__main__":
    main()
