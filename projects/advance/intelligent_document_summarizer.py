"""
Intelligent Document Summarizer

Features:
- Document summarization using NLP
- Keyword extraction
- GUI (tkinter)
- Modular design
- Error handling
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import re
from collections import Counter
try:
    from gensim.summarization import summarize
except ImportError:
    summarize = None

class Summarizer:
    def __init__(self):
        pass
    def extract_keywords(self, text):
        words = re.findall(r'\w+', text.lower())
        freq = Counter(words)
        return [w for w, c in freq.most_common(10)]
    def summarize_text(self, text):
        if summarize:
            return summarize(text)
        else:
            return '\n'.join(text.split('.')[:3])

class SummarizerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Document Summarizer")
        self.text = tk.Text(self.root, width=80, height=20)
        self.text.pack()
        self.summary = tk.Text(self.root, width=80, height=10)
        self.summary.pack()
        self.keywords = tk.Label(self.root, text="Keywords:")
        self.keywords.pack()
        self.open_btn = tk.Button(self.root, text="Open Document", command=self.open_doc)
        self.open_btn.pack()
        self.summarize_btn = tk.Button(self.root, text="Summarize", command=self.summarize)
        self.summarize_btn.pack()
        self.summarizer = Summarizer()

    def open_doc(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text.delete('1.0', tk.END)
            self.text.insert(tk.END, content)

    def summarize(self):
        content = self.text.get('1.0', tk.END)
        summary = self.summarizer.summarize_text(content)
        self.summary.delete('1.0', tk.END)
        self.summary.insert(tk.END, summary)
        keywords = self.summarizer.extract_keywords(content)
        self.keywords.config(text=f"Keywords: {', '.join(keywords)}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        gui = SummarizerGUI()
        gui.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
