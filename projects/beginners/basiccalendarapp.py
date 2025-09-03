# Basic Calendar App

import calendar
import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple

class Event:
    def __init__(self, event_id: str, title: str, date: str, time: str = "", 
                 description: str = "", category: str = "General"):
        self.id = event_id
        self.title = title
        self.date = date  # Format: YYYY-MM-DD
        self.time = time  # Format: HH:MM
        self.description = description
        self.category = category
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'date': self.date,
            'time': self.time,
            'description': self.description,
            'category': self.category,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Event':
        """Create event from dictionary"""
        event = cls(
            data['id'], data['title'], data['date'], 
            data.get('time', ''), data.get('description', ''),
            data.get('category', 'General')
        )
        event.created_at = data.get('created_at', datetime.now().isoformat())
        return event
    
    def get_datetime(self) -> Optional[datetime]:
        """Get datetime object for the event"""
        try:
            if self.time:
                datetime_str = f"{self.date} {self.time}"
                return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
            else:
                return datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            return None
    
    def is_today(self) -> bool:
        """Check if event is today"""
        return self.date == date.today().strftime("%Y-%m-%d")
    
    def is_upcoming(self, days: int = 7) -> bool:
        """Check if event is within next N days"""
        try:
            event_date = datetime.strptime(self.date, "%Y-%m-%d").date()
            today = date.today()
            return today <= event_date <= today + timedelta(days=days)
        except ValueError:
            return False
    
    def __str__(self):
        time_str = f" at {self.time}" if self.time else ""
        return f"{self.title}{time_str} ({self.category})"

