# Advanced Hangman Game with Database

import sqlite3
import random
import json
import hashlib
import datetime
from typing import List, Dict, Optional, Tuple
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
from pathlib import Path
import re
import string

class HangmanDatabase:
    """Database manager for hangman game"""
    
    def __init__(self, db_path: str = "hangman.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Words table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    difficulty INTEGER NOT NULL,
                    hint TEXT,
                    added_date TEXT NOT NULL,
                    used_count INTEGER DEFAULT 0
                )
            """)
            
            # Players table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_date TEXT NOT NULL,
                    last_login TEXT,
                    total_games INTEGER DEFAULT 0,
                    total_wins INTEGER DEFAULT 0,
                    total_losses INTEGER DEFAULT 0,
                    best_streak INTEGER DEFAULT 0,
                    current_streak INTEGER DEFAULT 0
                )
            """)
            
            # Games table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    word_id INTEGER NOT NULL,
                    guessed_letters TEXT NOT NULL,
                    wrong_guesses INTEGER NOT NULL,
                    max_wrong_guesses INTEGER NOT NULL,
                    won BOOLEAN NOT NULL,
                    duration_seconds INTEGER,
                    game_date TEXT NOT NULL,
                    FOREIGN KEY (player_id) REFERENCES players (id),
                    FOREIGN KEY (word_id) REFERENCES words (id)
                )
            """)
            
            # Achievements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER NOT NULL,
                    achievement_type TEXT NOT NULL,
                    achievement_data TEXT,
                    earned_date TEXT NOT NULL,
                    FOREIGN KEY (player_id) REFERENCES players (id)
                )
            """)
            
            conn.commit()
            
            # Add default words if database is empty
            self.add_default_words()
    
    def add_default_words(self):
        """Add default word list if database is empty"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM words")
            if cursor.fetchone()[0] == 0:
                default_words = [
                    # Animals
                    ("elephant", "animals", 2, "Large mammal with trunk"),
                    ("giraffe", "animals", 2, "Tallest animal in the world"),
                    ("penguin", "animals", 2, "Flightless bird from Antarctica"),
                    ("dolphin", "animals", 2, "Intelligent marine mammal"),
                    ("butterfly", "animals", 3, "Colorful flying insect"),
                    ("rhinoceros", "animals", 4, "Large horned mammal"),
                    ("hippopotamus", "animals", 4, "Large water-loving mammal"),
                    
                    # Countries
                    ("france", "countries", 2, "European country known for Eiffel Tower"),
                    ("japan", "countries", 1, "Island nation in East Asia"),
                    ("brazil", "countries", 2, "Largest South American country"),
                    ("australia", "countries", 3, "Island continent"),
                    ("switzerland", "countries", 4, "Neutral European country"),
                    ("madagascar", "countries", 4, "Large island off Africa"),
                    
                    # Technology
                    ("computer", "technology", 2, "Electronic device for processing data"),
                    ("internet", "technology", 2, "Global network of computers"),
                    ("smartphone", "technology", 3, "Portable communication device"),
                    ("artificial", "technology", 4, "Type of intelligence in machines"),
                    ("programming", "technology", 4, "Process of creating software"),
                    ("cybersecurity", "technology", 5, "Protection of digital systems"),
                    
                    # Science
                    ("gravity", "science", 2, "Force that pulls objects down"),
                    ("molecule", "science", 3, "Smallest unit of a compound"),
                    ("photosynthesis", "science", 5, "Process plants use to make food"),
                    ("ecosystem", "science", 3, "Community of living organisms"),
                    ("chromosome", "science", 4, "Structure containing DNA"),
                    ("quantum", "science", 3, "Related to atomic particles"),
                    
                    # Sports
                    ("basketball", "sports", 3, "Sport played with orange ball"),
                    ("swimming", "sports", 2, "Water sport activity"),
                    ("marathon", "sports", 3, "Long distance running race"),
                    ("gymnastics", "sports", 4, "Sport involving flexibility and strength"),
                    ("badminton", "sports", 3, "Racquet sport with shuttlecock"),
                    
                    # Food
                    ("chocolate", "food", 2, "Sweet treat made from cocoa"),
                    ("spaghetti", "food", 3, "Long thin pasta"),
                    ("hamburger", "food", 3, "Ground meat sandwich"),
                    ("pizza", "food", 1, "Italian flatbread with toppings"),
                    ("sandwich", "food", 2, "Food between two pieces of bread"),
                ]
                
                for word, category, difficulty, hint in default_words:
                    self.add_word(word, category, difficulty, hint)
    
    def add_word(self, word: str, category: str, difficulty: int, hint: str = ""):
        """Add a new word to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO words (word, category, difficulty, hint, added_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (word.lower(), category.lower(), difficulty, hint, datetime.datetime.now().isoformat()))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False  # Word already exists
    
    def get_random_word(self, category: str = None, difficulty: int = None) -> Optional[Dict]:
        """Get a random word from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT id, word, category, difficulty, hint FROM words WHERE 1=1"
            params = []
            
            if category:
                query += " AND category = ?"
                params.append(category.lower())
            
            if difficulty:
                query += " AND difficulty = ?"
                params.append(difficulty)
            
            cursor.execute(query, params)
            words = cursor.fetchall()
            
            if words:
                word_data = random.choice(words)
                return {
                    'id': word_data[0],
                    'word': word_data[1],
                    'category': word_data[2],
                    'difficulty': word_data[3],
                    'hint': word_data[4]
                }
            return None
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM words ORDER BY category")
            return [row[0] for row in cursor.fetchall()]
    
    def create_player(self, username: str, password: str) -> bool:
        """Create a new player account"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO players (username, password_hash, created_date)
                    VALUES (?, ?, ?)
                """, (username, password_hash, datetime.datetime.now().isoformat()))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False  # Username already exists
    
    def authenticate_player(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate player login"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, total_games, total_wins, total_losses, 
                       best_streak, current_streak
                FROM players 
                WHERE username = ? AND password_hash = ?
            """, (username, password_hash))
            
            result = cursor.fetchone()
            if result:
                # Update last login
                cursor.execute("""
                    UPDATE players SET last_login = ? WHERE id = ?
                """, (datetime.datetime.now().isoformat(), result[0]))
                conn.commit()
                
                return {
                    'id': result[0],
                    'username': result[1],
                    'total_games': result[2],
                    'total_wins': result[3],
                    'total_losses': result[4],
                    'best_streak': result[5],
                    'current_streak': result[6]
                }
            return None
    
    def save_game(self, player_id: int, word_id: int, guessed_letters: List[str], 
                  wrong_guesses: int, max_wrong_guesses: int, won: bool, duration: int):
        """Save game result to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Save game
            cursor.execute("""
                INSERT INTO games (player_id, word_id, guessed_letters, wrong_guesses,
                                 max_wrong_guesses, won, duration_seconds, game_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (player_id, word_id, json.dumps(guessed_letters), wrong_guesses,
                  max_wrong_guesses, won, duration, datetime.datetime.now().isoformat()))
            
            # Update player stats
            if won:
                cursor.execute("""
                    UPDATE players 
                    SET total_games = total_games + 1, 
                        total_wins = total_wins + 1,
                        current_streak = current_streak + 1
                    WHERE id = ?
                """, (player_id,))
                
                # Check for new best streak
                cursor.execute("SELECT current_streak, best_streak FROM players WHERE id = ?", (player_id,))
                current, best = cursor.fetchone()
                if current > best:
                    cursor.execute("UPDATE players SET best_streak = ? WHERE id = ?", (current, player_id))
            else:
                cursor.execute("""
                    UPDATE players 
                    SET total_games = total_games + 1, 
                        total_losses = total_losses + 1,
                        current_streak = 0
                    WHERE id = ?
                """, (player_id,))
            
            # Update word usage count
            cursor.execute("UPDATE words SET used_count = used_count + 1 WHERE id = ?", (word_id,))
            
            conn.commit()
    
    def get_player_stats(self, player_id: int) -> Dict:
        """Get detailed player statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Basic stats
            cursor.execute("""
                SELECT username, total_games, total_wins, total_losses, 
                       best_streak, current_streak, created_date
                FROM players WHERE id = ?
            """, (player_id,))
            
            player_data = cursor.fetchone()
            
            # Recent games
            cursor.execute("""
                SELECT g.won, g.duration_seconds, g.game_date, w.word, w.category
                FROM games g
                JOIN words w ON g.word_id = w.id
                WHERE g.player_id = ?
                ORDER BY g.game_date DESC
                LIMIT 10
            """, (player_id,))
            
            recent_games = cursor.fetchall()
            
            # Category performance
            cursor.execute("""
                SELECT w.category, COUNT(*) as games, SUM(g.won) as wins
                FROM games g
                JOIN words w ON g.word_id = w.id
                WHERE g.player_id = ?
                GROUP BY w.category
            """, (player_id,))
            
            category_stats = cursor.fetchall()
            
            win_rate = (player_data[2] / player_data[1] * 100) if player_data[1] > 0 else 0
            
            return {
                'username': player_data[0],
                'total_games': player_data[1],
                'total_wins': player_data[2],
                'total_losses': player_data[3],
                'win_rate': win_rate,
                'best_streak': player_data[4],
                'current_streak': player_data[5],
                'member_since': player_data[6],
                'recent_games': recent_games,
                'category_stats': category_stats
            }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top players leaderboard"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, total_games, total_wins, total_losses, 
                       best_streak, current_streak,
                       CASE WHEN total_games > 0 THEN ROUND(total_wins * 100.0 / total_games, 1) ELSE 0 END as win_rate
                FROM players
                WHERE total_games > 0
                ORDER BY total_wins DESC, win_rate DESC, best_streak DESC
                LIMIT ?
            """, (limit,))
            
            return [
                {
                    'username': row[0],
                    'total_games': row[1],
                    'total_wins': row[2],
                    'total_losses': row[3],
                    'best_streak': row[4],
                    'current_streak': row[5],
                    'win_rate': row[6]
                }
                for row in cursor.fetchall()
            ]

