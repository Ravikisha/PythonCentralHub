"""
Voice Assistant

Features:
- Speech recognition
- Command execution
- Modular design
- CLI interface
- Error handling
"""
import sys
try:
    import speech_recognition as sr
except ImportError:
    sr = None

class VoiceAssistant:
    def __init__(self):
        pass
    def listen(self):
        if sr:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source)
                try:
                    cmd = recognizer.recognize_google(audio).lower()
                    print(f"Heard: {cmd}")
                    self.execute(cmd)
                except Exception as e:
                    print(f"Speech error: {e}")
        else:
            print("Speech recognition not available.")
    def execute(self, cmd):
        if 'hello' in cmd:
            print("Hello! How can I help you?")
        elif 'time' in cmd:
            import datetime
            print(f"Current time: {datetime.datetime.now()}")
        else:
            print("Unknown command.")

class CLI:
    @staticmethod
    def run():
        va = VoiceAssistant()
        print("Voice Assistant")
        while True:
            cmd = input('> ')
            if cmd == 'listen':
                va.listen()
            elif cmd == 'exit':
                break
            else:
                print("Unknown command. Type 'listen' or 'exit'.")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
