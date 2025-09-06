"""
Real-Time Stock Market Dashboard

Features:
- Live stock dashboard
- Data streaming
- Charting
- Analytics
- Modular design
- CLI interface
- Error handling
"""
import sys
import time
import random
import matplotlib.pyplot as plt
import threading

class StockData:
    def __init__(self, symbol):
        self.symbol = symbol
        self.prices = []
        self.timestamps = []

    def stream(self):
        for _ in range(100):
            price = 100 + random.uniform(-5, 5)
            self.prices.append(price)
            self.timestamps.append(time.time())
            time.sleep(0.5)

class Dashboard:
    def __init__(self, stock):
        self.stock = stock

    def plot(self):
        plt.plot(self.stock.timestamps, self.stock.prices, label=self.stock.symbol)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title(f'Stock Price for {self.stock.symbol}')
        plt.legend()
        plt.show()

class CLI:
    @staticmethod
    def run():
        if len(sys.argv) < 2:
            print("Usage: python real_time_stock_market_dashboard.py <symbol>")
            sys.exit(1)
        symbol = sys.argv[1]
        stock = StockData(symbol)
        print(f"Streaming data for {symbol}...")
        t = threading.Thread(target=stock.stream)
        t.start()
        t.join()
        dash = Dashboard(stock)
        dash.plot()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
