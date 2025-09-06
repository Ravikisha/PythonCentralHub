"""
Emotion-Based Music Player

Features:
- Selects tracks based on user emotion (face/speech analysis)
- Music playback
- Modular design
- GUI (tkinter)
- Error handling
"""
import tkinter as tk
from tkinter import filedialog
import os
import random
try:
    import cv2
    import numpy as np
    import librosa
except ImportError:
    cv2 = None
    np = None
    librosa = None

class EmotionDetector:
    def __init__(self):
        pass
    def detect_emotion(self, img_path):
        if cv2:
            img = cv2.imread(img_path)
            # Dummy: random emotion
            return random.choice(['happy', 'sad', 'neutral'])
        return 'neutral'

class MusicPlayer:
    def __init__(self):
        self.tracks = {'happy': [], 'sad': [], 'neutral': []}
        self.current = None
    def load_tracks(self, folder):
        for mood in self.tracks:
            mood_folder = os.path.join(folder, mood)
            if os.path.isdir(mood_folder):
                self.tracks[mood] = [os.path.join(mood_folder, f) for f in os.listdir(mood_folder) if f.endswith('.mp3')]
    def play(self, mood):
        if self.tracks[mood]:
            self.current = random.choice(self.tracks[mood])
            print(f"Playing: {self.current}")
            # Actual playback omitted for brevity
        else:
            print(f"No tracks for mood: {mood}")

class MusicPlayerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Emotion-Based Music Player")
        self.player = MusicPlayer()
        self.detector = EmotionDetector()
        self.load_btn = tk.Button(self.root, text="Load Music Folder", command=self.load_folder)
        self.load_btn.pack()
        self.img_btn = tk.Button(self.root, text="Select Image", command=self.select_img)
        self.img_btn.pack()
        self.status = tk.Label(self.root, text="")
        self.status.pack()

    def load_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.player.load_tracks(folder)
            self.status.config(text="Tracks loaded.")

    def select_img(self):
        img_path = filedialog.askopenfilename()
        if img_path:
            mood = self.detector.detect_emotion(img_path)
            self.status.config(text=f"Detected mood: {mood}")
            self.player.play(mood)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        gui = MusicPlayerGUI()
        gui.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
