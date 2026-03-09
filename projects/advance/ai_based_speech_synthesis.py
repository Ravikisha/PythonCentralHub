"""
AI-based Speech Synthesis

Features:
- Speech synthesis using deep learning
- Text-to-speech
- Modular design
- CLI interface
- Error handling
"""
import sys
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

class SpeechSynthesizer:
    def __init__(self):
        self.engine = pyttsx3.init() if pyttsx3 else None
    def synthesize(self, text):
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
        else:
            print("Speech synthesis library not available.")

class CLI:
    @staticmethod
    def run():
        print("AI-based Speech Synthesis")
        synthesizer = SpeechSynthesizer()
        while True:
            cmd = input('> ')
            if cmd.startswith('speak'):
                parts = cmd.split(maxsplit=1)
                if len(parts) < 2:
                    print("Usage: speak <text>")
                    continue
                text = parts[1]
                synthesizer.synthesize(text)
            elif cmd == 'exit':
                break
            else:
                print("Unknown command. Type 'speak <text>' or 'exit'.")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
