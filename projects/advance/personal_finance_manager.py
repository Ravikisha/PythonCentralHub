"""
Personal Finance Manager

Features:
- Budgeting
- Analytics
- Reporting
- Modular design
- CLI interface
- Error handling
"""
import sys
import json
import datetime
from collections import defaultdict

class Transaction:
    def __init__(self, date, amount, category, desc):
        self.date = date
        self.amount = amount
        self.category = category
        self.desc = desc

class FinanceManager:
    def __init__(self):
        self.transactions = []
        self.budget = defaultdict(float)

    def add_transaction(self, date, amount, category, desc):
        self.transactions.append(Transaction(date, amount, category, desc))

    def set_budget(self, category, amount):
        self.budget[category] = amount

    def report(self):
        summary = defaultdict(float)
        for t in self.transactions:
            summary[t.category] += t.amount
        print("Budget Report:")
        for cat, spent in summary.items():
            budget = self.budget.get(cat, 0)
            print(f"{cat}: Spent={spent}, Budget={budget}, Remaining={budget-spent}")

    def save(self, filename):
        data = [{"date": t.date, "amount": t.amount, "category": t.category, "desc": t.desc} for t in self.transactions]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

class CLI:
    @staticmethod
    def run():
        fm = FinanceManager()
        print("Personal Finance Manager")
        while True:
            cmd = input('> ')
            if cmd.startswith('add'):
                parts = cmd.split()
                if len(parts) < 5:
                    print("Usage: add <date> <amount> <category> <desc>")
                    continue
                date, amount, category, desc = parts[1], float(parts[2]), parts[3], ' '.join(parts[4:])
                fm.add_transaction(date, amount, category, desc)
                print("Transaction added.")
            elif cmd.startswith('budget'):
                parts = cmd.split()
                if len(parts) < 3:
                    print("Usage: budget <category> <amount>")
                    continue
                category, amount = parts[1], float(parts[2])
                fm.set_budget(category, amount)
                print("Budget set.")
            elif cmd == 'report':
                fm.report()
            elif cmd.startswith('save'):
                parts = cmd.split()
                filename = parts[1] if len(parts) > 1 else 'finance_data.json'
                fm.save(filename)
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
