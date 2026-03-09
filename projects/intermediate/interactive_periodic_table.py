"""
Interactive Periodic Table

A Python application that displays an interactive periodic table. Features include:
- Displaying information about elements when clicked.
- Searching for elements by name or symbol.
"""

import tkinter as tk
from tkinter import messagebox

# Sample data for the periodic table
elements = [
    {"symbol": "H", "name": "Hydrogen", "atomic_number": 1, "atomic_mass": 1.008},
    {"symbol": "He", "name": "Helium", "atomic_number": 2, "atomic_mass": 4.0026},
    {"symbol": "Li", "name": "Lithium", "atomic_number": 3, "atomic_mass": 6.94},
    {"symbol": "Be", "name": "Beryllium", "atomic_number": 4, "atomic_mass": 9.0122},
    {"symbol": "B", "name": "Boron", "atomic_number": 5, "atomic_mass": 10.81},
    {"symbol": "C", "name": "Carbon", "atomic_number": 6, "atomic_mass": 12.011},
    {"symbol": "N", "name": "Nitrogen", "atomic_number": 7, "atomic_mass": 14.007},
    {"symbol": "O", "name": "Oxygen", "atomic_number": 8, "atomic_mass": 15.999},
    {"symbol": "F", "name": "Fluorine", "atomic_number": 9, "atomic_mass": 18.998},
    {"symbol": "Ne", "name": "Neon", "atomic_number": 10, "atomic_mass": 20.180},
]


class InteractivePeriodicTable:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Periodic Table")

        self.create_table()

    def create_table(self):
        """Create the periodic table layout."""
        for i, element in enumerate(elements):
            button = tk.Button(
                self.root,
                text=element["symbol"],
                width=10,
                height=3,
                command=lambda e=element: self.show_element_info(e),
            )
            button.grid(row=i // 5, column=i % 5, padx=5, pady=5)

    def show_element_info(self, element):
        """Display information about the selected element."""
        info = (
            f"Name: {element['name']}\n"
            f"Symbol: {element['symbol']}\n"
            f"Atomic Number: {element['atomic_number']}\n"
            f"Atomic Mass: {element['atomic_mass']}"
        )
        messagebox.showinfo("Element Information", info)


def main():
    root = tk.Tk()
    app = InteractivePeriodicTable(root)
    root.mainloop()


if __name__ == "__main__":
    main()
