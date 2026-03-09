"""
Cryptocurrency Wallet

Features:
- Transaction management
- Security
- Modular design
- CLI interface
- Error handling
"""
import sys
import os
import json
import random
import hashlib

class Wallet:
    def __init__(self):
        self.balance = 0
        self.transactions = []
        self.address = self.generate_address()
    def generate_address(self):
        return hashlib.sha256(str(random.random()).encode()).hexdigest()
    def send(self, amount, to_addr):
        if amount > self.balance:
            print("Insufficient balance.")
            return False
        self.balance -= amount
        self.transactions.append({'to': to_addr, 'amount': amount})
        print(f"Sent {amount} to {to_addr}")
        return True
    def receive(self, amount, from_addr):
        self.balance += amount
        self.transactions.append({'from': from_addr, 'amount': amount})
        print(f"Received {amount} from {from_addr}")
    def show(self):
        print(f"Address: {self.address}")
        print(f"Balance: {self.balance}")
        print("Transactions:")
        for t in self.transactions:
            print(t)
    def save(self, filename):
        data = {'address': self.address, 'balance': self.balance, 'transactions': self.transactions}
        with open(filename, 'w') as f:
            json.dump(data, f)
    def load(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                self.address = data['address']
                self.balance = data['balance']
                self.transactions = data['transactions']

class CLI:
    @staticmethod
    def run():
        wallet = Wallet()
        wallet.load('wallet.json')
        print("Cryptocurrency Wallet")
        print("Commands: send <amount> <to_addr>, receive <amount> <from_addr>, show, save, exit")
        while True:
            cmd = input('> ')
            if cmd.startswith('send'):
                parts = cmd.split()
                if len(parts) < 3:
                    print("Usage: send <amount> <to_addr>")
                    continue
                wallet.send(float(parts[1]), parts[2])
            elif cmd.startswith('receive'):
                parts = cmd.split()
                if len(parts) < 3:
                    print("Usage: receive <amount> <from_addr>")
                    continue
                wallet.receive(float(parts[1]), parts[2])
            elif cmd == 'show':
                wallet.show()
            elif cmd == 'save':
                wallet.save('wallet.json')
                print("Wallet saved.")
            elif cmd == 'exit':
                wallet.save('wallet.json')
                break
            else:
                print("Unknown command.")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
