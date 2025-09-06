"""
Blockchain Implementation (Basic)

Features:
- Basic blockchain
- Transaction handling
- Validation
- Modular design
- CLI interface
- Error handling
"""
import hashlib
import json
import sys
import time

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
        return Block(0, time.time(), {"transactions": []}, "0")
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

class CLI:
    @staticmethod
    def run():
        bc = Blockchain()
        print("Blockchain Implementation (Basic)")
        while True:
            cmd = input('> ')
            if cmd.startswith('add'):
                parts = cmd.split(maxsplit=1)
                if len(parts) < 2:
                    print("Usage: add <data>")
                    continue
                data = json.loads(parts[1])
                bc.add_block(data)
                print("Block added.")
            elif cmd == 'validate':
                print(f"Blockchain valid: {bc.is_valid()}")
            elif cmd == 'exit':
                break
            else:
                print("Unknown command. Type 'add', 'validate', or 'exit'.")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
