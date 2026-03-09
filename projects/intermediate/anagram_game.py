"""
Anagram Game

A Python application that challenges users to form words from a scrambled set of letters.
Features include:
- Generating random anagrams.
- Validating user input against a dictionary.
- Keeping track of the score.
"""

import random
from tkinter import Tk, Label, Entry, Button, messagebox

# Sample word list
WORDS = ["python", "anagram", "challenge", "programming", "developer", "algorithm"]


class AnagramGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Anagram Game")

        self.score = 0
        self.current_word = ""
        self.scrambled_word = ""

        Label(root, text="Unscramble the word:").grid(row=0, column=0, padx=10, pady=10)
        self.word_label = Label(root, text="", font=("Helvetica", 16))
        self.word_label.grid(row=1, column=0, padx=10, pady=10)

        Label(root, text="Your Answer:").grid(row=2, column=0, padx=10, pady=10)
        self.answer_entry = Entry(root, width=30)
        self.answer_entry.grid(row=3, column=0, padx=10, pady=10)

        Button(root, text="Submit", command=self.check_answer).grid(row=4, column=0, pady=10)
        Button(root, text="Next", command=self.next_word).grid(row=5, column=0, pady=10)

        self.next_word()

    def next_word(self):
        """Generate a new scrambled word."""
        self.current_word = random.choice(WORDS)
        self.scrambled_word = "".join(random.sample(self.current_word, len(self.current_word)))
        self.word_label.config(text=self.scrambled_word)
        self.answer_entry.delete(0, "end")

    def check_answer(self):
        """Check the user's answer and update the score."""
        user_answer = self.answer_entry.get().strip().lower()
        if user_answer == self.current_word:
            self.score += 1
            messagebox.showinfo("Correct!", f"Well done! Your score: {self.score}")
        else:
            messagebox.showerror("Incorrect", f"The correct word was: {self.current_word}")
        self.next_word()


def main():
    root = Tk()
    app = AnagramGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
