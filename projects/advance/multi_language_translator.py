"""
Multi-language Translator

Features:
- Multi-language translation
- API integration
- GUI (tkinter)
- Modular design
- Error handling
"""
import tkinter as tk
from tkinter import scrolledtext
import sys
try:
    from googletrans import Translator
except ImportError:
    Translator = None

class TranslatorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Multi-language Translator")
        self.translator = Translator() if Translator else None
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=60, height=20)
        self.text_area.pack()
        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack()
        self.lang_var = tk.StringVar(value='en')
        self.lang_menu = tk.OptionMenu(self.root, self.lang_var, 'en', 'fr', 'de', 'es', 'zh', 'hi')
        self.lang_menu.pack()
        self.send_btn = tk.Button(self.root, text="Translate", command=self.translate)
        self.send_btn.pack()
    def translate(self):
        msg = self.entry.get()
        lang = self.lang_var.get()
        if self.translator:
            translated = self.translator.translate(msg, dest=lang).text
            self.text_area.insert(tk.END, f"Original: {msg}\nTranslated: {translated}\n")
        else:
            self.text_area.insert(tk.END, f"Original: {msg}\n")
        self.entry.delete(0, tk.END)
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = TranslatorApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