class BasicCalendarApp:
    def __init__(self, data_file: str = "calendar_data.json"):
        self.data_file = data_file
        self.events = {}  # event_id -> Event
        self.categories = set(["General", "Work", "Personal", "Health", "Education"])
        self.load_data()
    
    def load_data(self):
        """Load events from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Load events
                for event_data in data.get('events', []):
                    event = Event.from_dict(event_data)
                    self.events[event.id] = event
                
                # Load categories
                saved_categories = data.get('categories', [])
                if saved_categories:
                    self.categories.update(saved_categories)
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading data: {e}")
                self.events = {}
    
    def save_data(self):
        """Save events to JSON file"""
        try:
            data = {
                'events': [event.to_dict() for event in self.events.values()],
                'categories': list(self.categories)
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def generate_event_id(self) -> str:
        """Generate unique event ID"""
        if not self.events:
            return "EVT001"
        
        # Extract numeric part and increment
        max_num = 0
        for event_id in self.events.keys():
            if event_id.startswith("EVT"):
                try:
                    num = int(event_id[3:])
                    max_num = max(max_num, num)
                except ValueError:
                    pass
        
        return f"EVT{max_num + 1:03d}"
    
    def add_event(self, title: str, date_str: str, time_str: str = "", 
                  description: str = "", category: str = "General") -> Optional[Event]:
        """Add a new event"""
        try:
            # Validate date format
            datetime.strptime(date_str, "%Y-%m-%d")
            
            # Validate time format if provided
            if time_str:
                datetime.strptime(time_str, "%H:%M")
            
            event_id = self.generate_event_id()
            event = Event(event_id, title, date_str, time_str, description, category)
            self.events[event_id] = event
            
            # Add category if new
            self.categories.add(category)
            
            self.save_data()
            return event
            
        except ValueError as e:
            print(f"Invalid date/time format: {e}")
            return None
    
    def get_event(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        return self.events.get(event_id)
    
    def update_event(self, event_id: str, title: str = None, date_str: str = None,
                    time_str: str = None, description: str = None, 
                    category: str = None) -> bool:
        """Update an existing event"""
        event = self.get_event(event_id)
        if not event:
            return False
        
        try:
            if title is not None:
                event.title = title
            if date_str is not None:
                datetime.strptime(date_str, "%Y-%m-%d")  # Validate
                event.date = date_str
            if time_str is not None:
                if time_str:  # If not empty, validate
                    datetime.strptime(time_str, "%H:%M")
                event.time = time_str
            if description is not None:
                event.description = description
            if category is not None:
                event.category = category
                self.categories.add(category)
            
            self.save_data()
            return True
            
        except ValueError as e:
            print(f"Invalid date/time format: {e}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        if event_id in self.events:
            del self.events[event_id]
            self.save_data()
            return True
        return False
    
    def get_events_for_date(self, date_str: str) -> List[Event]:
        """Get all events for a specific date"""
        return [event for event in self.events.values() if event.date == date_str]
    
    def get_events_for_month(self, year: int, month: int) -> List[Event]:
        """Get all events for a specific month"""
        month_events = []
        for event in self.events.values():
            try:
                event_date = datetime.strptime(event.date, "%Y-%m-%d")
                if event_date.year == year and event_date.month == month:
                    month_events.append(event)
            except ValueError:
                continue
        
        # Sort by date and time
        month_events.sort(key=lambda e: (e.date, e.time or "00:00"))
        return month_events
    
    def get_upcoming_events(self, days: int = 7) -> List[Event]:
        """Get upcoming events within N days"""
        upcoming = [event for event in self.events.values() if event.is_upcoming(days)]
        # Sort by date and time
        upcoming.sort(key=lambda e: (e.date, e.time or "00:00"))
        return upcoming
    
    def get_today_events(self) -> List[Event]:
        """Get today's events"""
        today_str = date.today().strftime("%Y-%m-%d")
        today_events = self.get_events_for_date(today_str)
        # Sort by time
        today_events.sort(key=lambda e: e.time or "00:00")
        return today_events
    
    def get_events_by_category(self, category: str) -> List[Event]:
        """Get all events in a specific category"""
        return [event for event in self.events.values() if event.category == category]
    
    def search_events(self, query: str) -> List[Event]:
        """Search events by title or description"""
        query = query.lower()
        results = []
        
        for event in self.events.values():
            if (query in event.title.lower() or 
                query in event.description.lower() or
                query in event.category.lower()):
                results.append(event)
        
        # Sort by date
        results.sort(key=lambda e: e.date)
        return results
    
    def get_calendar_view(self, year: int, month: int) -> str:
        """Get calendar view for a month with events"""
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        
        # Get events for the month
        month_events = self.get_events_for_month(year, month)
        events_by_day = {}
        for event in month_events:
            try:
                day = datetime.strptime(event.date, "%Y-%m-%d").day
                if day not in events_by_day:
                    events_by_day[day] = []
                events_by_day[day].append(event)
            except ValueError:
                continue
        
        # Create calendar string
        result = f"\n{month_name} {year}\n"
        result += "Mo Tu We Th Fr Sa Su\n"
        
        for week in cal:
            week_str = ""
            for day in week:
                if day == 0:
                    week_str += "   "
                else:
                    day_str = f"{day:2d}"
                    # Mark days with events
                    if day in events_by_day:
                        day_str += "*"
                    else:
                        day_str += " "
                    week_str += day_str
            result += week_str + "\n"
        
        result += "\n* = Has events\n"
        return result
    
    def get_event_statistics(self) -> Dict:
        """Get event statistics"""
        if not self.events:
            return {}
        
        total_events = len(self.events)
        
        # Category distribution
        category_count = {}
        for event in self.events.values():
            category_count[event.category] = category_count.get(event.category, 0) + 1
        
        # Upcoming events
        upcoming_count = len(self.get_upcoming_events(30))
        today_count = len(self.get_today_events())
        
        # Monthly distribution
        monthly_count = {}
        for event in self.events.values():
            try:
                event_date = datetime.strptime(event.date, "%Y-%m-%d")
                month_key = f"{event_date.year}-{event_date.month:02d}"
                monthly_count[month_key] = monthly_count.get(month_key, 0) + 1
            except ValueError:
                continue
        
        return {
            'total_events': total_events,
            'today_events': today_count,
            'upcoming_events': upcoming_count,
            'categories': dict(category_count),
            'monthly_distribution': dict(monthly_count),
            'total_categories': len(self.categories)
        }
    
    def export_events(self, filename: str, start_date: str = None, end_date: str = None):
        """Export events to a text file"""
        try:
            events_to_export = list(self.events.values())
            
            # Filter by date range if provided
            if start_date:
                events_to_export = [e for e in events_to_export if e.date >= start_date]
            if end_date:
                events_to_export = [e for e in events_to_export if e.date <= end_date]
            
            # Sort by date
            events_to_export.sort(key=lambda e: (e.date, e.time or "00:00"))
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Calendar Events Export\n")
                f.write("=" * 50 + "\n\n")
                
                current_date = None
                for event in events_to_export:
                    if event.date != current_date:
                        current_date = event.date
                        f.write(f"\n{current_date} ({calendar.day_name[datetime.strptime(current_date, '%Y-%m-%d').weekday()]})\n")
                        f.write("-" * 30 + "\n")
                    
                    time_str = f" at {event.time}" if event.time else ""
                    f.write(f"• {event.title}{time_str}\n")
                    if event.description:
                        f.write(f"  Description: {event.description}\n")
                    f.write(f"  Category: {event.category}\n\n")
            
            print(f"Events exported to {filename}")
            
        except Exception as e:
            print(f"Error exporting events: {e}")
    
    def add_category(self, category: str):
        """Add a new category"""
        self.categories.add(category)
        self.save_data()

