"""Real-time inventory management.

An append-only event log of receipts and sales, replayed to give stock on hand
at any moment. Each SKU has a reorder point and a lead time, so the interesting
output is not the stock level but the count of **stockouts** -- the times demand
arrived and there was nothing to sell.
"""

from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np


class InventoryLedger:
    """Append-only events; stock is always derived, never edited in place.

    Storing the events rather than a running total is what makes the history
    auditable: any stock figure can be traced to the movements that produced it.
    """

    def __init__(self):
        self.events = []

    def receive(self, period, sku, quantity):
        self.events.append((period, sku, "receive", int(quantity)))

    def sell(self, period, sku, quantity):
        self.events.append((period, sku, "sell", int(quantity)))

    def on_hand(self, sku=None):
        totals = defaultdict(int)
        for _, item, kind, quantity in self.events:
            totals[item] += quantity if kind == "receive" else -quantity
        return totals if sku is None else totals[sku]

    def history(self, sku):
        level, out = 0, []
        for _, item, kind, quantity in self.events:
            if item != sku:
                continue
            level += quantity if kind == "receive" else -quantity
            out.append(level)
        return out


class ReorderPolicy:
    """Order `quantity` whenever stock falls to `point`; arrives after `lead`."""

    def __init__(self, point, quantity, lead=3):
        self.point = point
        self.quantity = quantity
        self.lead = lead


def simulate(policy, periods=120, mean_demand=8.0, seed=0):
    rng = np.random.default_rng(seed)
    ledger = InventoryLedger()
    ledger.receive(0, "WIDGET", policy.quantity)
    incoming, stockouts, lost = {}, 0, 0

    for period in range(1, periods + 1):
        if period in incoming:
            ledger.receive(period, "WIDGET", incoming.pop(period))

        demand = int(rng.poisson(mean_demand))
        available = ledger.on_hand("WIDGET")
        sold = min(demand, available)
        if sold:
            ledger.sell(period, "WIDGET", sold)
        if demand > available:
            stockouts += 1
            lost += demand - available

        outstanding = sum(incoming.values())
        if ledger.on_hand("WIDGET") + outstanding <= policy.point:
            incoming[period + policy.lead] = (
                incoming.get(period + policy.lead, 0) + policy.quantity)

    return {"ledger": ledger, "stockouts": stockouts, "lost": lost,
            "events": len(ledger.events),
            "levels": ledger.history("WIDGET")}


def main():
    print("Real-Time Inventory Management")
    print(f"  {'reorder point':>14} {'order qty':>10} {'stockouts':>10} "
          f"{'lost units':>11} {'mean stock':>11}")

    results = []
    for point in (10, 25, 40, 60):
        policy = ReorderPolicy(point=point, quantity=60)
        result = simulate(policy)
        levels = np.asarray(result["levels"], dtype=float)
        results.append((point, result, levels.mean()))
        print(f"  {point:>14} {policy.quantity:>10} "
              f"{result['stockouts']:>10} {result['lost']:>11} "
              f"{levels.mean():>11.1f}")

    best = min(results, key=lambda row: (row[1]["stockouts"], row[2]))
    print(f"\n  fewest stockouts at reorder point {best[0]} "
          f"({best[1]['stockouts']} over 120 periods)")
    print("  holding more stock buys fewer stockouts and costs carrying space")
    print(f"  every figure above is derived from "
          f"{best[1]['events']} logged events, not a stored total")

    figure, axes = plt.subplots(1, 2, figsize=(9.5, 3.6))
    for point, result, _ in results:
        axes[0].plot(result["levels"], linewidth=1.1,
                     label=f"reorder at {point}")
    axes[0].axhline(0, color="black", linewidth=0.8, linestyle=":")
    axes[0].set_xlabel("movement")
    axes[0].set_ylabel("units on hand")
    axes[0].set_title("stock derived from the event log")
    axes[0].legend(fontsize=7)

    points = [row[0] for row in results]
    axes[1].bar([str(p) for p in points],
                [row[1]["stockouts"] for row in results])
    for index, row in enumerate(results):
        axes[1].annotate(str(row[1]["stockouts"]), (index, row[1]["stockouts"]),
                         ha="center", va="bottom", fontsize=8)
    axes[1].set_xlabel("reorder point")
    axes[1].set_ylabel("periods with a stockout")
    axes[1].set_title("the number the policy is chosen on")
    figure.tight_layout()
    plt.savefig("real_time_inventory_management.png", dpi=120,
                bbox_inches="tight")
    print("saved real_time_inventory_management.png")


if __name__ == "__main__":
    main()
