import pandas as pd

class RealTimeInventoryManagement:
    def __init__(self):
        self.inventory = pd.DataFrame({'item': [], 'quantity': []})

    def add_item(self, item, quantity):
        self.inventory = self.inventory.append({'item': item, 'quantity': quantity}, ignore_index=True)
        print(f"Added {item} (x{quantity}) to inventory.")

    def list_inventory(self):
        print("Current inventory:")
        print(self.inventory)

    def demo(self):
        self.add_item('Widget', 10)
        self.add_item('Gadget', 5)
        self.list_inventory()

if __name__ == "__main__":
    print("Real-Time Inventory Management Demo")
    manager = RealTimeInventoryManagement()
    manager.demo()