def display_events(events: List[Event], title: str = "Events"):
    """Display a list of events"""
    print(f"\n=== {title} ===")
    if not events:
        print("No events found.")
        return
    
    current_date = None
    for event in events:
        if event.date != current_date:
            current_date = event.date
            try:
                date_obj = datetime.strptime(current_date, "%Y-%m-%d")
                day_name = calendar.day_name[date_obj.weekday()]
                print(f"\n{current_date} ({day_name})")
                print("-" * 25)
            except ValueError:
                print(f"\n{current_date}")
                print("-" * 25)
        
        time_str = f" at {event.time}" if event.time else ""
        print(f"  [{event.id}] {event.title}{time_str} ({event.category})")
        if event.description:
            print(f"      {event.description}")

def get_date_input(prompt: str) -> str:
    """Get date input from user with validation"""
    while True:
        date_str = input(f"{prompt} (YYYY-MM-DD): ").strip()
        if not date_str:
            return ""
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

def get_time_input(prompt: str) -> str:
    """Get time input from user with validation"""
    while True:
        time_str = input(f"{prompt} (HH:MM, optional): ").strip()
        if not time_str:
            return ""
        
        try:
            datetime.strptime(time_str, "%H:%M")
            return time_str
        except ValueError:
            print("Invalid time format. Please use HH:MM.")

