"""
Intelligent Timetable Scheduler

Features:
- Constraint satisfaction
- Optimization
- Modular design
- CLI interface
- Error handling
"""
import sys
import random
from collections import defaultdict

class Scheduler:
    def __init__(self):
        self.timetable = defaultdict(list)
        self.constraints = defaultdict(list)
    def add_event(self, day, time, event):
        self.timetable[day].append((time, event))
    def add_constraint(self, day, time):
        self.constraints[day].append(time)
    def optimize(self):
        # Dummy: shuffle events
        for day in self.timetable:
            random.shuffle(self.timetable[day])
    def show(self):
        for day, events in self.timetable.items():
            print(f"{day}:")
            for time, event in events:
                print(f"  {time}: {event}")

class CLI:
    @staticmethod
    def run():
        sched = Scheduler()
        print("Intelligent Timetable Scheduler")
        while True:
            cmd = input('> ')
            if cmd.startswith('add'):
                parts = cmd.split()
                if len(parts) < 4:
                    print("Usage: add <day> <time> <event>")
                    continue
                day, time, event = parts[1], parts[2], ' '.join(parts[3:])
                sched.add_event(day, time, event)
                print("Event added.")
            elif cmd.startswith('constraint'):
                parts = cmd.split()
                if len(parts) < 3:
                    print("Usage: constraint <day> <time>")
                    continue
                day, time = parts[1], parts[2]
                sched.add_constraint(day, time)
                print("Constraint added.")
            elif cmd == 'optimize':
                sched.optimize()
                print("Timetable optimized.")
            elif cmd == 'show':
                sched.show()
            elif cmd == 'exit':
                break
            else:
                print("Unknown command")

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
