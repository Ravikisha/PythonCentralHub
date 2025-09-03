# Personal Diary Application

import datetime
import os
import json

class DiaryEntry:
    def __init__(self, date, title, content, mood="neutral"):
        self.date = date
        self.title = title
        self.content = content
        self.mood = mood
    
    def to_dict(self):
        return {
            'date': self.date.isoformat(),
            'title': self.title,
            'content': self.content,
            'mood': self.mood
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            datetime.datetime.fromisoformat(data['date']),
            data['title'],
            data['content'],
            data.get('mood', 'neutral')
        )

class PersonalDiary:
    def __init__(self, filename="diary.json"):
        self.filename = filename
        self.entries = []
        self.load_entries()
    
    def load_entries(self):
        """Load entries from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.entries = [DiaryEntry.from_dict(entry) for entry in data]
            except (json.JSONDecodeError, KeyError):
                print("Warning: Could not load diary entries. Starting fresh.")
                self.entries = []
    
    def save_entries(self):
        """Save entries to file"""
        with open(self.filename, 'w') as f:
            json.dump([entry.to_dict() for entry in self.entries], f, indent=2)
    
    def add_entry(self, title, content, mood="neutral"):
        """Add a new diary entry"""
        entry = DiaryEntry(datetime.datetime.now(), title, content, mood)
        self.entries.append(entry)
        self.save_entries()
        print("Entry added successfully!")
    
    def view_entries(self):
        """Display all diary entries"""
        if not self.entries:
            print("No diary entries found.")
            return
        
        print("\n" + "="*50)
        print("YOUR DIARY ENTRIES")
        print("="*50)
        
        for i, entry in enumerate(self.entries, 1):
            print(f"\nEntry #{i}")
            print(f"Date: {entry.date.strftime('%Y-%m-%d %H:%M')}")
            print(f"Title: {entry.title}")
            print(f"Mood: {entry.mood}")
            print(f"Content: {entry.content}")
            print("-" * 30)
    
    def search_entries(self, keyword):
        """Search entries by keyword"""
        found_entries = []
        keyword_lower = keyword.lower()
        
        for entry in self.entries:
            if (keyword_lower in entry.title.lower() or 
                keyword_lower in entry.content.lower()):
                found_entries.append(entry)
        
        if not found_entries:
            print(f"No entries found containing '{keyword}'")
            return
        
        print(f"\nFound {len(found_entries)} entries containing '{keyword}':")
        print("="*50)
        
        for i, entry in enumerate(found_entries, 1):
            print(f"\nResult #{i}")
            print(f"Date: {entry.date.strftime('%Y-%m-%d %H:%M')}")
            print(f"Title: {entry.title}")
            print(f"Mood: {entry.mood}")
            print(f"Content: {entry.content}")
            print("-" * 30)
    
    def filter_by_mood(self, mood):
        """Filter entries by mood"""
        mood_entries = [entry for entry in self.entries if entry.mood.lower() == mood.lower()]
        
        if not mood_entries:
            print(f"No entries found with mood '{mood}'")
            return
        
        print(f"\nEntries with mood '{mood}':")
        print("="*50)
        
        for i, entry in enumerate(mood_entries, 1):
            print(f"\nEntry #{i}")
            print(f"Date: {entry.date.strftime('%Y-%m-%d %H:%M')}")
            print(f"Title: {entry.title}")
            print(f"Content: {entry.content}")
            print("-" * 30)
    
    def get_statistics(self):
        """Display diary statistics"""
        if not self.entries:
            print("No entries to analyze.")
            return
        
        total_entries = len(self.entries)
        mood_counts = {}
        
        for entry in self.entries:
            mood = entry.mood
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        print(f"\nDiary Statistics:")
        print("="*30)
        print(f"Total entries: {total_entries}")
        print(f"First entry: {min(self.entries, key=lambda x: x.date).date.strftime('%Y-%m-%d')}")
        print(f"Latest entry: {max(self.entries, key=lambda x: x.date).date.strftime('%Y-%m-%d')}")
        print(f"\nMood distribution:")
        for mood, count in mood_counts.items():
            percentage = (count / total_entries) * 100
            print(f"  {mood}: {count} ({percentage:.1f}%)")

def main():
    diary = PersonalDiary()
    
    while True:
        print("\n" + "="*40)
        print("PERSONAL DIARY APPLICATION")
        print("="*40)
        print("1. Add new entry")
        print("2. View all entries")
        print("3. Search entries")
        print("4. Filter by mood")
        print("5. View statistics")
        print("6. Exit")
        
        choice = input("\nSelect an option (1-6): ").strip()
        
        if choice == '1':
            print("\nAdding new diary entry:")
            title = input("Enter title: ").strip()
            print("Enter content (press Enter twice to finish):")
            content_lines = []
            while True:
                line = input()
                if line == "":
                    break
                content_lines.append(line)
            content = "\n".join(content_lines)
            
            print("Select mood:")
            print("1. Happy  2. Sad  3. Excited  4. Anxious  5. Peaceful  6. Other")
            mood_choice = input("Enter choice (1-6): ").strip()
            
            mood_map = {'1': 'happy', '2': 'sad', '3': 'excited', 
                       '4': 'anxious', '5': 'peaceful', '6': 'other'}
            mood = mood_map.get(mood_choice, 'neutral')
            
            if mood == 'other':
                mood = input("Enter custom mood: ").strip() or 'neutral'
            
            diary.add_entry(title, content, mood)
        
        elif choice == '2':
            diary.view_entries()
        
        elif choice == '3':
            keyword = input("Enter search keyword: ").strip()
            if keyword:
                diary.search_entries(keyword)
        
        elif choice == '4':
            mood = input("Enter mood to filter by: ").strip()
            if mood:
                diary.filter_by_mood(mood)
        
        elif choice == '5':
            diary.get_statistics()
        
        elif choice == '6':
            print("Thank you for using Personal Diary. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
