"""
Voice Controlled Home Assistant

Features:
- Voice command recognition
- Device control
- Modular design
- CLI interface
- Error handling
"""
import sys
import random
try:
    import speech_recognition as sr
except ImportError:
    sr = None

class Device:
    def __init__(self, name):
        self.name = name
        self.state = 'off'
    def turn_on(self):
        self.state = 'on'
        print(f"{self.name} turned ON")
    def turn_off(self):
        self.state = 'off'
        print(f"{self.name} turned OFF")
    def status(self):
        return self.state

class VoiceAssistant:
    def __init__(self, devices):
        self.devices = devices
    def listen(self):
        if sr:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening...")
                audio = recognizer.listen(source)
                try:
                    cmd = recognizer.recognize_google(audio).lower()
                    print(f"Heard: {cmd}")
                    self.parse_command(cmd)
                except Exception as e:
                    print(f"Speech error: {e}")
        else:
            print("Speech recognition not available.")
    def parse_command(self, cmd):
        if 'turn on' in cmd:
            for d in self.devices:
                if d.name.lower() in cmd:
                    d.turn_on()
        elif 'turn off' in cmd:
            for d in self.devices:
                if d.name.lower() in cmd:
                    d.turn_off()
        else:
            print("Unknown command")

class CLI:
    @staticmethod
    def run():
        devices = [Device('Light'), Device('Fan'), Device('AC')]
        va = VoiceAssistant(devices)
        print("Voice Controlled Home Assistant")
        while True:
            cmd = input('> ')
            if cmd == 'listen':
                va.listen()
            elif cmd == 'status':
                for d in devices:
                    print(f"{d.name}: {d.status()}")
            elif cmd == 'exit':
                break
            else:
                print("Unknown command. Type 'listen', 'status', or 'exit'.")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
