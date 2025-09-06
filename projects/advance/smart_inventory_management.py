"""
Smart Inventory Management System

Features:
- Demand forecasting
- Restock alerts
- Reporting
- Modular design
- CLI interface
- Error handling
"""
import sys
import json
import random
from collections import defaultdict

class InventoryItem:
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity

class InventoryManager:
    def __init__(self):
        self.items = defaultdict(int)
        self.history = defaultdict(list)

    def add_item(self, name, quantity):
        self.items[name] += quantity
        self.history[name].append(quantity)

    def forecast(self, name):
        hist = self.history[name]
        if len(hist) < 2:
            return hist[-1] if hist else 0
        return int(sum(hist[-5:])/min(5, len(hist)))

    def restock_alert(self, name):
        forecast = self.forecast(name)
        if self.items[name] < forecast:
            print(f"Restock alert for {name}! Current: {self.items[name]}, Forecast: {forecast}")

    def report(self):
        print("Inventory Report:")
        for name, qty in self.items.items():
            print(f"{name}: {qty}")
            self.restock_alert(name)

    def save(self, filename):
        data = {name: qty for name, qty in self.items.items()}
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

class CLI:
    @staticmethod
    def run():
        im = InventoryManager()
        print("Smart Inventory Management System")
        while True:
            cmd = input('> ')
            if cmd.startswith('add'):
                parts = cmd.split()
                if len(parts) < 3:
                    print("Usage: add <name> <quantity>")
                    continue
                name, quantity = parts[1], int(parts[2])
                im.add_item(name, quantity)
                print("Item added.")
            elif cmd == 'report':
                im.report()
            elif cmd.startswith('save'):
                parts = cmd.split()
                filename = parts[1] if len(parts) > 1 else 'inventory_data.json'
                im.save(filename)
                print(f"Data saved to {filename}")
            elif cmd == 'exit':
                break
            else:
                print("Unknown command")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
