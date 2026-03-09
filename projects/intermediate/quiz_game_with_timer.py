"""
Quiz Game with Timer

A Python-based quiz game where players must answer questions within a time limit. The game includes:
- A set of multiple-choice questions
- A timer for each question
- Score calculation based on correct answers
"""

import time
import threading
from tkinter import Tk, Label, Button, messagebox


class QuizGameWithTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Game with Timer")

        self.questions = [
            {"question": "What is the capital of France?", "options": ["Paris", "London", "Berlin", "Madrid"], "answer": "Paris"},
            {"question": "What is 5 + 7?", "options": ["10", "12", "14", "16"], "answer": "12"},
            {"question": "Which planet is known as the Red Planet?", "options": ["Earth", "Mars", "Jupiter", "Venus"], "answer": "Mars"},
        ]

        self.current_question_index = 0
        self.score = 0
        self.time_left = 10

        self.timer_thread = None
        self.timer_running = False

        self.setup_ui()
        self.display_question()

    def setup_ui(self):
        """Set up the user interface."""
        self.question_label = Label(self.root, text="", wraplength=400, font=("Arial", 14))
        self.question_label.pack(pady=20)

        self.option_buttons = []
        for i in range(4):
            button = Button(self.root, text="", command=lambda i=i: self.check_answer(i), width=20)
            button.pack(pady=5)
            self.option_buttons.append(button)

        self.timer_label = Label(self.root, text="Time left: 10 seconds", font=("Arial", 12))
        self.timer_label.pack(pady=10)

    def display_question(self):
        """Display the current question and options."""
        if self.current_question_index >= len(self.questions):
            self.end_game()
            return

        question_data = self.questions[self.current_question_index]
        self.question_label.config(text=question_data["question"])

        for i, option in enumerate(question_data["options"]):
            self.option_buttons[i].config(text=option)

        self.time_left = 10
        self.timer_label.config(text=f"Time left: {self.time_left} seconds")
        self.start_timer()

    def start_timer(self):
        """Start the countdown timer."""
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self.countdown)
        self.timer_thread.start()

    def countdown(self):
        """Countdown timer logic."""
        while self.time_left > 0 and self.timer_running:
            time.sleep(1)
            self.time_left -= 1
            self.timer_label.config(text=f"Time left: {self.time_left} seconds")

        if self.time_left == 0:
            self.timer_running = False
            self.root.after(0, self.time_up)

    def time_up(self):
        """Handle the event when time is up."""
        messagebox.showinfo("Time's Up!", "You ran out of time for this question.")
        self.next_question()

    def check_answer(self, index):
        """Check if the selected answer is correct."""
        if not self.timer_running:
            return

        self.timer_running = False
        question_data = self.questions[self.current_question_index]
        selected_option = self.option_buttons[index].cget("text")

        if selected_option == question_data["answer"]:
            self.score += 1

        self.next_question()

    def next_question(self):
        """Move to the next question."""
        self.current_question_index += 1
        self.display_question()

    def end_game(self):
        """End the game and display the score."""
        messagebox.showinfo("Game Over", f"Your score: {self.score}/{len(self.questions)}")
        self.root.destroy()


def main():
    root = Tk()
    app = QuizGameWithTimer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
