"""
Financial Portfolio Optimizer

Features:
- Risk analysis
- Monte Carlo simulation
- Portfolio optimization
- Reporting
- CLI interface
- Error handling
"""
import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
from scipy.optimize import minimize

class Portfolio:
    def __init__(self, returns):
        self.returns = returns
        self.num_assets = returns.shape[1]

    def statistics(self, weights):
        port_return = np.sum(self.returns.mean() * weights) * 252
        port_vol = np.sqrt(np.dot(weights.T, np.dot(self.returns.cov() * 252, weights)))
        return port_return, port_vol

    def simulate(self, num_portfolios=5000):
        results = np.zeros((3, num_portfolios))
        weights_record = []
        for i in range(num_portfolios):
            weights = np.random.random(self.num_assets)
            weights /= np.sum(weights)
            port_return, port_vol = self.statistics(weights)
            results[0,i] = port_return
            results[1,i] = port_vol
            results[2,i] = results[0,i] / results[1,i]
            weights_record.append(weights)
        return results, weights_record

    def optimize(self):
        def neg_sharpe(weights):
            ret, vol = self.statistics(weights)
            return -ret/vol
        constraints = ({'type':'eq','fun':lambda x: np.sum(x)-1})
        bounds = tuple((0,1) for _ in range(self.num_assets))
        result = minimize(neg_sharpe, self.num_assets*[1./self.num_assets], bounds=bounds, constraints=constraints)
        return result.x

class CLI:
    @staticmethod
    def run():
        if len(sys.argv) < 2:
            print("Usage: python financial_portfolio_optimizer.py <returns_csv>")
            sys.exit(1)
        returns_csv = sys.argv[1]
        df = pd.read_csv(returns_csv)
        returns = df.pct_change().dropna()
        portfolio = Portfolio(returns)
        print("Simulating portfolios...")
        results, weights_record = portfolio.simulate()
        max_sharpe_idx = np.argmax(results[2])
        print(f"Max Sharpe Ratio Portfolio Return: {results[0,max_sharpe_idx]:.2f}")
        print(f"Max Sharpe Ratio Portfolio Volatility: {results[1,max_sharpe_idx]:.2f}")
        print(f"Weights: {weights_record[max_sharpe_idx]}")
        print("Optimizing portfolio...")
        opt_weights = portfolio.optimize()
        print(f"Optimized Weights: {opt_weights}")
        plt.scatter(results[1], results[0], c=results[2], cmap='viridis')
        plt.xlabel('Volatility')
        plt.ylabel('Return')
        plt.colorbar(label='Sharpe Ratio')
        plt.show()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
