"""
Blockchain-Based Voting System

Features:
- Secure voting using blockchain
- User authentication
- Result dashboard
- Modular design
- CLI interface
- Error handling
"""
import hashlib
import json
import sys
import time
from collections import defaultdict

class Block:
    def __init__(self, index, timestamp, data, prev_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, time.time(), {"votes": {}}, "0")

    def add_block(self, data):
        prev = self.chain[-1]
        block = Block(len(self.chain), time.time(), data, prev.hash)
        self.chain.append(block)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            if self.chain[i].prev_hash != self.chain[i-1].hash:
                return False
            if self.chain[i].hash != self.chain[i].compute_hash():
                return False
        return True

class VotingSystem:
    def __init__(self):
        self.blockchain = Blockchain()
        self.users = {"alice": "pass1", "bob": "pass2", "carol": "pass3"}
        self.votes = defaultdict(str)
        self.candidates = ["A", "B", "C"]

    def authenticate(self, user, pwd):
        return self.users.get(user) == pwd

    def vote(self, user, candidate):
        if candidate not in self.candidates:
            raise ValueError("Invalid candidate")
        self.votes[user] = candidate
        self.blockchain.add_block({"user": user, "vote": candidate})

    def results(self):
        tally = defaultdict(int)
        for v in self.votes.values():
            tally[v] += 1
        return dict(tally)

    def dashboard(self):
        print("Voting Results:")
        for c, v in self.results().items():
            print(f"{c}: {v}")
        print(f"Blockchain valid: {self.blockchain.is_valid()}")

class CLI:
    @staticmethod
    def run():
        system = VotingSystem()
        print("Candidates: A, B, C")
        while True:
            user = input("Username: ")
            pwd = input("Password: ")
            if not system.authenticate(user, pwd):
                print("Authentication failed.")
                continue
            print("Vote for (A/B/C): ")
            candidate = input().strip().upper()
            try:
                system.vote(user, candidate)
                print("Vote recorded.")
            except Exception as e:
                print(f"Error: {e}")
            if input("Show dashboard? (y/n): ").lower() == 'y':
                system.dashboard()
            if input("Exit? (y/n): ").lower() == 'y':
                break

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
