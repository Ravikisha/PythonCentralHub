#!/usr/bin/env python3
"""
Speech-to-Text Converter
Advanced speech recognition application with multiple engines and features.

Features:
- Real-time speech recognition
- Audio file transcription
- Multiple recognition engines
- Language selection
- Text output formats
- Audio recording capabilities

Requirements:
- SpeechRecognition
- pyaudio
- pydub
- tkinter

Author: Python Central Hub
Date: 2025-09-05
"""

import speech_recognition as sr
import pyaudio
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import wave
import time
import json
from datetime import datetime
import os


class SpeechToTextConverter:
    """Advanced speech-to-text converter with GUI."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.audio_data = None
        
        # Recognition engines
        self.engines = {
            'Google': self.recognize_google,
            'Google Cloud': self.recognize_google_cloud,
            'Sphinx': self.recognize_sphinx,
            'Wit.ai': self.recognize_wit,
            'Microsoft Bing': self.recognize_bing
        }
        
        # Supported languages for Google Speech Recognition
        self.languages = {
            'English (US)': 'en-US',
            'English (UK)': 'en-GB',
            'Spanish': 'es-ES',
            'French': 'fr-FR',
            'German': 'de-DE',
            'Italian': 'it-IT',
            'Portuguese': 'pt-PT',
            'Russian': 'ru-RU',
            'Chinese': 'zh-CN',
            'Japanese': 'ja-JP'
        }
        
        self.setup_gui()
        self.calibrate_microphone()
    
    def setup_gui(self):
        """Setup the graphical user interface."""
        self.root = tk.Tk()
        self.root.title("Speech-to-Text Converter")
        self.root.geometry("800x600")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Real-time tab
        self.create_realtime_tab(notebook)
        
        # File transcription tab
        self.create_file_tab(notebook)
        
        # Settings tab
        self.create_settings_tab(notebook)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_realtime_tab(self, notebook):
        """Create real-time speech recognition tab."""
        realtime_frame = ttk.Frame(notebook)
        notebook.add(realtime_frame, text="Real-time Recognition")
        
        # Control buttons
        button_frame = ttk.Frame(realtime_frame)
        button_frame.pack(pady=10)
        
        self.listen_button = ttk.Button(
            button_frame, text="Start Listening", 
            command=self.toggle_listening
        )
        self.listen_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(
            button_frame, text="Clear Text", 
            command=self.clear_text
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        save_button = ttk.Button(
            button_frame, text="Save Text", 
            command=self.save_text
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Text display area
        text_frame = ttk.LabelFrame(realtime_frame, text="Recognized Text")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame, wrap=tk.WORD, height=15
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Confidence display
        confidence_frame = ttk.Frame(realtime_frame)
        confidence_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(confidence_frame, text="Confidence:").pack(side=tk.LEFT)
        self.confidence_var = tk.StringVar()
        self.confidence_var.set("N/A")
        ttk.Label(confidence_frame, textvariable=self.confidence_var).pack(side=tk.LEFT, padx=5)
    
    def create_file_tab(self, notebook):
        """Create file transcription tab."""
        file_frame = ttk.Frame(notebook)
        notebook.add(file_frame, text="File Transcription")
        
        # File selection
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(file_select_frame, text="Audio File:").pack(side=tk.LEFT)
        self.file_path_var = tk.StringVar()
        ttk.Entry(
            file_select_frame, textvariable=self.file_path_var, 
            state="readonly", width=50
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(
            file_select_frame, text="Browse", 
            command=self.browse_audio_file
        ).pack(side=tk.RIGHT)
        
        # Transcription controls
        control_frame = ttk.Frame(file_frame)
        control_frame.pack(pady=10)
        
        transcribe_button = ttk.Button(
            control_frame, text="Transcribe File", 
            command=self.transcribe_file
        )
        transcribe_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            control_frame, variable=self.progress_var, 
            maximum=100, length=200
        )
        self.progress_bar.pack(side=tk.LEFT, padx=10)
        
        # Results area
        results_frame = ttk.LabelFrame(file_frame, text="Transcription Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.file_text_area = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, height=15
        )
        self.file_text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_settings_tab(self, notebook):
        """Create settings tab."""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Settings")
        
        # Recognition engine selection
        engine_frame = ttk.LabelFrame(settings_frame, text="Recognition Engine")
        engine_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.engine_var = tk.StringVar(value="Google")
        for engine in self.engines.keys():
            ttk.Radiobutton(
                engine_frame, text=engine, variable=self.engine_var, 
                value=engine
            ).pack(anchor=tk.W, padx=5, pady=2)
        
        # Language selection
        language_frame = ttk.LabelFrame(settings_frame, text="Language")
        language_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.language_var = tk.StringVar(value="English (US)")
        language_combo = ttk.Combobox(
            language_frame, textvariable=self.language_var,
            values=list(self.languages.keys()), state="readonly"
        )
        language_combo.pack(padx=5, pady=5)
        
        # Audio settings
        audio_frame = ttk.LabelFrame(settings_frame, text="Audio Settings")
        audio_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Microphone sensitivity
        ttk.Label(audio_frame, text="Microphone Sensitivity:").pack(anchor=tk.W, padx=5)
        self.sensitivity_var = tk.DoubleVar(value=0.5)
        sensitivity_scale = ttk.Scale(
            audio_frame, from_=0.1, to=1.0, variable=self.sensitivity_var,
            orient=tk.HORIZONTAL
        )
        sensitivity_scale.pack(fill=tk.X, padx=5, pady=5)
        
        # Pause threshold
        ttk.Label(audio_frame, text="Pause Threshold (seconds):").pack(anchor=tk.W, padx=5)
        self.pause_var = tk.DoubleVar(value=0.8)
        pause_scale = ttk.Scale(
            audio_frame, from_=0.3, to=2.0, variable=self.pause_var,
            orient=tk.HORIZONTAL
        )
        pause_scale.pack(fill=tk.X, padx=5, pady=5)
        
        # Calibrate button
        calibrate_button = ttk.Button(
            audio_frame, text="Calibrate Microphone", 
            command=self.calibrate_microphone
        )
        calibrate_button.pack(pady=10)
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise."""
        try:
            self.status_var.set("Calibrating microphone... Please remain quiet.")
            self.root.update()
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            self.status_var.set("Microphone calibrated successfully")
        except Exception as e:
            self.status_var.set(f"Calibration failed: {e}")
    
    def toggle_listening(self):
        """Toggle real-time listening mode."""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        """Start real-time speech recognition."""
        self.is_listening = True
        self.listen_button.config(text="Stop Listening")
        self.status_var.set("Listening for speech...")
        
        # Start listening in a separate thread
        self.listen_thread = threading.Thread(target=self.listen_continuously)
        self.listen_thread.daemon = True
        self.listen_thread.start()
    
    def stop_listening(self):
        """Stop real-time speech recognition."""
        self.is_listening = False
        self.listen_button.config(text="Start Listening")
        self.status_var.set("Stopped listening")
    
    def listen_continuously(self):
        """Continuously listen for speech and recognize."""
        while self.is_listening:
            try:
                # Listen for audio
                with self.microphone as source:
                    # Adjust recognizer settings
                    self.recognizer.energy_threshold = 300 * self.sensitivity_var.get()
                    self.recognizer.pause_threshold = self.pause_var.get()
                    
                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                # Recognize speech in background thread
                recognition_thread = threading.Thread(
                    target=self.process_audio, args=(audio,)
                )
                recognition_thread.daemon = True
                recognition_thread.start()
                
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                if self.is_listening:
                    self.root.after(0, lambda: self.status_var.set(f"Error: {e}"))
                break
    
    def process_audio(self, audio):
        """Process audio and update GUI with recognized text."""
        try:
            # Get selected engine and language
            engine_name = self.engine_var.get()
            language_code = self.languages.get(self.language_var.get(), 'en-US')
            
            # Recognize speech
            if engine_name in self.engines:
                text = self.engines[engine_name](audio, language_code)
                
                # Update GUI in main thread
                self.root.after(0, lambda: self.update_recognized_text(text))
            
        except sr.UnknownValueError:
            self.root.after(0, lambda: self.status_var.set("Could not understand audio"))
        except sr.RequestError as e:
            self.root.after(0, lambda: self.status_var.set(f"Recognition error: {e}"))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {e}"))
    
    def update_recognized_text(self, text):
        """Update the text area with recognized text."""
        if text:
            self.text_area.insert(tk.END, text + " ")
            self.text_area.see(tk.END)
            self.status_var.set("Speech recognized")
    
    def recognize_google(self, audio, language='en-US'):
        """Recognize speech using Google Speech Recognition."""
        return self.recognizer.recognize_google(audio, language=language)
    
    def recognize_google_cloud(self, audio, language='en-US'):
        """Recognize speech using Google Cloud Speech."""
        # Note: Requires API key
        try:
            return self.recognizer.recognize_google_cloud(audio, language=language)
        except:
            return self.recognizer.recognize_google(audio, language=language)
    
    def recognize_sphinx(self, audio, language='en-US'):
        """Recognize speech using CMU Sphinx (offline)."""
        return self.recognizer.recognize_sphinx(audio)
    
    def recognize_wit(self, audio, language='en-US'):
        """Recognize speech using Wit.ai."""
        # Note: Requires API key
        return self.recognizer.recognize_wit(audio)
    
    def recognize_bing(self, audio, language='en-US'):
        """Recognize speech using Microsoft Bing."""
        # Note: Requires API key
        return self.recognizer.recognize_bing(audio, language=language)
    
    def browse_audio_file(self):
        """Browse for audio file to transcribe."""
        file_types = [
            ("Audio files", "*.wav *.mp3 *.flac *.m4a"),
            ("WAV files", "*.wav"),
            ("MP3 files", "*.mp3"),
            ("FLAC files", "*.flac"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=file_types
        )
        
        if filename:
            self.file_path_var.set(filename)
    
    def transcribe_file(self):
        """Transcribe selected audio file."""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select an audio file first.")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Selected file does not exist.")
            return
        
        # Start transcription in separate thread
        transcription_thread = threading.Thread(target=self.process_audio_file, args=(file_path,))
        transcription_thread.daemon = True
        transcription_thread.start()
    
    def process_audio_file(self, file_path):
        """Process audio file and transcribe."""
        try:
            self.root.after(0, lambda: self.status_var.set("Processing audio file..."))
            self.root.after(0, lambda: self.progress_var.set(10))
            
            # Load audio file
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
            
            self.root.after(0, lambda: self.progress_var.set(50))
            
            # Get selected engine and language
            engine_name = self.engine_var.get()
            language_code = self.languages.get(self.language_var.get(), 'en-US')
            
            # Recognize speech
            if engine_name in self.engines:
                text = self.engines[engine_name](audio, language_code)
                
                # Update results area
                self.root.after(0, lambda: self.update_file_results(text, file_path))
            
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.status_var.set("Transcription completed"))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Transcription error: {e}"))
            self.root.after(0, lambda: self.progress_var.set(0))
    
    def update_file_results(self, text, file_path):
        """Update file transcription results."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        result_text = f"=== Transcription Results ===\n"
        result_text += f"File: {os.path.basename(file_path)}\n"
        result_text += f"Date: {timestamp}\n"
        result_text += f"Engine: {self.engine_var.get()}\n"
        result_text += f"Language: {self.language_var.get()}\n"
        result_text += f"{'='*50}\n\n"
        result_text += text
        result_text += f"\n\n{'='*50}\n\n"
        
        self.file_text_area.delete(1.0, tk.END)
        self.file_text_area.insert(1.0, result_text)
    
    def clear_text(self):
        """Clear the recognized text area."""
        self.text_area.delete(1.0, tk.END)
    
    def save_text(self):
        """Save recognized text to file."""
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No text to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Text",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    # Save as JSON with metadata
                    data = {
                        'text': text,
                        'timestamp': datetime.now().isoformat(),
                        'engine': self.engine_var.get(),
                        'language': self.language_var.get()
                    }
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=2)
                else:
                    # Save as plain text
                    with open(file_path, 'w') as f:
                        f.write(text)
                
                self.status_var.set(f"Text saved to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main function to run the speech-to-text converter."""
    try:
        app = SpeechToTextConverter()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Make sure you have installed all required packages:")
        print("pip install SpeechRecognition pyaudio pydub")


if __name__ == "__main__":
    main()
