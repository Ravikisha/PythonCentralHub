# Morse Code Audio Player

import numpy as np
import pygame
import time
import threading
from typing import Dict, List, Optional
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import io
import wave
from datetime import datetime

class MorseCodeAudio:
    def __init__(self, frequency: int = 600, wpm: int = 20, sample_rate: int = 44100):
        """
        Initialize Morse Code Audio Player
        
        Args:
            frequency: Tone frequency in Hz
            wpm: Words per minute
            sample_rate: Audio sample rate
        """
        self.frequency = frequency
        self.wpm = wpm
        self.sample_rate = sample_rate
        
        # Morse code dictionary
        self.morse_code = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--',
            '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
            '9': '----.', '0': '-----', '.': '.-.-.-', ',': '--..--', '?': '..--..',
            "'": '.----.', '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-',
            '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-', '+': '.-.-.',
            '-': '-....-', '_': '..--.-', '"': '.-..-.', '$': '...-..-', '@': '.--.-.',
            ' ': '/'  # Space between words
        }
        
        # Reverse mapping for decoding
        self.reverse_morse = {v: k for k, v in self.morse_code.items()}
        
        # Timing calculations (based on WPM)
        self.calculate_timings()
        
        # Initialize pygame mixer
        pygame.mixer.pre_init(frequency=self.sample_rate, size=-16, channels=1, buffer=512)
        pygame.mixer.init()
        
        # Audio control
        self.is_playing = False
        self.stop_playback = False
        
    def calculate_timings(self):
        """Calculate timing for dots, dashes, and spaces based on WPM"""
        # Standard: PARIS = 50 units, 1 WPM = 50 units per minute
        unit_time = 60.0 / (50 * self.wpm)
        
        self.dot_duration = unit_time
        self.dash_duration = 3 * unit_time
        self.inter_element_gap = unit_time
        self.inter_letter_gap = 3 * unit_time
        self.inter_word_gap = 7 * unit_time
    
    def generate_tone(self, duration: float) -> np.ndarray:
        """Generate a sine wave tone"""
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)
        
        # Generate sine wave
        wave = np.sin(2 * np.pi * self.frequency * t)
        
        # Apply envelope to avoid clicks
        fade_samples = int(0.01 * self.sample_rate)  # 10ms fade
        if samples > 2 * fade_samples:
            # Fade in
            wave[:fade_samples] *= np.linspace(0, 1, fade_samples)
            # Fade out
            wave[-fade_samples:] *= np.linspace(1, 0, fade_samples)
        
        # Convert to 16-bit PCM
        wave = (wave * 32767).astype(np.int16)
        return wave
    
    def generate_silence(self, duration: float) -> np.ndarray:
        """Generate silence"""
        samples = int(duration * self.sample_rate)
        return np.zeros(samples, dtype=np.int16)
    
    def text_to_morse(self, text: str) -> str:
        """Convert text to morse code"""
        morse = []
        for char in text.upper():
            if char in self.morse_code:
                morse.append(self.morse_code[char])
            elif char == ' ':
                morse.append('/')
            else:
                morse.append('?')  # Unknown character
        
        return ' '.join(morse)
    
    def morse_to_text(self, morse: str) -> str:
        """Convert morse code to text"""
        # Handle different separators
        morse = morse.replace('/', ' / ')  # Ensure word separators are spaced
        morse_chars = morse.split()
        
        text = []
        for morse_char in morse_chars:
            if morse_char == '/':
                text.append(' ')
            elif morse_char in self.reverse_morse:
                text.append(self.reverse_morse[morse_char])
            else:
                text.append('?')  # Unknown morse code
        
        return ''.join(text)
    
    def create_audio_from_text(self, text: str) -> np.ndarray:
        """Create audio data from text"""
        audio_data = []
        
        for i, char in enumerate(text.upper()):
            if self.stop_playback:
                break
                
            if char == ' ':
                # Inter-word gap
                audio_data.append(self.generate_silence(self.inter_word_gap))
            elif char in self.morse_code:
                morse_char = self.morse_code[char]
                
                # Convert each dot/dash to audio
                for j, symbol in enumerate(morse_char):
                    if symbol == '.':
                        audio_data.append(self.generate_tone(self.dot_duration))
                    elif symbol == '-':
                        audio_data.append(self.generate_tone(self.dash_duration))
                    
                    # Inter-element gap (except after last symbol)
                    if j < len(morse_char) - 1:
                        audio_data.append(self.generate_silence(self.inter_element_gap))
                
                # Inter-letter gap (except after last character)
                if i < len(text) - 1 and text[i + 1] != ' ':
                    audio_data.append(self.generate_silence(self.inter_letter_gap))
        
        if audio_data:
            return np.concatenate(audio_data)
        else:
            return np.array([], dtype=np.int16)
    
    def create_audio_from_morse(self, morse: str) -> np.ndarray:
        """Create audio data from morse code"""
        audio_data = []
        morse_chars = morse.split()
        
        for i, morse_char in enumerate(morse_chars):
            if self.stop_playback:
                break
                
            if morse_char == '/':
                # Inter-word gap
                audio_data.append(self.generate_silence(self.inter_word_gap))
            else:
                # Convert each dot/dash to audio
                for j, symbol in enumerate(morse_char):
                    if symbol == '.':
                        audio_data.append(self.generate_tone(self.dot_duration))
                    elif symbol == '-':
                        audio_data.append(self.generate_tone(self.dash_duration))
                    
                    # Inter-element gap (except after last symbol)
                    if j < len(morse_char) - 1:
                        audio_data.append(self.generate_silence(self.inter_element_gap))
                
                # Inter-letter gap (except after last character)
                if i < len(morse_chars) - 1 and morse_chars[i + 1] != '/':
                    audio_data.append(self.generate_silence(self.inter_letter_gap))
        
        if audio_data:
            return np.concatenate(audio_data)
        else:
            return np.array([], dtype=np.int16)
    
    def play_audio_data(self, audio_data: np.ndarray, callback=None):
        """Play audio data using pygame"""
        if len(audio_data) == 0:
            return
        
        # Convert to bytes
        audio_bytes = audio_data.tobytes()
        
        # Create pygame sound object
        sound = pygame.sndarray.make_sound(audio_data.reshape(-1, 1))
        
        # Play sound
        channel = sound.play()
        
        # Wait for playback to finish or stop signal
        while channel.get_busy() and not self.stop_playback:
            time.sleep(0.1)
            if callback:
                callback()
        
        if self.stop_playback:
            channel.stop()
    
    def play_text(self, text: str, callback=None):
        """Play text as morse code"""
        self.is_playing = True
        self.stop_playback = False
        
        audio_data = self.create_audio_from_text(text)
        self.play_audio_data(audio_data, callback)
        
        self.is_playing = False
    
    def play_morse(self, morse: str, callback=None):
        """Play morse code"""
        self.is_playing = True
        self.stop_playback = False
        
        audio_data = self.create_audio_from_morse(morse)
        self.play_audio_data(audio_data, callback)
        
        self.is_playing = False
    
    def stop(self):
        """Stop playback"""
        self.stop_playback = True
        pygame.mixer.stop()
    
    def save_to_wav(self, audio_data: np.ndarray, filename: str):
        """Save audio data to WAV file"""
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data.tobytes())