class HangmanGame:
    """Hangman game logic"""
    
    def __init__(self, database: HangmanDatabase):
        self.db = database
        self.reset_game()
        
        # Hangman drawings
        self.hangman_stages = [
            """
   +---+
   |   |
       |
       |
       |
       |
=========
""",
            """
   +---+
   |   |
   O   |
       |
       |
       |
=========
""",
            """
   +---+
   |   |
   O   |
   |   |
       |
       |
=========
""",
            """
   +---+
   |   |
   O   |
  /|   |
       |
       |
=========
""",
            """
   +---+
   |   |
   O   |
  /|\\  |
       |
       |
=========
""",
            """
   +---+
   |   |
   O   |
  /|\\  |
  /    |
       |
=========
""",
            """
   +---+
   |   |
   O   |
  /|\\  |
  / \\  |
       |
=========
"""
        ]
    
    def reset_game(self):
        """Reset game state"""
        self.current_word_data = None
        self.current_word = ""
        self.guessed_letters = []
        self.wrong_guesses = 0
        self.max_wrong_guesses = 6
        self.game_won = False
        self.game_over = False
        self.start_time = None
        self.end_time = None
    
    def start_new_game(self, category: str = None, difficulty: int = None) -> bool:
        """Start a new game"""
        self.reset_game()
        
        self.current_word_data = self.db.get_random_word(category, difficulty)
        if not self.current_word_data:
            return False
        
        self.current_word = self.current_word_data['word'].upper()
        self.start_time = datetime.datetime.now()
        return True
    
    def make_guess(self, letter: str) -> Dict:
        """Make a letter guess"""
        letter = letter.upper()
        
        if self.game_over:
            return {'status': 'game_over', 'message': 'Game is already over'}
        
        if letter in self.guessed_letters:
            return {'status': 'already_guessed', 'message': f'You already guessed "{letter}"'}
        
        if not letter.isalpha() or len(letter) != 1:
            return {'status': 'invalid', 'message': 'Please enter a single letter'}
        
        self.guessed_letters.append(letter)
        
        if letter in self.current_word:
            # Correct guess
            if self.is_word_complete():
                self.game_won = True
                self.game_over = True
                self.end_time = datetime.datetime.now()
                return {
                    'status': 'won',
                    'message': f'Congratulations! You won! The word was "{self.current_word}"',
                    'correct': True
                }
            else:
                return {
                    'status': 'correct',
                    'message': f'Good guess! "{letter}" is in the word',
                    'correct': True
                }
        else:
            # Wrong guess
            self.wrong_guesses += 1
            
            if self.wrong_guesses >= self.max_wrong_guesses:
                self.game_over = True
                self.end_time = datetime.datetime.now()
                return {
                    'status': 'lost',
                    'message': f'Game over! The word was "{self.current_word}"',
                    'correct': False
                }
            else:
                remaining = self.max_wrong_guesses - self.wrong_guesses
                return {
                    'status': 'wrong',
                    'message': f'Sorry, "{letter}" is not in the word. {remaining} guesses remaining',
                    'correct': False
                }
    
    def guess_word(self, word: str) -> Dict:
        """Guess the entire word"""
        word = word.upper().strip()
        
        if self.game_over:
            return {'status': 'game_over', 'message': 'Game is already over'}
        
        if word == self.current_word:
            self.game_won = True
            self.game_over = True
            self.end_time = datetime.datetime.now()
            return {
                'status': 'won',
                'message': f'Excellent! You guessed the word "{self.current_word}"!',
                'correct': True
            }
        else:
            self.wrong_guesses += 1
            
            if self.wrong_guesses >= self.max_wrong_guesses:
                self.game_over = True
                self.end_time = datetime.datetime.now()
                return {
                    'status': 'lost',
                    'message': f'Wrong word! Game over! The word was "{self.current_word}"',
                    'correct': False
                }
            else:
                remaining = self.max_wrong_guesses - self.wrong_guesses
                return {
                    'status': 'wrong',
                    'message': f'Wrong word! {remaining} guesses remaining',
                    'correct': False
                }
    
    def is_word_complete(self) -> bool:
        """Check if all letters in the word have been guessed"""
        return all(letter in self.guessed_letters for letter in self.current_word if letter.isalpha())
    
    def get_display_word(self) -> str:
        """Get the word with guessed letters revealed and others as underscores"""
        display = ""
        for letter in self.current_word:
            if letter.isalpha():
                if letter in self.guessed_letters:
                    display += letter + " "
                else:
                    display += "_ "
            else:
                display += letter + " "
        return display.strip()
    
    def get_hangman_display(self) -> str:
        """Get current hangman drawing"""
        return self.hangman_stages[min(self.wrong_guesses, len(self.hangman_stages) - 1)]
    
    def get_game_duration(self) -> int:
        """Get game duration in seconds"""
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds())
        return 0
    
    def save_game_result(self, player_id: int):
        """Save game result to database"""
        if self.current_word_data and self.game_over:
            duration = self.get_game_duration()
            self.db.save_game(
                player_id=player_id,
                word_id=self.current_word_data['id'],
                guessed_letters=self.guessed_letters,
                wrong_guesses=self.wrong_guesses,
                max_wrong_guesses=self.max_wrong_guesses,
                won=self.game_won,
                duration=duration
            )

