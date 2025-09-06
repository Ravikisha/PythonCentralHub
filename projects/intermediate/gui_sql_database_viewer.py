"""
GUI-based SQL Database Viewer

A Python application with a graphical user interface to view and interact with SQL databases. Features include:
- Connecting to a database.
- Executing SQL queries.
- Displaying query results in a table format.
"""

import sqlite3
from tkinter import Tk, Label, Entry, Button, Text, Scrollbar, messagebox, END
from tkinter.ttk import Treeview


class SQLDatabaseViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Database Viewer")

        Label(root, text="Database Path:").grid(row=0, column=0, padx=10, pady=10)
        self.db_entry = Entry(root, width=50)
        self.db_entry.grid(row=0, column=1, padx=10, pady=10)

        Button(root, text="Connect", command=self.connect_to_db).grid(row=0, column=2, padx=10, pady=10)

        Label(root, text="Enter SQL Query:").grid(row=1, column=0, padx=10, pady=10)
        self.query_text = Text(root, height=5, width=60)
        self.query_text.grid(row=1, column=1, columnspan=2, padx=10, pady=10)

        Button(root, text="Execute", command=self.execute_query).grid(row=2, column=1, pady=10)

        self.result_tree = Treeview(root, columns=("#1", "#2", "#3"), show="headings")
        self.result_tree.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        scrollbar = Scrollbar(root, command=self.result_tree.yview)
        scrollbar.grid(row=3, column=3, sticky="ns")
        self.result_tree.configure(yscrollcommand=scrollbar.set)

        self.connection = None

    def connect_to_db(self):
        """Connect to the SQLite database."""
        db_path = self.db_entry.get()
        try:
            self.connection = sqlite3.connect(db_path)
            messagebox.showinfo("Success", "Connected to the database successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to connect to the database: {e}")

    def execute_query(self):
        """Execute the SQL query and display results."""
        if not self.connection:
            messagebox.showerror("Error", "Please connect to a database first.")
            return

        query = self.query_text.get("1.0", END).strip()
        if not query:
            messagebox.showerror("Error", "Please enter an SQL query.")
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()

            # Clear previous results
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)

            # Display results
            columns = [description[0] for description in cursor.description] if cursor.description else []
            self.result_tree["columns"] = columns

            for col in columns:
                self.result_tree.heading(col, text=col)

            for row in cursor.fetchall():
                self.result_tree.insert("", END, values=row)

            messagebox.showinfo("Success", "Query executed successfully.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to execute query: {e}")


def main():
    root = Tk()
    app = SQLDatabaseViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