def main():
    """Main function to run the calendar app"""
    calendar_app = BasicCalendarApp()
    
    while True:
        print("\n=== Basic Calendar App ===")
        print("1. Add Event")
        print("2. View Today's Events")
        print("3. View Upcoming Events")
        print("4. View Monthly Calendar")
        print("5. View Events by Date")
        print("6. Search Events")
        print("7. View Events by Category")
        print("8. Edit Event")
        print("9. Delete Event")
        print("10. View Statistics")
        print("11. Export Events")
        print("12. Manage Categories")
        print("0. Exit")
        
        try:
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                print("\n=== Add New Event ===")
                title = input("Event title: ").strip()
                if not title:
                    print("Title cannot be empty!")
                    continue
                
                date_str = get_date_input("Event date")
                if not date_str:
                    print("Date is required!")
                    continue
                
                time_str = get_time_input("Event time")
                description = input("Description (optional): ").strip()
                
                print("\nAvailable categories:")
                categories = list(calendar_app.categories)
                for i, cat in enumerate(categories, 1):
                    print(f"  {i}. {cat}")
                
                cat_choice = input("Choose category (number) or enter new: ").strip()
                try:
                    cat_idx = int(cat_choice) - 1
                    if 0 <= cat_idx < len(categories):
                        category = categories[cat_idx]
                    else:
                        category = "General"
                except ValueError:
                    category = cat_choice if cat_choice else "General"
                
                event = calendar_app.add_event(title, date_str, time_str, description, category)
                if event:
                    print(f"Event added successfully! ID: {event.id}")
                else:
                    print("Failed to add event.")
            
            elif choice == '2':
                today_events = calendar_app.get_today_events()
                display_events(today_events, "Today's Events")
            
            elif choice == '3':
                try:
                    days = int(input("Show events for next how many days? (default 7): ").strip() or "7")
                    upcoming = calendar_app.get_upcoming_events(days)
                    display_events(upcoming, f"Upcoming Events (Next {days} days)")
                except ValueError:
                    print("Invalid number of days!")
            
            elif choice == '4':
                try:
                    year = int(input("Enter year (default current): ").strip() or str(date.today().year))
                    month = int(input("Enter month (1-12, default current): ").strip() or str(date.today().month))
                    
                    if 1 <= month <= 12:
                        calendar_view = calendar_app.get_calendar_view(year, month)
                        print(calendar_view)
                        
                        # Show events for the month
                        month_events = calendar_app.get_events_for_month(year, month)
                        if month_events:
                            display_events(month_events, f"Events in {calendar.month_name[month]} {year}")
                    else:
                        print("Invalid month! Please enter 1-12.")
                except ValueError:
                    print("Invalid year or month!")
            
            elif choice == '5':
                date_str = get_date_input("Enter date to view")
                if date_str:
                    date_events = calendar_app.get_events_for_date(date_str)
                    display_events(date_events, f"Events on {date_str}")
            
            elif choice == '6':
                query = input("Enter search query: ").strip()
                if query:
                    results = calendar_app.search_events(query)
                    display_events(results, f"Search Results for '{query}'")
            
            elif choice == '7':
                print("\nAvailable categories:")
                for category in sorted(calendar_app.categories):
                    print(f"  • {category}")
                
                category = input("\nEnter category name: ").strip()
                if category:
                    category_events = calendar_app.get_events_by_category(category)
                    display_events(category_events, f"Events in '{category}' Category")
            
            elif choice == '8':
                event_id = input("Enter event ID to edit: ").strip()
                event = calendar_app.get_event(event_id)
                if event:
                    print(f"\nCurrent event: {event}")
                    print(f"Date: {event.date}, Time: {event.time or 'Not set'}")
                    print(f"Description: {event.description or 'None'}")
                    print(f"Category: {event.category}")
                    
                    print("\nLeave blank to keep current value:")
                    new_title = input(f"New title ({event.title}): ").strip()
                    new_date = get_date_input(f"New date ({event.date})")
                    new_time = get_time_input(f"New time ({event.time or 'Not set'})")
                    new_desc = input(f"New description ({event.description or 'None'}): ").strip()
                    new_cat = input(f"New category ({event.category}): ").strip()
                    
                    success = calendar_app.update_event(
                        event_id,
                        new_title if new_title else None,
                        new_date if new_date else None,
                        new_time if new_time else None,
                        new_desc if new_desc else None,
                        new_cat if new_cat else None
                    )
                    
                    if success:
                        print("Event updated successfully!")
                    else:
                        print("Failed to update event.")
                else:
                    print("Event not found!")
            
            elif choice == '9':
                event_id = input("Enter event ID to delete: ").strip()
                event = calendar_app.get_event(event_id)
                if event:
                    confirm = input(f"Are you sure you want to delete '{event.title}'? (y/N): ").strip().lower()
                    if confirm == 'y':
                        if calendar_app.delete_event(event_id):
                            print("Event deleted successfully!")
                        else:
                            print("Failed to delete event.")
                    else:
                        print("Deletion cancelled.")
                else:
                    print("Event not found!")
            
            elif choice == '10':
                stats = calendar_app.get_event_statistics()
                if stats:
                    print("\n=== Calendar Statistics ===")
                    print(f"Total events: {stats['total_events']}")
                    print(f"Today's events: {stats['today_events']}")
                    print(f"Upcoming events (30 days): {stats['upcoming_events']}")
                    print(f"Total categories: {stats['total_categories']}")
                    
                    if stats['categories']:
                        print("\nEvents by category:")
                        for category, count in sorted(stats['categories'].items()):
                            print(f"  {category}: {count}")
                    
                    if stats['monthly_distribution']:
                        print("\nMonthly distribution:")
                        for month, count in sorted(stats['monthly_distribution'].items()):
                            print(f"  {month}: {count}")
                else:
                    print("No events to show statistics for.")
            
            elif choice == '11':
                filename = input("Enter filename for export (e.g., my_events.txt): ").strip()
                if not filename:
                    filename = f"calendar_export_{date.today().strftime('%Y%m%d')}.txt"
                
                start_date = get_date_input("Start date (optional, leave blank for all)")
                end_date = get_date_input("End date (optional, leave blank for all)")
                
                calendar_app.export_events(filename, start_date, end_date)
            
            elif choice == '12':
                print("\n=== Manage Categories ===")
                print("Current categories:")
                for category in sorted(calendar_app.categories):
                    print(f"  • {category}")
                
                new_category = input("\nAdd new category (or press Enter to skip): ").strip()
                if new_category:
                    calendar_app.add_category(new_category)
                    print(f"Category '{new_category}' added!")
            
            elif choice == '0':
                print("Thank you for using Basic Calendar App!")
                break
            
            else:
                print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