class MorseCodeGUI:
    def __init__(self):
        self.morse_player = MorseCodeAudio()
        self.playback_thread = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Morse Code Audio Player")
        self.root.geometry("800x700")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="5")
        settings_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Frequency setting
        ttk.Label(settings_frame, text="Frequency (Hz):").grid(row=0, column=0, sticky=tk.W)
        self.frequency_var = tk.StringVar(value=str(self.morse_player.frequency))
        frequency_spinbox = ttk.Spinbox(settings_frame, from_=200, to=2000, 
                                       textvariable=self.frequency_var, width=10,
                                       command=self.update_settings)
        frequency_spinbox.grid(row=0, column=1, padx=(5, 20), sticky=tk.W)
        
        # WPM setting
        ttk.Label(settings_frame, text="WPM:").grid(row=0, column=2, sticky=tk.W)
        self.wpm_var = tk.StringVar(value=str(self.morse_player.wpm))
        wpm_spinbox = ttk.Spinbox(settings_frame, from_=5, to=50, 
                                 textvariable=self.wpm_var, width=10,
                                 command=self.update_settings)
        wpm_spinbox.grid(row=0, column=3, padx=(5, 0), sticky=tk.W)
        
        # Text input frame
        text_frame = ttk.LabelFrame(main_frame, text="Text to Morse", padding="5")
        text_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Text input
        self.text_input = scrolledtext.ScrolledText(text_frame, height=6, wrap=tk.WORD)
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        self.text_input.insert(tk.END, "Hello World! This is a morse code test.")
        
        # Text buttons frame
        text_buttons_frame = ttk.Frame(text_frame)
        text_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(text_buttons_frame, text="Play Text", 
                  command=self.play_text).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(text_buttons_frame, text="Convert to Morse", 
                  command=self.convert_to_morse).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(text_buttons_frame, text="Save as WAV", 
                  command=self.save_text_wav).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(text_buttons_frame, text="Clear", 
                  command=lambda: self.text_input.delete(1.0, tk.END)).pack(side=tk.LEFT)
        
        # Morse input frame
        morse_frame = ttk.LabelFrame(main_frame, text="Morse Code", padding="5")
        morse_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        morse_frame.columnconfigure(0, weight=1)
        morse_frame.rowconfigure(0, weight=1)
        
        # Morse input
        self.morse_input = scrolledtext.ScrolledText(morse_frame, height=6, wrap=tk.WORD)
        self.morse_input.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # Morse buttons frame
        morse_buttons_frame = ttk.Frame(morse_frame)
        morse_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(morse_buttons_frame, text="Play Morse", 
                  command=self.play_morse).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(morse_buttons_frame, text="Convert to Text", 
                  command=self.convert_to_text).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(morse_buttons_frame, text="Save as WAV", 
                  command=self.save_morse_wav).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(morse_buttons_frame, text="Clear", 
                  command=lambda: self.morse_input.delete(1.0, tk.END)).pack(side=tk.LEFT)
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))
        
        self.play_button = ttk.Button(control_frame, text="▶ Play", state=tk.NORMAL)
        self.play_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="⏹ Stop", 
                                     command=self.stop_playback, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        # Reference frame
        ref_frame = ttk.LabelFrame(main_frame, text="Morse Code Reference", padding="5")
        ref_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        ref_frame.columnconfigure(0, weight=1)
        ref_frame.rowconfigure(0, weight=1)
        
        # Reference text
        ref_text = scrolledtext.ScrolledText(ref_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        ref_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Populate reference
        self.populate_reference(ref_text)
        
        # Configure grid weights for resizing
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(5, weight=1)
    
    def populate_reference(self, text_widget):
        """Populate morse code reference"""
        text_widget.config(state=tk.NORMAL)
        
        # Letters
        text_widget.insert(tk.END, "LETTERS:\n")
        letters = ['ABCDEFGHIJKLMNOPQRSTUVWXYZ']
        for i in range(0, 26, 6):
            line = ""
            for j in range(6):
                if i + j < 26:
                    char = chr(ord('A') + i + j)
                    morse = self.morse_player.morse_code.get(char, '')
                    line += f"{char}:{morse:6} "
            text_widget.insert(tk.END, line + "\n")
        
        # Numbers
        text_widget.insert(tk.END, "\nNUMBERS:\n")
        for i in range(0, 10, 5):
            line = ""
            for j in range(5):
                if i + j < 10:
                    char = str(i + j)
                    morse = self.morse_player.morse_code.get(char, '')
                    line += f"{char}:{morse:7} "
            text_widget.insert(tk.END, line + "\n")
        
        # Punctuation
        text_widget.insert(tk.END, "\nPUNCTUATION:\n")
        punct = ['.', ',', '?', "'", '!', '/', '(', ')', '&', ':', ';', '=', '+', '-', '_', '"', '$', '@']
        for i in range(0, len(punct), 6):
            line = ""
            for j in range(6):
                if i + j < len(punct):
                    char = punct[i + j]
                    morse = self.morse_player.morse_code.get(char, '')
                    line += f"{char}:{morse:8} "
            text_widget.insert(tk.END, line + "\n")
        
        text_widget.config(state=tk.DISABLED)
    
    def update_settings(self):
        """Update morse player settings"""
        try:
            frequency = int(self.frequency_var.get())
            wpm = int(self.wpm_var.get())
            
            self.morse_player.frequency = frequency
            self.morse_player.wpm = wpm
            self.morse_player.calculate_timings()
            
        except ValueError:
            pass  # Invalid input, ignore
    
    def play_text(self):
        """Play text as morse code"""
        if self.morse_player.is_playing:
            return
        
        text = self.text_input.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to play.")
            return
        
        self.update_settings()
        self.set_playing_state(True)
        
        def play_thread():
            try:
                self.progress_var.set("Playing text...")
                self.morse_player.play_text(text, self.update_progress)
                self.progress_var.set("Finished playing text")
            except Exception as e:
                self.progress_var.set(f"Error: {e}")
            finally:
                self.root.after(0, lambda: self.set_playing_state(False))
        
        self.playback_thread = threading.Thread(target=play_thread, daemon=True)
        self.playback_thread.start()
    
    def play_morse(self):
        """Play morse code"""
        if self.morse_player.is_playing:
            return
        
        morse = self.morse_input.get(1.0, tk.END).strip()
        if not morse:
            messagebox.showwarning("Warning", "Please enter some morse code to play.")
            return
        
        self.update_settings()
        self.set_playing_state(True)
        
        def play_thread():
            try:
                self.progress_var.set("Playing morse code...")
                self.morse_player.play_morse(morse, self.update_progress)
                self.progress_var.set("Finished playing morse code")
            except Exception as e:
                self.progress_var.set(f"Error: {e}")
            finally:
                self.root.after(0, lambda: self.set_playing_state(False))
        
        self.playback_thread = threading.Thread(target=play_thread, daemon=True)
        self.playback_thread.start()
    
    def stop_playback(self):
        """Stop current playback"""
        self.morse_player.stop()
        self.progress_var.set("Stopped")
        self.set_playing_state(False)
    
    def convert_to_morse(self):
        """Convert text to morse code"""
        text = self.text_input.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to convert.")
            return
        
        morse = self.morse_player.text_to_morse(text)
        self.morse_input.delete(1.0, tk.END)
        self.morse_input.insert(tk.END, morse)
        self.progress_var.set("Converted text to morse code")
    
    def convert_to_text(self):
        """Convert morse code to text"""
        morse = self.morse_input.get(1.0, tk.END).strip()
        if not morse:
            messagebox.showwarning("Warning", "Please enter some morse code to convert.")
            return
        
        text = self.morse_player.morse_to_text(morse)
        self.text_input.delete(1.0, tk.END)
        self.text_input.insert(tk.END, text)
        self.progress_var.set("Converted morse code to text")
    
    def save_text_wav(self):
        """Save text as WAV file"""
        text = self.text_input.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to save.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.update_settings()
                audio_data = self.morse_player.create_audio_from_text(text)
                self.morse_player.save_to_wav(audio_data, filename)
                self.progress_var.set(f"Saved as {filename}")
                messagebox.showinfo("Success", f"Audio saved as {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save audio: {e}")
    
    def save_morse_wav(self):
        """Save morse code as WAV file"""
        morse = self.morse_input.get(1.0, tk.END).strip()
        if not morse:
            messagebox.showwarning("Warning", "Please enter some morse code to save.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.update_settings()
                audio_data = self.morse_player.create_audio_from_morse(morse)
                self.morse_player.save_to_wav(audio_data, filename)
                self.progress_var.set(f"Saved as {filename}")
                messagebox.showinfo("Success", f"Audio saved as {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save audio: {e}")
    
    def set_playing_state(self, playing: bool):
        """Update UI for playing state"""
        if playing:
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.stop_button.config(state=tk.DISABLED)
    
    def update_progress(self):
        """Update progress during playback"""
        # This could be enhanced to show actual progress
        pass
    
    def run(self):
        """Run the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        self.morse_player.stop()
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join(timeout=1.0)
        self.root.destroy()

def main():
    """Main function to run the application"""
    try:
        app = MorseCodeGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()

def demo_console():
    """Console demo of morse code functionality"""
    print("=== Morse Code Audio Player Demo ===")
    
    # Create morse player
    morse_player = MorseCodeAudio(frequency=600, wpm=20)
    
    # Demo text
    demo_text = "HELLO WORLD"
    print(f"Demo text: {demo_text}")
    
    # Convert to morse
    morse_code = morse_player.text_to_morse(demo_text)
    print(f"Morse code: {morse_code}")
    
    # Convert back to text
    decoded_text = morse_player.morse_to_text(morse_code)
    print(f"Decoded text: {decoded_text}")
    
    # Play audio (comment out if no audio system)
    print("\nPlaying morse code audio...")
    try:
        morse_player.play_text(demo_text)
        print("Audio playback complete!")
    except Exception as e:
        print(f"Audio playback error: {e}")
    
    # Save to WAV file
    print("\nSaving to WAV file...")
    try:
        audio_data = morse_player.create_audio_from_text(demo_text)
        morse_player.save_to_wav(audio_data, "demo_morse.wav")
        print("WAV file saved: demo_morse.wav")
    except Exception as e:
        print(f"WAV save error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_console()
    else:
        main()
