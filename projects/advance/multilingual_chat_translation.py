"""
Multilingual Chat Translation App

Features:
- Real-time chat
- Multi-language support
- Speech-to-text
- Modular design
- GUI (tkinter)
- Error handling
"""
import tkinter as tk
from tkinter import scrolledtext
import threading
import sys
try:
    from googletrans import Translator
    import speech_recognition as sr
except ImportError:
    Translator = None
    sr = None

class ChatApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Multilingual Chat Translation")
        self.translator = Translator() if Translator else None
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=60, height=20)
        self.text_area.pack()
        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack()
        self.lang_var = tk.StringVar(value='en')
        self.lang_menu = tk.OptionMenu(self.root, self.lang_var, 'en', 'fr', 'de', 'es', 'zh', 'hi')
        self.lang_menu.pack()
        self.send_btn = tk.Button(self.root, text="Send", command=self.send)
        self.send_btn.pack()
        self.speech_btn = tk.Button(self.root, text="Speech", command=self.speech)
        self.speech_btn.pack()

    def send(self):
        msg = self.entry.get()
        lang = self.lang_var.get()
        if self.translator:
            translated = self.translator.translate(msg, dest=lang).text
            self.text_area.insert(tk.END, f"You: {msg}\nTranslated: {translated}\n")
        else:
            self.text_area.insert(tk.END, f"You: {msg}\n")
        self.entry.delete(0, tk.END)

    def speech(self):
        if sr:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                self.text_area.insert(tk.END, "Listening...\n")
                audio = recognizer.listen(source)
                try:
                    msg = recognizer.recognize_google(audio)
                    self.entry.delete(0, tk.END)
                    self.entry.insert(0, msg)
                except Exception as e:
                    self.text_area.insert(tk.END, f"Speech error: {e}\n")
        else:
            self.text_area.insert(tk.END, "Speech recognition not available.\n")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = ChatApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
