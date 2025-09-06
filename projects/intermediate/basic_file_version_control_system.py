"""
Basic File Version Control System

A Python-based version control system with the following features:
- Track changes to files
- Commit changes with messages
- Revert to previous versions
"""

import os
import hashlib
import pickle
from datetime import datetime


class BasicFileVersionControl:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.version_file = os.path.join(repo_path, ".versions.pkl")
        self.versions = {}

        if not os.path.exists(repo_path):
            os.makedirs(repo_path)

        if os.path.exists(self.version_file):
            with open(self.version_file, "rb") as f:
                self.versions = pickle.load(f)

    def hash_file(self, file_path):
        """Generate a hash for the given file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def commit(self, file_path, message):
        """Commit changes to the file."""
        if not os.path.exists(file_path):
            print("File does not exist.")
            return

        file_hash = self.hash_file(file_path)
        file_name = os.path.basename(file_path)

        if file_name in self.versions and self.versions[file_name]["hash"] == file_hash:
            print("No changes detected.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        version_data = {
            "hash": file_hash,
            "timestamp": timestamp,
            "message": message,
            "content": open(file_path, "rb").read(),
        }

        self.versions[file_name] = version_data

        with open(self.version_file, "wb") as f:
            pickle.dump(self.versions, f)

        print(f"Committed {file_name} at {timestamp} with message: {message}")

    def revert(self, file_name):
        """Revert the file to the last committed version."""
        if file_name not in self.versions:
            print("No version history found for this file.")
            return

        with open(os.path.join(self.repo_path, file_name), "wb") as f:
            f.write(self.versions[file_name]["content"])

        print(f"Reverted {file_name} to the last committed version.")

    def log(self, file_name):
        """Display the commit history for the file."""
        if file_name not in self.versions:
            print("No version history found for this file.")
            return

        version_data = self.versions[file_name]
        print(f"File: {file_name}")
        print(f"Last Commit: {version_data['timestamp']}")
        print(f"Message: {version_data['message']}")


def main():
    repo_path = "./repo"
    vcs = BasicFileVersionControl(repo_path)

    while True:
        print("\nBasic File Version Control System")
        print("1. Commit File")
        print("2. Revert File")
        print("3. View Log")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            file_path = input("Enter the file path to commit: ")
            message = input("Enter commit message: ")
            vcs.commit(file_path, message)
        elif choice == "2":
            file_name = input("Enter the file name to revert: ")
            vcs.revert(file_name)
        elif choice == "3":
            file_name = input("Enter the file name to view log: ")
            vcs.log(file_name)
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
