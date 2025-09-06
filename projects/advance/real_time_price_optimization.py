import numpy as np
from scipy.optimize import minimize

class RealTimePriceOptimization:
    def __init__(self):
        pass

    def optimize_price(self, cost, demand):
        def profit(price):
            return -(price - cost) * demand(price)
        result = minimize(profit, x0=[cost+10])
        print(f"Optimal price: {result.x[0]:.2f}")
        return result.x[0]

    def demo(self):
        cost = 50
        demand = lambda p: max(100 - 2*p, 0)
        self.optimize_price(cost, demand)

if __name__ == "__main__":
    print("Real-Time Price Optimization Demo")
    optimizer = RealTimePriceOptimization()
    optimizer.demo()
