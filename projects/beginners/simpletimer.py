# Simple Timer App

import time
import threading
from datetime import datetime, timedelta

class SimpleTimer:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.start_time = None
        self.pause_time = 0
        self.timer_thread = None
        
    def start_stopwatch(self):
        """Start a stopwatch"""
        print("Stopwatch started! Press Enter to stop.")
        self.is_running = True
        self.start_time = time.time()
        
        def update_display():
            while self.is_running:
                if not self.is_paused:
                    elapsed = time.time() - self.start_time - self.pause_time
                    hours = int(elapsed // 3600)
                    minutes = int((elapsed % 3600) // 60)
                    seconds = int(elapsed % 60)
                    milliseconds = int((elapsed % 1) * 100)
                    
                    print(f"\r⏱️  {hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:02d}", end="", flush=True)
                time.sleep(0.01)
        
        self.timer_thread = threading.Thread(target=update_display)
        self.timer_thread.start()
        
        input()  # Wait for Enter
        self.stop()
    
    def countdown_timer(self, duration_seconds):
        """Run a countdown timer"""
        print(f"Countdown timer: {duration_seconds} seconds")
        print("Press Enter to stop early.")
        
        self.is_running = True
        end_time = time.time() + duration_seconds
        
        def update_countdown():
            while self.is_running and time.time() < end_time:
                remaining = end_time - time.time()
                if remaining <= 0:
                    break
                    
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                seconds = int(remaining % 60)
                
                print(f"\r⏰ Time remaining: {hours:02d}:{minutes:02d}:{seconds:02d}", end="", flush=True)
                time.sleep(0.1)
            
            if self.is_running:
                print(f"\n🔔 Time's up!")
                # Beep sound simulation
                for _ in range(3):
                    print("BEEP!", end=" ")
                    time.sleep(0.5)
                print()
        
        self.timer_thread = threading.Thread(target=update_countdown)
        self.timer_thread.start()
        
        # Check for early stop
        input()
        if self.is_running:
            self.stop()
            print("\nTimer stopped early.")
    
    def pomodoro_timer(self, work_minutes=25, break_minutes=5, cycles=4):
        """Run a Pomodoro timer session"""
        print(f"Pomodoro Timer: {work_minutes}min work, {break_minutes}min break, {cycles} cycles")
        
        for cycle in range(1, cycles + 1):
            print(f"\n🍅 Cycle {cycle}/{cycles}")
            
            # Work session
            print(f"Work time: {work_minutes} minutes")
            self.countdown_timer(work_minutes * 60)
            
            if cycle < cycles:
                # Break session
                print(f"\n☕ Break time: {break_minutes} minutes")
                self.countdown_timer(break_minutes * 60)
        
        print("\n🎉 Pomodoro session complete!")
    
    def stop(self):
        """Stop the timer"""
        self.is_running = False
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join()
    
    def format_time_input(self, time_str):
        """Parse time input in various formats"""
        time_str = time_str.strip().lower()
        
        # Handle different formats
        if 's' in time_str:
            return int(time_str.replace('s', ''))
        elif 'm' in time_str:
            return int(time_str.replace('m', '')) * 60
        elif 'h' in time_str:
            return int(time_str.replace('h', '')) * 3600
        elif ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 2:  # MM:SS
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:  # HH:MM:SS
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        else:
            return int(time_str)  # Assume seconds

def main():
    """Main function to run the timer app"""
    timer = SimpleTimer()
    
    while True:
        print("\n" + "="*40)
        print("SIMPLE TIMER APP")
        print("="*40)
        print("1. Stopwatch")
        print("2. Countdown Timer")
        print("3. Pomodoro Timer")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        try:
            if choice == '1':
                timer.start_stopwatch()
            
            elif choice == '2':
                duration_input = input("Enter duration (e.g., '30s', '5m', '1h', '2:30'): ").strip()
                duration = timer.format_time_input(duration_input)
                timer.countdown_timer(duration)
            
            elif choice == '3':
                print("Pomodoro Timer Settings:")
                work_input = input("Work duration in minutes (default 25): ").strip()
                work_minutes = int(work_input) if work_input else 25
                
                break_input = input("Break duration in minutes (default 5): ").strip()
                break_minutes = int(break_input) if break_input else 5
                
                cycles_input = input("Number of cycles (default 4): ").strip()
                cycles = int(cycles_input) if cycles_input else 4
                
                timer.pomodoro_timer(work_minutes, break_minutes, cycles)
            
            elif choice == '4':
                print("Thank you for using Simple Timer App!")
                break
            
            else:
                print("Invalid choice! Please select 1-4.")
        
        except ValueError:
            print("Invalid input! Please enter a valid number.")
        except KeyboardInterrupt:
            timer.stop()
            print("\nTimer interrupted.")
        except Exception as e:
            timer.stop()
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
