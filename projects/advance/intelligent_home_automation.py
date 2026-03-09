"""
Intelligent Home Automation System

Features:
- Device control
- Scheduling
- Voice commands
- Modular design
- CLI interface
- Error handling
"""
import sys
import time
import threading
import json
import random
from datetime import datetime

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

class Scheduler:
    def __init__(self):
        self.tasks = []
    def schedule(self, device, action, run_time):
        self.tasks.append({'device': device, 'action': action, 'run_time': run_time})
    def run(self):
        while True:
            now = datetime.now().strftime('%H:%M')
            for task in self.tasks:
                if task['run_time'] == now:
                    if task['action'] == 'on':
                        task['device'].turn_on()
                    else:
                        task['device'].turn_off()
                    self.tasks.remove(task)
            time.sleep(60)

class VoiceAssistant:
    def __init__(self, devices):
        self.devices = devices
    def listen(self, command):
        cmd = command.lower().split()
        if 'turn' in cmd and 'on' in cmd:
            for d in self.devices:
                if d.name.lower() in cmd:
                    d.turn_on()
        elif 'turn' in cmd and 'off' in cmd:
            for d in self.devices:
                if d.name.lower() in cmd:
                    d.turn_off()
        else:
            print("Unknown command")

class HomeAutomation:
    def __init__(self):
        self.devices = [Device('Light'), Device('Fan'), Device('AC')]
        self.scheduler = Scheduler()
        self.voice = VoiceAssistant(self.devices)
    def run(self):
        print("Intelligent Home Automation System")
        print("Devices: Light, Fan, AC")
        print("Commands: turn on <device>, turn off <device>, schedule <device> <on/off> <HH:MM>")
        while True:
            cmd = input('> ')
            if cmd.startswith('turn'):
                self.voice.listen(cmd)
            elif cmd.startswith('schedule'):
                parts = cmd.split()
                if len(parts) == 5:
                    device_name = parts[1]
                    action = parts[2]
                    run_time = parts[4]
                    device = next((d for d in self.devices if d.name.lower() == device_name.lower()), None)
                    if device:
                        self.scheduler.schedule(device, action, run_time)
                        print(f"Scheduled {device_name} to turn {action} at {run_time}")
                    else:
                        print("Device not found")
                else:
                    print("Invalid schedule command")
            elif cmd == 'status':
                for d in self.devices:
                    print(f"{d.name}: {d.status()}")
            elif cmd == 'exit':
                print("Exiting...")
                break
            else:
                print("Unknown command")

if __name__ == "__main__":
    try:
        automation = HomeAutomation()
        threading.Thread(target=automation.scheduler.run, daemon=True).start()
        automation.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
