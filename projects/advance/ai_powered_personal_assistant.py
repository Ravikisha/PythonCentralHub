"""
AI Powered Personal Assistant

Features:
- Scheduling
- Reminders
- Natural language interface
- Modular design
- CLI interface
- Error handling
"""
import sys
import datetime
import threading
import time
import re
from collections import defaultdict
try:
    import nltk
    from nltk.tokenize import word_tokenize
except ImportError:
    nltk = None
    word_tokenize = lambda x: x.split()

class Reminder:
    def __init__(self, time, message):
        self.time = time
        self.message = message
        self.triggered = False

class PersonalAssistant:
    def __init__(self):
        self.reminders = []
        self.schedule = defaultdict(list)
        self.running = True
        self.thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.thread.start()

    def add_reminder(self, time_str, message):
        try:
            t = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M')
            self.reminders.append(Reminder(t, message))
            print(f"Reminder set for {t}: {message}")
        except Exception as e:
            print(f"Error: {e}")

    def add_schedule(self, date_str, event):
        self.schedule[date_str].append(event)
        print(f"Scheduled: {event} on {date_str}")

    def show_schedule(self, date_str):
        events = self.schedule.get(date_str, [])
        print(f"Schedule for {date_str}:")
        for e in events:
            print(f"- {e}")

    def check_reminders(self):
        while self.running:
            now = datetime.datetime.now()
            for r in self.reminders:
                if not r.triggered and now >= r.time:
                    print(f"REMINDER: {r.message}")
                    r.triggered = True
            time.sleep(30)

    def parse_command(self, cmd):
        tokens = word_tokenize(cmd.lower())
        if 'remind' in tokens:
            m = re.search(r'remind me at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) to (.+)', cmd)
            if m:
                self.add_reminder(m.group(1), m.group(2))
            else:
                print("Invalid reminder format.")
        elif 'schedule' in tokens:
            m = re.search(r'schedule (.+) on (\d{4}-\d{2}-\d{2})', cmd)
            if m:
                self.add_schedule(m.group(2), m.group(1))
            else:
                print("Invalid schedule format.")
        elif 'show' in tokens and 'schedule' in tokens:
            m = re.search(r'show schedule for (\d{4}-\d{2}-\d{2})', cmd)
            if m:
                self.show_schedule(m.group(1))
            else:
                print("Invalid show schedule format.")
        elif cmd == 'exit':
            self.running = False
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Unknown command.")

class CLI:
    @staticmethod
    def run():
        pa = PersonalAssistant()
        print("AI Powered Personal Assistant")
        print("Commands:")
        print("- remind me at YYYY-MM-DD HH:MM to <message>")
        print("- schedule <event> on YYYY-MM-DD")
        print("- show schedule for YYYY-MM-DD")
        print("- exit")
        while pa.running:
            cmd = input('> ')
            pa.parse_command(cmd)

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
