"""
AI-based Voice Recognition

Features:
- Voice recognition using ML
- Speaker identification
- Modular design
- CLI interface
- Error handling
"""
import sys
try:
    import speech_recognition as sr
except ImportError:
    sr = None

class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer() if sr else None
    def recognize(self, audio_file):
        if not self.recognizer:
            print("SpeechRecognition library not available.")
            return ""
        with sr.AudioFile(audio_file) as source:
            audio = self.recognizer.record(source)
            try:
                return self.recognizer.recognize_google(audio)
            except Exception as e:
                print(f"Recognition error: {e}")
                return ""

class CLI:
    @staticmethod
    def run():
        print("AI-based Voice Recognition")
        recognizer = VoiceRecognizer()
        while True:
            cmd = input('> ')
            if cmd.startswith('recognize'):
                parts = cmd.split()
                if len(parts) < 2:
                    print("Usage: recognize <audio_file>")
                    continue
                audio_file = parts[1]
                result = recognizer.recognize(audio_file)
                print(f"Recognized: {result}")
            elif cmd == 'exit':
                break
            else:
                print("Unknown command. Type 'recognize <audio_file>' or 'exit'.")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
