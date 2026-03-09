"""
File Synchronization Tool

A tool to synchronize files between two directories with the following features:
- Detect and copy new or updated files
- Delete files that no longer exist in the source directory
- Provide a summary of synchronization actions
"""

import os
import shutil
from tkinter import Tk, Label, Entry, Button, messagebox, filedialog


class FileSynchronizationTool:
    def __init__(self, root):
        self.root = root
        self.root.title("File Synchronization Tool")

        self.source_dir = ""
        self.target_dir = ""

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        Label(self.root, text="Source Directory:").grid(row=0, column=0, padx=10, pady=10)
        self.source_entry = Entry(self.root, width=50)
        self.source_entry.grid(row=0, column=1, padx=10, pady=10)
        Button(self.root, text="Browse", command=self.browse_source).grid(row=0, column=2, padx=10, pady=10)

        Label(self.root, text="Target Directory:").grid(row=1, column=0, padx=10, pady=10)
        self.target_entry = Entry(self.root, width=50)
        self.target_entry.grid(row=1, column=1, padx=10, pady=10)
        Button(self.root, text="Browse", command=self.browse_target).grid(row=1, column=2, padx=10, pady=10)

        Button(self.root, text="Synchronize", command=self.synchronize).grid(row=2, column=0, columnspan=3, pady=20)

    def browse_source(self):
        """Browse for the source directory."""
        self.source_dir = filedialog.askdirectory()
        self.source_entry.delete(0, "end")
        self.source_entry.insert(0, self.source_dir)

    def browse_target(self):
        """Browse for the target directory."""
        self.target_dir = filedialog.askdirectory()
        self.target_entry.delete(0, "end")
        self.target_entry.insert(0, self.target_dir)

    def synchronize(self):
        """Synchronize files between the source and target directories."""
        if not self.source_dir or not self.target_dir:
            messagebox.showerror("Error", "Both source and target directories must be selected.")
            return

        if not os.path.exists(self.source_dir):
            messagebox.showerror("Error", "Source directory does not exist.")
            return

        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)

        actions = []

        # Copy new and updated files
        for root, dirs, files in os.walk(self.source_dir):
            relative_path = os.path.relpath(root, self.source_dir)
            target_root = os.path.join(self.target_dir, relative_path)

            if not os.path.exists(target_root):
                os.makedirs(target_root)

            for file in files:
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_root, file)

                if not os.path.exists(target_file) or os.path.getmtime(source_file) > os.path.getmtime(target_file):
                    shutil.copy2(source_file, target_file)
                    actions.append(f"Copied: {source_file} -> {target_file}")

        # Delete files that no longer exist in the source directory
        for root, dirs, files in os.walk(self.target_dir):
            relative_path = os.path.relpath(root, self.target_dir)
            source_root = os.path.join(self.source_dir, relative_path)

            for file in files:
                target_file = os.path.join(root, file)
                source_file = os.path.join(source_root, file)

                if not os.path.exists(source_file):
                    os.remove(target_file)
                    actions.append(f"Deleted: {target_file}")

        # Show summary
        if actions:
            messagebox.showinfo("Synchronization Complete", "\n".join(actions))
        else:
            messagebox.showinfo("Synchronization Complete", "No changes were made.")


def main():
    root = Tk()
    app = FileSynchronizationTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()