class HangmanGUI:
    """GUI for Hangman game"""
    
    def __init__(self):
        self.db = HangmanDatabase()
        self.game = HangmanGame(self.db)
        self.current_player = None
        
        self.root = tk.Tk()
        self.root.title("Advanced Hangman Game")
        self.root.geometry("900x700")
        
        self.setup_ui()
        self.show_login_screen()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Game tab
        self.game_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.game_frame, text="Game")
        self.setup_game_tab()
        
        # Stats tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        self.setup_stats_tab()
        
        # Leaderboard tab
        self.leaderboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.leaderboard_frame, text="Leaderboard")
        self.setup_leaderboard_tab()
        
        # Words tab
        self.words_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.words_frame, text="Add Words")
        self.setup_words_tab()
    
    def setup_game_tab(self):
        """Setup game tab"""
        # Main game frame
        main_frame = ttk.Frame(self.game_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Player info
        player_frame = ttk.LabelFrame(main_frame, text="Player", padding="5")
        player_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.player_label = ttk.Label(player_frame, text="Not logged in", font=("TkDefaultFont", 10, "bold"))
        self.player_label.pack(side=tk.LEFT)
        
        ttk.Button(player_frame, text="Logout", command=self.logout).pack(side=tk.RIGHT)
        
        # Game controls
        controls_frame = ttk.LabelFrame(main_frame, text="Game Controls", padding="5")
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Category and difficulty selection
        settings_frame = ttk.Frame(controls_frame)
        settings_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(settings_frame, text="Category:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar(value="any")
        self.category_combo = ttk.Combobox(settings_frame, textvariable=self.category_var, width=15)
        self.category_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(settings_frame, text="Difficulty:").pack(side=tk.LEFT)
        self.difficulty_var = tk.StringVar(value="any")
        difficulty_combo = ttk.Combobox(settings_frame, textvariable=self.difficulty_var, 
                                       values=["any", "1", "2", "3", "4", "5"], width=10)
        difficulty_combo.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(controls_frame, text="New Game", command=self.start_new_game).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Hint", command=self.show_hint).pack(side=tk.LEFT)
        
        # Game display
        game_display_frame = ttk.Frame(main_frame)
        game_display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - hangman drawing
        left_frame = ttk.Frame(game_display_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.hangman_text = tk.Text(left_frame, height=10, width=20, font=("Courier", 12), state=tk.DISABLED)
        self.hangman_text.pack(pady=10)
        
        # Right side - game info
        right_frame = ttk.Frame(game_display_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Word display
        self.word_label = ttk.Label(right_frame, text="", font=("TkDefaultFont", 16, "bold"))
        self.word_label.pack(pady=10)
        
        # Category and difficulty info
        self.info_label = ttk.Label(right_frame, text="")
        self.info_label.pack()
        
        # Guessed letters
        self.guessed_label = ttk.Label(right_frame, text="Guessed letters: ")
        self.guessed_label.pack(pady=(10, 5))
        
        # Game status
        self.status_label = ttk.Label(right_frame, text="Click 'New Game' to start", foreground="blue")
        self.status_label.pack(pady=5)
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Letter input
        letter_frame = ttk.LabelFrame(input_frame, text="Guess Letter", padding="5")
        letter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.letter_var = tk.StringVar()
        self.letter_entry = ttk.Entry(letter_frame, textvariable=self.letter_var, width=5, font=("TkDefaultFont", 14))
        self.letter_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.letter_entry.bind('<Return>', lambda e: self.guess_letter())
        self.letter_entry.bind('<KeyRelease>', self.on_letter_keyrelease)
        
        ttk.Button(letter_frame, text="Guess Letter", command=self.guess_letter).pack(side=tk.LEFT)
        
        # Word input
        word_frame = ttk.LabelFrame(input_frame, text="Guess Word", padding="5")
        word_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.word_var = tk.StringVar()
        self.word_entry = ttk.Entry(word_frame, textvariable=self.word_var, font=("TkDefaultFont", 14))
        self.word_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.word_entry.bind('<Return>', lambda e: self.guess_word())
        
        ttk.Button(word_frame, text="Guess Word", command=self.guess_word).pack(side=tk.LEFT)
        
        self.update_categories()
    
    def setup_stats_tab(self):
        """Setup statistics tab"""
        stats_main = ttk.Frame(self.stats_frame, padding="10")
        stats_main.pack(fill=tk.BOTH, expand=True)
        
        # Stats display
        self.stats_text = scrolledtext.ScrolledText(stats_main, height=25, state=tk.DISABLED)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Refresh button
        ttk.Button(stats_main, text="Refresh Stats", command=self.update_stats).pack(pady=10)
    
    def setup_leaderboard_tab(self):
        """Setup leaderboard tab"""
        leader_main = ttk.Frame(self.leaderboard_frame, padding="10")
        leader_main.pack(fill=tk.BOTH, expand=True)
        
        # Leaderboard display
        self.leaderboard_text = scrolledtext.ScrolledText(leader_main, height=25, state=tk.DISABLED)
        self.leaderboard_text.pack(fill=tk.BOTH, expand=True)
        
        # Refresh button
        ttk.Button(leader_main, text="Refresh Leaderboard", command=self.update_leaderboard).pack(pady=10)
    
    def setup_words_tab(self):
        """Setup add words tab"""
        words_main = ttk.Frame(self.words_frame, padding="10")
        words_main.pack(fill=tk.BOTH, expand=True)
        
        # Add word form
        form_frame = ttk.LabelFrame(words_main, text="Add New Word", padding="10")
        form_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Word input
        ttk.Label(form_frame, text="Word:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.new_word_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.new_word_var, width=20).grid(row=0, column=1, padx=(5, 0), pady=2, sticky=tk.W)
        
        # Category input
        ttk.Label(form_frame, text="Category:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.new_category_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.new_category_var, width=20).grid(row=1, column=1, padx=(5, 0), pady=2, sticky=tk.W)
        
        # Difficulty input
        ttk.Label(form_frame, text="Difficulty (1-5):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.new_difficulty_var = tk.StringVar(value="1")
        ttk.Spinbox(form_frame, from_=1, to=5, textvariable=self.new_difficulty_var, width=18).grid(row=2, column=1, padx=(5, 0), pady=2, sticky=tk.W)
        
        # Hint input
        ttk.Label(form_frame, text="Hint:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.new_hint_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.new_hint_var, width=40).grid(row=3, column=1, padx=(5, 0), pady=2, sticky=tk.W)
        
        # Add button
        ttk.Button(form_frame, text="Add Word", command=self.add_word).grid(row=4, column=1, padx=(5, 0), pady=10, sticky=tk.W)
        
        # Instructions
        instructions = """
Instructions for adding words:
• Enter a single word (no spaces)
• Choose an appropriate category
• Set difficulty from 1 (easy) to 5 (very hard)
• Provide a helpful hint
• Words will be automatically converted to lowercase
        """
        
        ttk.Label(words_main, text=instructions, justify=tk.LEFT).pack(anchor=tk.W)
    
    def show_login_screen(self):
        """Show login/register dialog"""
        login_window = tk.Toplevel(self.root)
        login_window.title("Login / Register")
        login_window.geometry("400x300")
        login_window.transient(self.root)
        login_window.grab_set()
        
        # Center the window
        login_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 250, self.root.winfo_rooty() + 200))
        
        main_frame = ttk.Frame(login_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Welcome to Hangman!", font=("TkDefaultFont", 16, "bold")).pack(pady=(0, 20))
        
        # Username
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W)
        username_var = tk.StringVar()
        username_entry = ttk.Entry(main_frame, textvariable=username_var, width=30)
        username_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Password
        ttk.Label(main_frame, text="Password:").pack(anchor=tk.W)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=password_var, width=30, show="*")
        password_entry.pack(fill=tk.X, pady=(5, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def login():
            username = username_var.get().strip()
            password = password_var.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password")
                return
            
            player = self.db.authenticate_player(username, password)
            if player:
                self.current_player = player
                self.player_label.config(text=f"Player: {player['username']} | Wins: {player['total_wins']} | Streak: {player['current_streak']}")
                login_window.destroy()
                self.update_stats()
                self.update_leaderboard()
            else:
                messagebox.showerror("Error", "Invalid username or password")
        
        def register():
            username = username_var.get().strip()
            password = password_var.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password")
                return
            
            if len(username) < 3:
                messagebox.showerror("Error", "Username must be at least 3 characters long")
                return
            
            if len(password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long")
                return
            
            if self.db.create_player(username, password):
                messagebox.showinfo("Success", "Account created successfully! You can now log in.")
                # Auto-login
                player = self.db.authenticate_player(username, password)
                if player:
                    self.current_player = player
                    self.player_label.config(text=f"Player: {player['username']} | Wins: {player['total_wins']} | Streak: {player['current_streak']}")
                    login_window.destroy()
                    self.update_stats()
                    self.update_leaderboard()
            else:
                messagebox.showerror("Error", "Username already exists")
        
        ttk.Button(button_frame, text="Login", command=login).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Register", command=register).pack(side=tk.LEFT)
        
        # Enter key bindings
        username_entry.bind('<Return>', lambda e: password_entry.focus())
        password_entry.bind('<Return>', lambda e: login())
        
        username_entry.focus()
    
    def logout(self):
        """Logout current player"""
        self.current_player = None
        self.player_label.config(text="Not logged in")
        self.game.reset_game()
        self.update_display()
        self.show_login_screen()
    
    def update_categories(self):
        """Update category dropdown"""
        categories = ["any"] + self.db.get_categories()
        self.category_combo['values'] = categories
    
    def start_new_game(self):
        """Start a new hangman game"""
        if not self.current_player:
            messagebox.showerror("Error", "Please log in first")
            return
        
        category = self.category_var.get() if self.category_var.get() != "any" else None
        difficulty = int(self.difficulty_var.get()) if self.difficulty_var.get() != "any" else None
        
        if self.game.start_new_game(category, difficulty):
            self.update_display()
            self.letter_entry.focus()
            self.status_label.config(text="Game started! Guess a letter or the whole word.", foreground="blue")
        else:
            messagebox.showerror("Error", "No words found with the selected criteria")
    
    def guess_letter(self):
        """Process letter guess"""
        if not self.current_player:
            return
        
        letter = self.letter_var.get().strip()
        if not letter:
            return
        
        result = self.game.make_guess(letter)
        self.letter_var.set("")
        
        self.update_display()
        self.show_guess_result(result)
        
        if self.game.game_over:
            self.game.save_game_result(self.current_player['id'])
            self.update_player_info()
    
    def guess_word(self):
        """Process word guess"""
        if not self.current_player:
            return
        
        word = self.word_var.get().strip()
        if not word:
            return
        
        result = self.game.guess_word(word)
        self.word_var.set("")
        
        self.update_display()
        self.show_guess_result(result)
        
        if self.game.game_over:
            self.game.save_game_result(self.current_player['id'])
            self.update_player_info()
    
    def show_hint(self):
        """Show hint for current word"""
        if self.game.current_word_data and self.game.current_word_data['hint']:
            hint = self.game.current_word_data['hint']
            messagebox.showinfo("Hint", f"Hint: {hint}")
        else:
            messagebox.showinfo("Hint", "No hint available for this word")
    
    def on_letter_keyrelease(self, event):
        """Handle letter entry key release"""
        # Limit to single character and convert to uppercase
        text = self.letter_var.get().upper()
        if len(text) > 1:
            self.letter_var.set(text[-1])
        elif text and not text.isalpha():
            self.letter_var.set("")
    
    def update_display(self):
        """Update game display"""
        # Update hangman drawing
        self.hangman_text.config(state=tk.NORMAL)
        self.hangman_text.delete(1.0, tk.END)
        self.hangman_text.insert(tk.END, self.game.get_hangman_display())
        self.hangman_text.config(state=tk.DISABLED)
        
        # Update word display
        if self.game.current_word:
            self.word_label.config(text=self.game.get_display_word())
            
            # Update info
            category = self.game.current_word_data['category'].title()
            difficulty = self.game.current_word_data['difficulty']
            self.info_label.config(text=f"Category: {category} | Difficulty: {difficulty}")
        else:
            self.word_label.config(text="Click 'New Game' to start")
            self.info_label.config(text="")
        
        # Update guessed letters
        if self.game.guessed_letters:
            guessed = ", ".join(sorted(self.game.guessed_letters))
            self.guessed_label.config(text=f"Guessed letters: {guessed}")
        else:
            self.guessed_label.config(text="Guessed letters: ")
    
    def show_guess_result(self, result):
        """Show result of guess"""
        status = result['status']
        message = result['message']
        
        if status == 'won':
            self.status_label.config(text=message, foreground="green")
        elif status == 'lost':
            self.status_label.config(text=message, foreground="red")
        elif status == 'correct':
            self.status_label.config(text=message, foreground="blue")
        elif status == 'wrong':
            self.status_label.config(text=message, foreground="orange")
        else:
            self.status_label.config(text=message, foreground="gray")
    
    def update_player_info(self):
        """Update player info after game"""
        if self.current_player:
            # Refresh player stats
            updated_player = self.db.authenticate_player(
                self.current_player['username'], 
                ""  # We'll need to modify this to not require password for refresh
            )
            if updated_player:
                self.current_player = updated_player
                self.player_label.config(text=f"Player: {updated_player['username']} | Wins: {updated_player['total_wins']} | Streak: {updated_player['current_streak']}")
    
    def add_word(self):
        """Add new word to database"""
        word = self.new_word_var.get().strip()
        category = self.new_category_var.get().strip()
        hint = self.new_hint_var.get().strip()
        
        try:
            difficulty = int(self.new_difficulty_var.get())
        except ValueError:
            messagebox.showerror("Error", "Difficulty must be a number between 1 and 5")
            return
        
        if not word or not category:
            messagebox.showerror("Error", "Please enter both word and category")
            return
        
        if not word.replace(" ", "").isalpha():
            messagebox.showerror("Error", "Word should contain only letters (spaces will be removed)")
            return
        
        # Remove spaces from word
        word = word.replace(" ", "")
        
        if self.db.add_word(word, category, difficulty, hint):
            messagebox.showinfo("Success", f"Word '{word}' added successfully!")
            
            # Clear form
            self.new_word_var.set("")
            self.new_category_var.set("")
            self.new_difficulty_var.set("1")
            self.new_hint_var.set("")
            
            # Update categories
            self.update_categories()
        else:
            messagebox.showerror("Error", "Word already exists in database")
    
    def update_stats(self):
        """Update statistics display"""
        if not self.current_player:
            return
        
        stats = self.db.get_player_stats(self.current_player['id'])
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        # Basic stats
        self.stats_text.insert(tk.END, f"=== Statistics for {stats['username']} ===\n\n")
        self.stats_text.insert(tk.END, f"Member since: {stats['member_since'][:10]}\n")
        self.stats_text.insert(tk.END, f"Total games: {stats['total_games']}\n")
        self.stats_text.insert(tk.END, f"Total wins: {stats['total_wins']}\n")
        self.stats_text.insert(tk.END, f"Total losses: {stats['total_losses']}\n")
        self.stats_text.insert(tk.END, f"Win rate: {stats['win_rate']:.1f}%\n")
        self.stats_text.insert(tk.END, f"Best streak: {stats['best_streak']}\n")
        self.stats_text.insert(tk.END, f"Current streak: {stats['current_streak']}\n\n")
        
        # Category performance
        if stats['category_stats']:
            self.stats_text.insert(tk.END, "=== Performance by Category ===\n")
            for category, games, wins in stats['category_stats']:
                win_rate = (wins / games * 100) if games > 0 else 0
                self.stats_text.insert(tk.END, f"{category.title()}: {wins}/{games} ({win_rate:.1f}%)\n")
            self.stats_text.insert(tk.END, "\n")
        
        # Recent games
        if stats['recent_games']:
            self.stats_text.insert(tk.END, "=== Recent Games ===\n")
            for won, duration, date, word, category in stats['recent_games']:
                result = "Won" if won else "Lost"
                duration_str = f"{duration}s" if duration else "N/A"
                date_str = date[:10]  # Just the date part
                self.stats_text.insert(tk.END, f"{date_str}: {result} - {word.upper()} ({category}) - {duration_str}\n")
        
        self.stats_text.config(state=tk.DISABLED)
    
    def update_leaderboard(self):
        """Update leaderboard display"""
        leaderboard = self.db.get_leaderboard(20)
        
        self.leaderboard_text.config(state=tk.NORMAL)
        self.leaderboard_text.delete(1.0, tk.END)
        
        self.leaderboard_text.insert(tk.END, "=== LEADERBOARD ===\n\n")
        self.leaderboard_text.insert(tk.END, f"{'Rank':<5}{'Player':<15}{'Wins':<6}{'Games':<7}{'Win%':<6}{'Streak':<8}\n")
        self.leaderboard_text.insert(tk.END, "-" * 60 + "\n")
        
        for i, player in enumerate(leaderboard, 1):
            rank = f"{i}."
            username = player['username'][:14]
            wins = str(player['total_wins'])
            games = str(player['total_games'])
            win_rate = f"{player['win_rate']}%"
            streak = str(player['best_streak'])
            
            line = f"{rank:<5}{username:<15}{wins:<6}{games:<7}{win_rate:<6}{streak:<8}\n"
            self.leaderboard_text.insert(tk.END, line)
        
        self.leaderboard_text.config(state=tk.DISABLED)
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function"""
    app = HangmanGUI()
    app.run()

if __name__ == "__main__":
    main()
