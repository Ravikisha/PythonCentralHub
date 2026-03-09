#!/usr/bin/env python3
"""
Basic Music Streaming Application
A comprehensive music player with streaming capabilities, playlist management, and audio effects.

Features:
- Audio playback with various formats support
- Playlist creation and management
- Volume controls and equalizer
- Music library organization
- Search and filter functionality
- Audio effects and visualization
- Online radio streaming
- Music metadata display
- Shuffle and repeat modes
- Sleep timer and alarms

Requirements:
- pygame
- mutagen (for metadata)
- tkinter (built-in)
- threading (built-in)
- os (built-in)
- json (built-in)

Author: Python Central Hub
Date: 2025-09-06
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import json
import threading
import time
import random
from pathlib import Path
import webbrowser
from urllib.parse import urlparse

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("⚠️ pygame not available. Install with: pip install pygame")

try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3NoHeaderError
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    print("⚠️ mutagen not available. Install with: pip install mutagen")


class MusicPlayer:
    """Main music streaming application."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Music Streaming Player")
        self.root.geometry("1000x700")
        
        # Audio control variables
        self.current_song = None
        self.current_position = 0
        self.song_length = 0
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        self.is_muted = False
        self.previous_volume = 0.7
        
        # Playback modes
        self.shuffle_mode = False
        self.repeat_mode = "none"  # none, one, all
        
        # Data storage
        self.playlist = []
        self.current_playlist_index = 0
        self.music_library = []
        self.favorites = []
        self.radio_stations = []
        self.settings = {
            "default_volume": 0.7,
            "auto_crossfade": False,
            "visualizations": True,
            "last_directory": str(Path.home()),
            "theme": "dark"
        }
        
        # Data files
        self.library_file = Path("music_library.json")
        self.playlists_file = Path("playlists.json")
        self.settings_file = Path("music_settings.json")
        
        # Control variables
        self.position_update_job = None
        self.crossfade_enabled = False
        
        # Load saved data
        self.load_data()
        
        # Setup GUI
        self.setup_gui()
        
        # Set initial volume
        if PYGAME_AVAILABLE:
            pygame.mixer.music.set_volume(self.volume)
        
        # Start position updating
        self.start_position_updates()
    
    def setup_gui(self):
        """Setup the main GUI interface."""
        # Create menu
        self.create_menu()
        
        # Main layout
        self.create_main_layout()
        
        # Apply theme
        self.apply_theme()
    
    def create_menu(self):
        """Create application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Files", command=self.add_files)
        file_menu.add_command(label="Add Folder", command=self.add_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Import Playlist", command=self.import_playlist)
        file_menu.add_command(label="Export Playlist", command=self.export_playlist)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Playback menu
        playback_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Playback", menu=playback_menu)
        playback_menu.add_command(label="Play/Pause", command=self.toggle_playback)
        playback_menu.add_command(label="Stop", command=self.stop_playback)
        playback_menu.add_command(label="Previous", command=self.previous_song)
        playback_menu.add_command(label="Next", command=self.next_song)
        playback_menu.add_separator()
        playback_menu.add_command(label="Shuffle", command=self.toggle_shuffle)
        playback_menu.add_command(label="Repeat", command=self.cycle_repeat_mode)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Library", command=lambda: self.notebook.select(0))
        view_menu.add_command(label="Playlist", command=lambda: self.notebook.select(1))
        view_menu.add_command(label="Radio", command=lambda: self.notebook.select(2))
        view_menu.add_separator()
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Equalizer", command=self.show_equalizer)
        tools_menu.add_command(label="Sleep Timer", command=self.show_sleep_timer)
        tools_menu.add_command(label="Settings", command=self.show_settings)
        tools_menu.add_separator()
        tools_menu.add_command(label="Scan for Music", command=self.scan_for_music)
    
    def create_main_layout(self):
        """Create main application layout."""
        # Top frame - Now playing info
        self.create_now_playing_frame()
        
        # Middle frame - Controls
        self.create_controls_frame()
        
        # Bottom frame - Content (Library, Playlist, Radio)
        self.create_content_frame()
        
        # Status bar
        self.create_status_bar()
    
    def create_now_playing_frame(self):
        """Create now playing information frame."""
        now_playing_frame = ttk.LabelFrame(self.root, text="Now Playing")
        now_playing_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Album art placeholder
        art_frame = ttk.Frame(now_playing_frame)
        art_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.album_art_label = ttk.Label(art_frame, text="♪", font=("Arial", 48), width=8)
        self.album_art_label.pack()
        
        # Song info
        info_frame = ttk.Frame(now_playing_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        
        self.song_title_var = tk.StringVar(value="No song selected")
        song_title_label = ttk.Label(info_frame, textvariable=self.song_title_var, font=("Arial", 14, "bold"))
        song_title_label.pack(anchor=tk.W)
        
        self.song_artist_var = tk.StringVar(value="")
        song_artist_label = ttk.Label(info_frame, textvariable=self.song_artist_var, font=("Arial", 11))
        song_artist_label.pack(anchor=tk.W)
        
        self.song_album_var = tk.StringVar(value="")
        song_album_label = ttk.Label(info_frame, textvariable=self.song_album_var, font=("Arial", 10))
        song_album_label.pack(anchor=tk.W)
        
        # Progress bar and time
        progress_frame = ttk.Frame(info_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.time_current_var = tk.StringVar(value="0:00")
        ttk.Label(progress_frame, textvariable=self.time_current_var).pack(side=tk.LEFT)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(
            progress_frame, 
            from_=0, to=100, 
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            command=self.on_progress_change
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.time_total_var = tk.StringVar(value="0:00")
        ttk.Label(progress_frame, textvariable=self.time_total_var).pack(side=tk.RIGHT)
    
    def create_controls_frame(self):
        """Create playback controls frame."""
        controls_frame = ttk.Frame(self.root)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Main playback controls
        main_controls = ttk.Frame(controls_frame)
        main_controls.pack(side=tk.LEFT)
        
        # Previous button
        ttk.Button(main_controls, text="⏮", command=self.previous_song, width=4).pack(side=tk.LEFT, padx=2)
        
        # Play/Pause button
        self.play_button_text = tk.StringVar(value="▶")
        self.play_button = ttk.Button(
            main_controls, 
            textvariable=self.play_button_text, 
            command=self.toggle_playback,
            width=4
        )
        self.play_button.pack(side=tk.LEFT, padx=2)
        
        # Stop button
        ttk.Button(main_controls, text="⏹", command=self.stop_playback, width=4).pack(side=tk.LEFT, padx=2)
        
        # Next button
        ttk.Button(main_controls, text="⏭", command=self.next_song, width=4).pack(side=tk.LEFT, padx=2)
        
        # Mode controls
        mode_controls = ttk.Frame(controls_frame)
        mode_controls.pack(side=tk.LEFT, padx=20)
        
        # Shuffle button
        self.shuffle_button_text = tk.StringVar(value="🔀")
        self.shuffle_button = ttk.Button(
            mode_controls,
            textvariable=self.shuffle_button_text,
            command=self.toggle_shuffle,
            width=4
        )
        self.shuffle_button.pack(side=tk.LEFT, padx=2)
        
        # Repeat button
        self.repeat_button_text = tk.StringVar(value="🔁")
        self.repeat_button = ttk.Button(
            mode_controls,
            textvariable=self.repeat_button_text,
            command=self.cycle_repeat_mode,
            width=4
        )
        self.repeat_button.pack(side=tk.LEFT, padx=2)
        
        # Volume controls
        volume_frame = ttk.Frame(controls_frame)
        volume_frame.pack(side=tk.RIGHT)
        
        # Mute button
        self.mute_button_text = tk.StringVar(value="🔊")
        ttk.Button(
            volume_frame,
            textvariable=self.mute_button_text,
            command=self.toggle_mute,
            width=4
        ).pack(side=tk.LEFT, padx=2)
        
        # Volume scale
        self.volume_var = tk.DoubleVar(value=self.volume * 100)
        volume_scale = ttk.Scale(
            volume_frame,
            from_=0, to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            command=self.on_volume_change,
            length=100
        )
        volume_scale.pack(side=tk.LEFT, padx=5)
        
        # Volume label
        self.volume_label = ttk.Label(volume_frame, text=f"{int(self.volume * 100)}%")
        self.volume_label.pack(side=tk.LEFT, padx=5)
    
    def create_content_frame(self):
        """Create content frame with tabs."""
        # Create notebook for different views
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Library tab
        self.create_library_tab()
        
        # Playlist tab
        self.create_playlist_tab()
        
        # Radio tab
        self.create_radio_tab()
        
        # Favorites tab
        self.create_favorites_tab()
    
    def create_library_tab(self):
        """Create music library tab."""
        library_frame = ttk.Frame(self.notebook)
        self.notebook.add(library_frame, text="📚 Library")
        
        # Search and filter frame
        search_frame = ttk.Frame(library_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.library_search_var = tk.StringVar()
        self.library_search_entry = ttk.Entry(search_frame, textvariable=self.library_search_var, width=20)
        self.library_search_entry.pack(side=tk.LEFT, padx=5)
        self.library_search_var.trace('w', self.filter_library)
        
        ttk.Button(search_frame, text="🔍", command=self.filter_library).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.clear_library_search).pack(side=tk.LEFT, padx=5)
        
        # Sort controls
        ttk.Label(search_frame, text="Sort by:").pack(side=tk.LEFT, padx=(20, 5))
        self.library_sort_var = tk.StringVar(value="Title")
        sort_combo = ttk.Combobox(
            search_frame,
            textvariable=self.library_sort_var,
            values=["Title", "Artist", "Album", "Duration", "Date Added"],
            state="readonly",
            width=12
        )
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind('<<ComboboxSelected>>', self.sort_library)
        
        # Library list
        library_list_frame = ttk.Frame(library_frame)
        library_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Library treeview
        columns = ("Title", "Artist", "Album", "Duration", "Path")
        self.library_tree = ttk.Treeview(library_list_frame, columns=columns, show="headings")
        
        self.library_tree.heading("Title", text="Title")
        self.library_tree.heading("Artist", text="Artist")
        self.library_tree.heading("Album", text="Album")
        self.library_tree.heading("Duration", text="Duration")
        self.library_tree.heading("Path", text="Path")
        
        self.library_tree.column("Title", width=200)
        self.library_tree.column("Artist", width=150)
        self.library_tree.column("Album", width=150)
        self.library_tree.column("Duration", width=80)
        self.library_tree.column("Path", width=300)
        
        # Scrollbars
        library_v_scrollbar = ttk.Scrollbar(library_list_frame, orient=tk.VERTICAL, command=self.library_tree.yview)
        library_h_scrollbar = ttk.Scrollbar(library_list_frame, orient=tk.HORIZONTAL, command=self.library_tree.xview)
        self.library_tree.configure(yscrollcommand=library_v_scrollbar.set, xscrollcommand=library_h_scrollbar.set)
        
        # Pack library tree and scrollbars
        self.library_tree.grid(row=0, column=0, sticky="nsew")
        library_v_scrollbar.grid(row=0, column=1, sticky="ns")
        library_h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        library_list_frame.grid_rowconfigure(0, weight=1)
        library_list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.library_tree.bind('<Double-1>', self.play_selected_library_song)
        self.library_tree.bind('<Button-3>', self.show_library_context_menu)
        
        # Library controls
        library_controls = ttk.Frame(library_frame)
        library_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(library_controls, text="▶ Play", command=self.play_selected_library_song).pack(side=tk.LEFT, padx=5)
        ttk.Button(library_controls, text="+ Add to Playlist", command=self.add_to_playlist_from_library).pack(side=tk.LEFT, padx=5)
        ttk.Button(library_controls, text="⭐ Add to Favorites", command=self.add_to_favorites_from_library).pack(side=tk.LEFT, padx=5)
        ttk.Button(library_controls, text="🗑 Remove", command=self.remove_from_library).pack(side=tk.LEFT, padx=5)
        
        # Statistics
        self.library_stats_label = ttk.Label(library_controls, text="0 songs")
        self.library_stats_label.pack(side=tk.RIGHT, padx=5)
    
    def create_playlist_tab(self):
        """Create playlist tab."""
        playlist_frame = ttk.Frame(self.notebook)
        self.notebook.add(playlist_frame, text="📋 Playlist")
        
        # Playlist controls
        playlist_controls = ttk.Frame(playlist_frame)
        playlist_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(playlist_controls, text="🔄 Shuffle Playlist", command=self.shuffle_playlist).pack(side=tk.LEFT, padx=5)
        ttk.Button(playlist_controls, text="🗑 Clear Playlist", command=self.clear_playlist).pack(side=tk.LEFT, padx=5)
        ttk.Button(playlist_controls, text="💾 Save Playlist", command=self.save_playlist).pack(side=tk.LEFT, padx=5)
        ttk.Button(playlist_controls, text="📁 Load Playlist", command=self.load_playlist).pack(side=tk.LEFT, padx=5)
        
        # Current playlist label
        self.playlist_info_label = ttk.Label(playlist_controls, text="Playlist: 0 songs")
        self.playlist_info_label.pack(side=tk.RIGHT, padx=5)
        
        # Playlist list
        playlist_list_frame = ttk.Frame(playlist_frame)
        playlist_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Playlist treeview
        columns = ("#", "Title", "Artist", "Album", "Duration")
        self.playlist_tree = ttk.Treeview(playlist_list_frame, columns=columns, show="headings")
        
        self.playlist_tree.heading("#", text="#")
        self.playlist_tree.heading("Title", text="Title")
        self.playlist_tree.heading("Artist", text="Artist")
        self.playlist_tree.heading("Album", text="Album")
        self.playlist_tree.heading("Duration", text="Duration")
        
        self.playlist_tree.column("#", width=40)
        self.playlist_tree.column("Title", width=250)
        self.playlist_tree.column("Artist", width=150)
        self.playlist_tree.column("Album", width=150)
        self.playlist_tree.column("Duration", width=80)
        
        # Scrollbars for playlist
        playlist_v_scrollbar = ttk.Scrollbar(playlist_list_frame, orient=tk.VERTICAL, command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscrollcommand=playlist_v_scrollbar.set)
        
        self.playlist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        playlist_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.playlist_tree.bind('<Double-1>', self.play_selected_playlist_song)
        self.playlist_tree.bind('<Button-3>', self.show_playlist_context_menu)
        
        # Playlist action controls
        playlist_actions = ttk.Frame(playlist_frame)
        playlist_actions.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(playlist_actions, text="▶ Play Selected", command=self.play_selected_playlist_song).pack(side=tk.LEFT, padx=5)
        ttk.Button(playlist_actions, text="🔼 Move Up", command=self.move_playlist_item_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(playlist_actions, text="🔽 Move Down", command=self.move_playlist_item_down).pack(side=tk.LEFT, padx=5)
        ttk.Button(playlist_actions, text="❌ Remove", command=self.remove_from_playlist).pack(side=tk.LEFT, padx=5)
    
    def create_radio_tab(self):
        """Create radio stations tab."""
        radio_frame = ttk.Frame(self.notebook)
        self.notebook.add(radio_frame, text="📻 Radio")
        
        # Radio controls
        radio_controls = ttk.Frame(radio_frame)
        radio_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(radio_controls, text="+ Add Station", command=self.add_radio_station).pack(side=tk.LEFT, padx=5)
        ttk.Button(radio_controls, text="✏ Edit Station", command=self.edit_radio_station).pack(side=tk.LEFT, padx=5)
        ttk.Button(radio_controls, text="🗑 Remove Station", command=self.remove_radio_station).pack(side=tk.LEFT, padx=5)
        
        # Radio stations list
        radio_list_frame = ttk.Frame(radio_frame)
        radio_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Radio stations treeview
        columns = ("Name", "URL", "Genre", "Bitrate")
        self.radio_tree = ttk.Treeview(radio_list_frame, columns=columns, show="headings")
        
        self.radio_tree.heading("Name", text="Station Name")
        self.radio_tree.heading("URL", text="Stream URL")
        self.radio_tree.heading("Genre", text="Genre")
        self.radio_tree.heading("Bitrate", text="Bitrate")
        
        self.radio_tree.column("Name", width=200)
        self.radio_tree.column("URL", width=300)
        self.radio_tree.column("Genre", width=100)
        self.radio_tree.column("Bitrate", width=80)
        
        # Scrollbar for radio
        radio_scrollbar = ttk.Scrollbar(radio_list_frame, orient=tk.VERTICAL, command=self.radio_tree.yview)
        self.radio_tree.configure(yscrollcommand=radio_scrollbar.set)
        
        self.radio_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        radio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.radio_tree.bind('<Double-1>', self.play_radio_station)
        
        # Radio action controls
        radio_actions = ttk.Frame(radio_frame)
        radio_actions.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(radio_actions, text="▶ Play Station", command=self.play_radio_station).pack(side=tk.LEFT, padx=5)
        ttk.Button(radio_actions, text="⏹ Stop Radio", command=self.stop_radio).pack(side=tk.LEFT, padx=5)
        
        # Add some default radio stations
        self.add_default_radio_stations()
    
    def create_favorites_tab(self):
        """Create favorites tab."""
        favorites_frame = ttk.Frame(self.notebook)
        self.notebook.add(favorites_frame, text="⭐ Favorites")
        
        # Favorites controls
        favorites_controls = ttk.Frame(favorites_frame)
        favorites_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(favorites_controls, text="▶ Play All", command=self.play_all_favorites).pack(side=tk.LEFT, padx=5)
        ttk.Button(favorites_controls, text="+ Add to Playlist", command=self.add_favorites_to_playlist).pack(side=tk.LEFT, padx=5)
        ttk.Button(favorites_controls, text="🗑 Clear Favorites", command=self.clear_favorites).pack(side=tk.LEFT, padx=5)
        
        # Favorites list
        favorites_list_frame = ttk.Frame(favorites_frame)
        favorites_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Favorites treeview
        columns = ("Title", "Artist", "Album", "Duration")
        self.favorites_tree = ttk.Treeview(favorites_list_frame, columns=columns, show="headings")
        
        self.favorites_tree.heading("Title", text="Title")
        self.favorites_tree.heading("Artist", text="Artist")
        self.favorites_tree.heading("Album", text="Album")
        self.favorites_tree.heading("Duration", text="Duration")
        
        self.favorites_tree.column("Title", width=250)
        self.favorites_tree.column("Artist", width=150)
        self.favorites_tree.column("Album", width=150)
        self.favorites_tree.column("Duration", width=80)
        
        # Scrollbar for favorites
        favorites_scrollbar = ttk.Scrollbar(favorites_list_frame, orient=tk.VERTICAL, command=self.favorites_tree.yview)
        self.favorites_tree.configure(yscrollcommand=favorites_scrollbar.set)
        
        self.favorites_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        favorites_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.favorites_tree.bind('<Double-1>', self.play_selected_favorite)
        self.favorites_tree.bind('<Button-3>', self.show_favorites_context_menu)
        
        # Favorites statistics
        self.favorites_stats_label = ttk.Label(favorites_controls, text="0 favorites")
        self.favorites_stats_label.pack(side=tk.RIGHT, padx=5)
    
    def create_status_bar(self):
        """Create status bar."""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.playback_mode_label = ttk.Label(self.status_frame, text="Stopped", relief=tk.SUNKEN)
        self.playback_mode_label.pack(side=tk.RIGHT)
    
    # Data management methods
    def load_data(self):
        """Load saved data from files."""
        try:
            if self.library_file.exists():
                with open(self.library_file, 'r') as f:
                    self.music_library = json.load(f)
        except Exception as e:
            print(f"Error loading library: {e}")
        
        try:
            if self.playlists_file.exists():
                with open(self.playlists_file, 'r') as f:
                    data = json.load(f)
                    self.playlist = data.get('current_playlist', [])
                    self.favorites = data.get('favorites', [])
                    self.radio_stations = data.get('radio_stations', [])
        except Exception as e:
            print(f"Error loading playlists: {e}")
        
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_data(self):
        """Save data to files."""
        try:
            with open(self.library_file, 'w') as f:
                json.dump(self.music_library, f, indent=2)
        except Exception as e:
            print(f"Error saving library: {e}")
        
        try:
            data = {
                'current_playlist': self.playlist,
                'favorites': self.favorites,
                'radio_stations': self.radio_stations
            }
            with open(self.playlists_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving playlists: {e}")
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    # File management methods
    def add_files(self):
        """Add music files to library."""
        if not PYGAME_AVAILABLE:
            messagebox.showerror("Error", "pygame not available")
            return
        
        filetypes = [
            ("Audio files", "*.mp3;*.wav;*.ogg;*.flac;*.m4a"),
            ("MP3 files", "*.mp3"),
            ("WAV files", "*.wav"),
            ("OGG files", "*.ogg"),
            ("FLAC files", "*.flac"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select music files",
            filetypes=filetypes,
            initialdir=self.settings.get("last_directory", str(Path.home()))
        )
        
        if files:
            self.settings["last_directory"] = str(Path(files[0]).parent)
            
            # Add files to library
            added_count = 0
            for file_path in files:
                if self.add_to_library(file_path):
                    added_count += 1
            
            self.update_library_display()
            self.save_data()
            self.update_status(f"Added {added_count} files to library")
    
    def add_folder(self):
        """Add music folder to library."""
        if not PYGAME_AVAILABLE:
            messagebox.showerror("Error", "pygame not available")
            return
        
        folder = filedialog.askdirectory(
            title="Select music folder",
            initialdir=self.settings.get("last_directory", str(Path.home()))
        )
        
        if folder:
            self.settings["last_directory"] = folder
            
            # Scan folder for music files
            audio_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma'}
            added_count = 0
            
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if Path(file).suffix.lower() in audio_extensions:
                        file_path = os.path.join(root, file)
                        if self.add_to_library(file_path):
                            added_count += 1
            
            self.update_library_display()
            self.save_data()
            self.update_status(f"Added {added_count} files from folder")
    
    def add_to_library(self, file_path):
        """Add single file to library."""
        # Check if file already exists
        if any(song['path'] == file_path for song in self.music_library):
            return False
        
        try:
            # Get metadata
            metadata = self.get_metadata(file_path)
            
            song_info = {
                'path': file_path,
                'title': metadata.get('title', Path(file_path).stem),
                'artist': metadata.get('artist', 'Unknown Artist'),
                'album': metadata.get('album', 'Unknown Album'),
                'duration': metadata.get('duration', 0),
                'genre': metadata.get('genre', 'Unknown'),
                'year': metadata.get('year', ''),
                'track': metadata.get('track', ''),
                'date_added': time.time()
            }
            
            self.music_library.append(song_info)
            return True
            
        except Exception as e:
            print(f"Error adding file {file_path}: {e}")
            return False
    
    def get_metadata(self, file_path):
        """Extract metadata from audio file."""
        metadata = {}
        
        if MUTAGEN_AVAILABLE:
            try:
                audio_file = MutagenFile(file_path)
                if audio_file is not None:
                    # Extract common metadata
                    metadata['title'] = str(audio_file.get('TIT2', [Path(file_path).stem])[0]) if 'TIT2' in audio_file else Path(file_path).stem
                    metadata['artist'] = str(audio_file.get('TPE1', ['Unknown Artist'])[0]) if 'TPE1' in audio_file else 'Unknown Artist'
                    metadata['album'] = str(audio_file.get('TALB', ['Unknown Album'])[0]) if 'TALB' in audio_file else 'Unknown Album'
                    metadata['genre'] = str(audio_file.get('TCON', ['Unknown'])[0]) if 'TCON' in audio_file else 'Unknown'
                    metadata['year'] = str(audio_file.get('TDRC', [''])[0]) if 'TDRC' in audio_file else ''
                    metadata['track'] = str(audio_file.get('TRCK', [''])[0]) if 'TRCK' in audio_file else ''
                    
                    # Get duration
                    if hasattr(audio_file, 'info') and hasattr(audio_file.info, 'length'):
                        metadata['duration'] = int(audio_file.info.length)
                    
            except Exception as e:
                print(f"Error reading metadata for {file_path}: {e}")
        
        # Fallback values
        if 'title' not in metadata:
            metadata['title'] = Path(file_path).stem
        if 'artist' not in metadata:
            metadata['artist'] = 'Unknown Artist'
        if 'album' not in metadata:
            metadata['album'] = 'Unknown Album'
        if 'duration' not in metadata:
            metadata['duration'] = 0
        
        return metadata
    
    def format_duration(self, seconds):
        """Format duration in seconds to MM:SS format."""
        if seconds <= 0:
            return "0:00"
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"
    
    # Display update methods
    def update_library_display(self):
        """Update library display."""
        # Clear existing items
        for item in self.library_tree.get_children():
            self.library_tree.delete(item)
        
        # Apply search filter
        search_term = self.library_search_var.get().lower()
        filtered_library = self.music_library
        
        if search_term:
            filtered_library = [
                song for song in self.music_library
                if (search_term in song.get('title', '').lower() or
                    search_term in song.get('artist', '').lower() or
                    search_term in song.get('album', '').lower())
            ]
        
        # Sort library
        sort_by = self.library_sort_var.get()
        if sort_by == "Title":
            filtered_library.sort(key=lambda x: x.get('title', '').lower())
        elif sort_by == "Artist":
            filtered_library.sort(key=lambda x: x.get('artist', '').lower())
        elif sort_by == "Album":
            filtered_library.sort(key=lambda x: x.get('album', '').lower())
        elif sort_by == "Duration":
            filtered_library.sort(key=lambda x: x.get('duration', 0))
        elif sort_by == "Date Added":
            filtered_library.sort(key=lambda x: x.get('date_added', 0), reverse=True)
        
        # Add songs to tree
        for song in filtered_library:
            duration_str = self.format_duration(song.get('duration', 0))
            self.library_tree.insert('', tk.END, values=(
                song.get('title', 'Unknown'),
                song.get('artist', 'Unknown Artist'),
                song.get('album', 'Unknown Album'),
                duration_str,
                song.get('path', '')
            ))
        
        # Update statistics
        self.library_stats_label.config(text=f"{len(filtered_library)} songs")
    
    def update_playlist_display(self):
        """Update playlist display."""
        # Clear existing items
        for item in self.playlist_tree.get_children():
            self.playlist_tree.delete(item)
        
        # Add songs to playlist tree
        for i, song in enumerate(self.playlist):
            duration_str = self.format_duration(song.get('duration', 0))
            
            # Highlight currently playing song
            tags = ()
            if i == self.current_playlist_index and self.is_playing:
                tags = ('current',)
            
            self.playlist_tree.insert('', tk.END, values=(
                i + 1,
                song.get('title', 'Unknown'),
                song.get('artist', 'Unknown Artist'),
                song.get('album', 'Unknown Album'),
                duration_str
            ), tags=tags)
        
        # Configure tag colors
        self.playlist_tree.tag_configure('current', background='lightblue')
        
        # Update info label
        total_duration = sum(song.get('duration', 0) for song in self.playlist)
        self.playlist_info_label.config(
            text=f"Playlist: {len(self.playlist)} songs, {self.format_duration(total_duration)}"
        )
    
    def update_favorites_display(self):
        """Update favorites display."""
        # Clear existing items
        for item in self.favorites_tree.get_children():
            self.favorites_tree.delete(item)
        
        # Add favorites to tree
        for song in self.favorites:
            duration_str = self.format_duration(song.get('duration', 0))
            self.favorites_tree.insert('', tk.END, values=(
                song.get('title', 'Unknown'),
                song.get('artist', 'Unknown Artist'),
                song.get('album', 'Unknown Album'),
                duration_str
            ))
        
        # Update statistics
        self.favorites_stats_label.config(text=f"{len(self.favorites)} favorites")
    
    def update_radio_display(self):
        """Update radio stations display."""
        # Clear existing items
        for item in self.radio_tree.get_children():
            self.radio_tree.delete(item)
        
        # Add radio stations to tree
        for station in self.radio_stations:
            self.radio_tree.insert(
                '', tk.END,
                values=(
                    station.get("name", ""),
                    station.get("url", ""),
                    station.get("genre", ""),
                    station.get("bitrate", "")
                )
            )
    
    # Playback control methods
    def toggle_playback(self):
        """Toggle play/pause."""
        if not PYGAME_AVAILABLE:
            messagebox.showerror("Error", "pygame not available")
            return
        
        if not self.current_song and self.playlist:
            # Start playing first song in playlist
            self.play_song(0)
        elif self.is_playing:
            self.pause_playback()
        elif self.is_paused:
            self.resume_playback()
    
    def play_song(self, index=None):
        """Play song at specified index."""
        if not PYGAME_AVAILABLE:
            return
        
        if index is not None:
            if 0 <= index < len(self.playlist):
                self.current_playlist_index = index
            else:
                return
        
        if not self.playlist:
            self.update_status("No songs in playlist")
            return
        
        try:
            self.current_song = self.playlist[self.current_playlist_index]
            song_path = self.current_song['path']
            
            # Check if file exists
            if not os.path.exists(song_path):
                messagebox.showerror("Error", f"File not found: {song_path}")
                return
            
            # Load and play song
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            
            self.is_playing = True
            self.is_paused = False
            self.current_position = 0
            self.song_length = self.current_song.get('duration', 0)
            
            # Update display
            self.update_now_playing_display()
            self.update_playlist_display()
            self.play_button_text.set("⏸")
            self.playback_mode_label.config(text="Playing")
            
            self.update_status(f"Playing: {self.current_song.get('title', 'Unknown')}")
            
        except Exception as e:
            messagebox.showerror("Playback Error", f"Failed to play song: {e}")
    
    def pause_playback(self):
        """Pause playback."""
        if PYGAME_AVAILABLE and self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.is_paused = True
            self.play_button_text.set("▶")
            self.playback_mode_label.config(text="Paused")
            self.update_status("Paused")
    
    def resume_playback(self):
        """Resume playback."""
        if PYGAME_AVAILABLE and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.is_paused = False
            self.play_button_text.set("⏸")
            self.playback_mode_label.config(text="Playing")
            self.update_status("Resumed")
    
    def stop_playback(self):
        """Stop playback."""
        if PYGAME_AVAILABLE:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.current_position = 0
            self.play_button_text.set("▶")
            self.playback_mode_label.config(text="Stopped")
            self.update_progress_display()
            self.update_playlist_display()
            self.update_status("Stopped")
    
    def next_song(self):
        """Play next song."""
        if not self.playlist:
            return
        
        if self.shuffle_mode:
            # Random next song
            self.current_playlist_index = random.randint(0, len(self.playlist) - 1)
        else:
            # Next song in order
            self.current_playlist_index += 1
            if self.current_playlist_index >= len(self.playlist):
                if self.repeat_mode == "all":
                    self.current_playlist_index = 0
                else:
                    self.stop_playback()
                    return
        
        self.play_song()
    
    def previous_song(self):
        """Play previous song."""
        if not self.playlist:
            return
        
        if self.shuffle_mode:
            # Random previous song
            self.current_playlist_index = random.randint(0, len(self.playlist) - 1)
        else:
            # Previous song in order
            self.current_playlist_index -= 1
            if self.current_playlist_index < 0:
                if self.repeat_mode == "all":
                    self.current_playlist_index = len(self.playlist) - 1
                else:
                    self.current_playlist_index = 0
        
        self.play_song()
    
    def toggle_shuffle(self):
        """Toggle shuffle mode."""
        self.shuffle_mode = not self.shuffle_mode
        if self.shuffle_mode:
            self.shuffle_button_text.set("🔀*")
            self.update_status("Shuffle enabled")
        else:
            self.shuffle_button_text.set("🔀")
            self.update_status("Shuffle disabled")
    
    def cycle_repeat_mode(self):
        """Cycle through repeat modes."""
        if self.repeat_mode == "none":
            self.repeat_mode = "one"
            self.repeat_button_text.set("🔂")
            self.update_status("Repeat one enabled")
        elif self.repeat_mode == "one":
            self.repeat_mode = "all"
            self.repeat_button_text.set("🔁*")
            self.update_status("Repeat all enabled")
        else:
            self.repeat_mode = "none"
            self.repeat_button_text.set("🔁")
            self.update_status("Repeat disabled")
    
    def toggle_mute(self):
        """Toggle mute."""
        if self.is_muted:
            # Unmute
            self.volume = self.previous_volume
            self.is_muted = False
            self.mute_button_text.set("🔊")
        else:
            # Mute
            self.previous_volume = self.volume
            self.volume = 0
            self.is_muted = True
            self.mute_button_text.set("🔇")
        
        if PYGAME_AVAILABLE:
            pygame.mixer.music.set_volume(self.volume)
        
        self.volume_var.set(self.volume * 100)
        self.volume_label.config(text=f"{int(self.volume * 100)}%")
    
    def on_volume_change(self, value):
        """Handle volume change."""
        self.volume = float(value) / 100.0
        
        if PYGAME_AVAILABLE:
            pygame.mixer.music.set_volume(self.volume)
        
        self.volume_label.config(text=f"{int(self.volume * 100)}%")
        
        # Update mute status
        if self.volume > 0 and self.is_muted:
            self.is_muted = False
            self.mute_button_text.set("🔊")
        elif self.volume == 0 and not self.is_muted:
            self.is_muted = True
            self.mute_button_text.set("🔇")
    
    def on_progress_change(self, value):
        """Handle progress bar change."""
        if self.current_song and self.song_length > 0:
            new_position = (float(value) / 100.0) * self.song_length
            self.current_position = new_position
            # Note: pygame doesn't support seeking, this is a placeholder
    
    # Display update methods
    def update_now_playing_display(self):
        """Update now playing information."""
        if self.current_song:
            self.song_title_var.set(self.current_song.get('title', 'Unknown'))
            self.song_artist_var.set(self.current_song.get('artist', 'Unknown Artist'))
            self.song_album_var.set(self.current_song.get('album', 'Unknown Album'))
            self.time_total_var.set(self.format_duration(self.song_length))
        else:
            self.song_title_var.set("No song selected")
            self.song_artist_var.set("")
            self.song_album_var.set("")
            self.time_total_var.set("0:00")
    
    def update_progress_display(self):
        """Update progress display."""
        if self.current_song and self.song_length > 0:
            progress = (self.current_position / self.song_length) * 100
            self.progress_var.set(progress)
            self.time_current_var.set(self.format_duration(self.current_position))
        else:
            self.progress_var.set(0)
            self.time_current_var.set("0:00")
    
    def start_position_updates(self):
        """Start updating playback position."""
        if self.position_update_job:
            self.root.after_cancel(self.position_update_job)
        
        if self.is_playing and PYGAME_AVAILABLE:
            # Check if song finished
            if not pygame.mixer.music.get_busy():
                self.on_song_finished()
            else:
                # Update position (approximate)
                self.current_position += 1
                self.update_progress_display()
        
        # Schedule next update
        self.position_update_job = self.root.after(1000, self.start_position_updates)
    
    def on_song_finished(self):
        """Handle song finished event."""
        if self.repeat_mode == "one":
            # Repeat current song
            self.play_song()
        else:
            # Play next song
            self.next_song()
    
    # Library methods
    def filter_library(self, *args):
        """Filter library based on search term."""
        self.update_library_display()
    
    def clear_library_search(self):
        """Clear library search."""
        self.library_search_var.set("")
    
    def sort_library(self, event=None):
        """Sort library by selected criteria."""
        self.update_library_display()
    
    def play_selected_library_song(self, event=None):
        """Play selected song from library."""
        selection = self.library_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a song to play")
            return
        
        # Get song path
        item = self.library_tree.item(selection[0])
        song_path = item['values'][4]  # Path is in column 4
        
        # Find song in library
        song = next((s for s in self.music_library if s['path'] == song_path), None)
        if song:
            # Clear playlist and add this song
            self.playlist = [song]
            self.current_playlist_index = 0
            self.update_playlist_display()
            self.play_song()
    
    def add_to_playlist_from_library(self):
        """Add selected library songs to playlist."""
        selection = self.library_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select songs to add to playlist")
            return
        
        added_count = 0
        for item_id in selection:
            item = self.library_tree.item(item_id)
            song_path = item['values'][4]  # Path is in column 4
            
            # Find song in library
            song = next((s for s in self.music_library if s['path'] == song_path), None)
            if song and song not in self.playlist:
                self.playlist.append(song)
                added_count += 1
        
        self.update_playlist_display()
        self.save_data()
        self.update_status(f"Added {added_count} songs to playlist")
    
    def add_to_favorites_from_library(self):
        """Add selected library songs to favorites."""
        selection = self.library_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select songs to add to favorites")
            return
        
        added_count = 0
        for item_id in selection:
            item = self.library_tree.item(item_id)
            song_path = item['values'][4]  # Path is in column 4
            
            # Find song in library
            song = next((s for s in self.music_library if s['path'] == song_path), None)
            if song and song not in self.favorites:
                self.favorites.append(song)
                added_count += 1
        
        self.update_favorites_display()
        self.save_data()
        self.update_status(f"Added {added_count} songs to favorites")
    
    def remove_from_library(self):
        """Remove selected songs from library."""
        selection = self.library_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select songs to remove")
            return
        
        if not messagebox.askyesno("Confirm", f"Remove {len(selection)} songs from library?"):
            return
        
        # Remove songs
        removed_count = 0
        for item_id in selection:
            item = self.library_tree.item(item_id)
            song_path = item['values'][4]  # Path is in column 4
            
            # Remove from library
            self.music_library = [s for s in self.music_library if s['path'] != song_path]
            removed_count += 1
        
        self.update_library_display()
        self.save_data()
        self.update_status(f"Removed {removed_count} songs from library")
    
    # Playlist methods
    def play_selected_playlist_song(self, event=None):
        """Play selected song from playlist."""
        selection = self.playlist_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a song to play")
            return
        
        # Get song index
        item = self.playlist_tree.item(selection[0])
        song_index = int(item['values'][0]) - 1  # Index is in column 0, subtract 1 for 0-based
        
        self.current_playlist_index = song_index
        self.play_song()
    
    def move_playlist_item_up(self):
        """Move selected playlist item up."""
        selection = self.playlist_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a song to move")
            return
        
        item = self.playlist_tree.item(selection[0])
        song_index = int(item['values'][0]) - 1
        
        if song_index > 0:
            # Swap with previous item
            self.playlist[song_index], self.playlist[song_index - 1] = \
                self.playlist[song_index - 1], self.playlist[song_index]
            
            # Update current index if needed
            if self.current_playlist_index == song_index:
                self.current_playlist_index -= 1
            elif self.current_playlist_index == song_index - 1:
                self.current_playlist_index += 1
            
            self.update_playlist_display()
            self.save_data()
    
    def move_playlist_item_down(self):
        """Move selected playlist item down."""
        selection = self.playlist_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a song to move")
            return
        
        item = self.playlist_tree.item(selection[0])
        song_index = int(item['values'][0]) - 1
        
        if song_index < len(self.playlist) - 1:
            # Swap with next item
            self.playlist[song_index], self.playlist[song_index + 1] = \
                self.playlist[song_index + 1], self.playlist[song_index]
            
            # Update current index if needed
            if self.current_playlist_index == song_index:
                self.current_playlist_index += 1
            elif self.current_playlist_index == song_index + 1:
                self.current_playlist_index -= 1
            
            self.update_playlist_display()
            self.save_data()
    
    def remove_from_playlist(self):
        """Remove selected songs from playlist."""
        selection = self.playlist_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select songs to remove")
            return
        
        # Get indices to remove (reverse order to avoid index issues)
        indices_to_remove = []
        for item_id in selection:
            item = self.playlist_tree.item(item_id)
            song_index = int(item['values'][0]) - 1
            indices_to_remove.append(song_index)
        
        indices_to_remove.sort(reverse=True)
        
        # Remove songs
        for index in indices_to_remove:
            if 0 <= index < len(self.playlist):
                del self.playlist[index]
                
                # Adjust current index
                if self.current_playlist_index > index:
                    self.current_playlist_index -= 1
                elif self.current_playlist_index == index:
                    if self.current_playlist_index >= len(self.playlist):
                        self.current_playlist_index = len(self.playlist) - 1
        
        self.update_playlist_display()
        self.save_data()
        self.update_status(f"Removed {len(selection)} songs from playlist")
    
    def shuffle_playlist(self):
        """Shuffle current playlist."""
        if self.playlist:
            # Remember current song
            current_song = None
            if 0 <= self.current_playlist_index < len(self.playlist):
                current_song = self.playlist[self.current_playlist_index]
            
            # Shuffle playlist
            random.shuffle(self.playlist)
            
            # Find new index of current song
            if current_song:
                try:
                    self.current_playlist_index = self.playlist.index(current_song)
                except ValueError:
                    self.current_playlist_index = 0
            
            self.update_playlist_display()
            self.save_data()
            self.update_status("Playlist shuffled")
    
    def clear_playlist(self):
        """Clear current playlist."""
        if messagebox.askyesno("Confirm", "Clear current playlist?"):
            self.stop_playback()
            self.playlist.clear()
            self.current_playlist_index = 0
            self.update_playlist_display()
            self.save_data()
            self.update_status("Playlist cleared")
    
    def save_playlist(self):
        """Save current playlist to file."""
        if not self.playlist:
            messagebox.showwarning("Warning", "No playlist to save")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save playlist",
            defaultextension=".m3u",
            filetypes=[("M3U playlists", "*.m3u"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.lower().endswith('.m3u'):
                    # Save as M3U playlist
                    with open(filename, 'w') as f:
                        f.write("#EXTM3U\n")
                        for song in self.playlist:
                            f.write(f"#EXTINF:{song.get('duration', 0)},{song.get('artist', '')} - {song.get('title', '')}\n")
                            f.write(f"{song['path']}\n")
                else:
                    # Save as JSON
                    with open(filename, 'w') as f:
                        json.dump(self.playlist, f, indent=2)
                
                self.update_status(f"Playlist saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save playlist: {e}")
    
    def load_playlist(self):
        """Load playlist from file."""
        filename = filedialog.askopenfilename(
            title="Load playlist",
            filetypes=[("M3U playlists", "*.m3u"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.lower().endswith('.m3u'):
                    # Load M3U playlist
                    self.load_m3u_playlist(filename)
                else:
                    # Load JSON playlist
                    with open(filename, 'r') as f:
                        loaded_playlist = json.load(f)
                        
                        # Validate and add songs
                        valid_songs = []
                        for song in loaded_playlist:
                            if isinstance(song, dict) and 'path' in song:
                                if os.path.exists(song['path']):
                                    valid_songs.append(song)
                        
                        if valid_songs:
                            self.playlist = valid_songs
                            self.current_playlist_index = 0
                            self.update_playlist_display()
                            self.save_data()
                            self.update_status(f"Loaded {len(valid_songs)} songs from playlist")
                        else:
                            messagebox.showwarning("Warning", "No valid songs found in playlist")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load playlist: {e}")
    
    def load_m3u_playlist(self, filename):
        """Load M3U playlist file."""
        songs = []
        
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_song = {}
        for line in lines:
            line = line.strip()
            
            if line.startswith('#EXTINF:'):
                # Parse metadata
                parts = line.split(',', 1)
                if len(parts) > 1:
                    title_artist = parts[1]
                    if ' - ' in title_artist:
                        artist, title = title_artist.split(' - ', 1)
                        current_song['artist'] = artist.strip()
                        current_song['title'] = title.strip()
                    else:
                        current_song['title'] = title_artist.strip()
            
            elif line and not line.startswith('#'):
                # File path
                if os.path.exists(line):
                    # Get metadata from file if not in playlist
                    if 'title' not in current_song:
                        metadata = self.get_metadata(line)
                        current_song.update(metadata)
                    
                    current_song['path'] = line
                    songs.append(current_song)
                
                current_song = {}
        
        if songs:
            self.playlist = songs
            self.current_playlist_index = 0
            self.update_playlist_display()
            self.save_data()
    
    # Radio methods
    def add_default_radio_stations(self):
        """Add some default radio stations."""
        if not self.radio_stations:
            default_stations = [
                {
                    "name": "Example Jazz Radio",
                    "url": "http://example.com/jazz.mp3",
                    "genre": "Jazz",
                    "bitrate": "128"
                },
                {
                    "name": "Example Rock Radio",
                    "url": "http://example.com/rock.mp3",
                    "genre": "Rock",
                    "bitrate": "192"
                }
            ]
            self.radio_stations.extend(default_stations)
            self.update_radio_display()
    
    def add_radio_station(self):
        """Add new radio station."""
        dialog = RadioStationDialog(self.root)
        result = dialog.result
        
        if result:
            name, url, genre, bitrate = result
            station = {
                "name": name,
                "url": url,
                "genre": genre,
                "bitrate": bitrate
            }
            self.radio_stations.append(station)
            self.update_radio_display()
            self.save_data()
            self.update_status(f"Added radio station: {name}")
    
    def edit_radio_station(self):
        """Edit selected radio station."""
        selection = self.radio_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a radio station to edit")
            return
        
        item = self.radio_tree.item(selection[0])
        station_name = item['values'][0]
        
        # Find station
        station = next((s for s in self.radio_stations if s['name'] == station_name), None)
        if station:
            dialog = RadioStationDialog(
                self.root,
                station['name'],
                station['url'],
                station['genre'],
                station['bitrate']
            )
            result = dialog.result
            
            if result:
                name, url, genre, bitrate = result
                station.update({
                    "name": name,
                    "url": url,
                    "genre": genre,
                    "bitrate": bitrate
                })
                self.update_radio_display()
                self.save_data()
                self.update_status(f"Updated radio station: {name}")
    
    def remove_radio_station(self):
        """Remove selected radio station."""
        selection = self.radio_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a radio station to remove")
            return
        
        item = self.radio_tree.item(selection[0])
        station_name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Remove radio station '{station_name}'?"):
            self.radio_stations = [s for s in self.radio_stations if s['name'] != station_name]
            self.update_radio_display()
            self.save_data()
            self.update_status(f"Removed radio station: {station_name}")
    
    def play_radio_station(self, event=None):
        """Play selected radio station."""
        selection = self.radio_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a radio station to play")
            return
        
        item = self.radio_tree.item(selection[0])
        station_name = item['values'][0]
        station_url = item['values'][1]
        
        # Note: This is a placeholder - pygame doesn't support streaming URLs directly
        messagebox.showinfo("Radio", f"Would play radio station: {station_name}\nURL: {station_url}")
        self.update_status(f"Playing radio: {station_name}")
    
    def stop_radio(self):
        """Stop radio playback."""
        self.stop_playback()
        self.update_status("Radio stopped")
    
    # Favorites methods
    def play_all_favorites(self):
        """Play all favorite songs."""
        if not self.favorites:
            messagebox.showwarning("Warning", "No favorite songs to play")
            return
        
        self.playlist = self.favorites.copy()
        self.current_playlist_index = 0
        self.update_playlist_display()
        self.play_song()
        self.update_status(f"Playing {len(self.favorites)} favorite songs")
    
    def add_favorites_to_playlist(self):
        """Add all favorites to current playlist."""
        if not self.favorites:
            messagebox.showwarning("Warning", "No favorite songs to add")
            return
        
        added_count = 0
        for song in self.favorites:
            if song not in self.playlist:
                self.playlist.append(song)
                added_count += 1
        
        self.update_playlist_display()
        self.save_data()
        self.update_status(f"Added {added_count} favorite songs to playlist")
    
    def clear_favorites(self):
        """Clear all favorites."""
        if messagebox.askyesno("Confirm", "Clear all favorite songs?"):
            self.favorites.clear()
            self.update_favorites_display()
            self.save_data()
            self.update_status("Favorites cleared")
    
    def play_selected_favorite(self, event=None):
        """Play selected favorite song."""
        selection = self.favorites_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a favorite song to play")
            return
        
        # Get song index
        item_index = self.favorites_tree.index(selection[0])
        if 0 <= item_index < len(self.favorites):
            song = self.favorites[item_index]
            self.playlist = [song]
            self.current_playlist_index = 0
            self.update_playlist_display()
            self.play_song()
    
    # Context menus
    def show_library_context_menu(self, event):
        """Show context menu for library."""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Play", command=self.play_selected_library_song)
        context_menu.add_command(label="Add to Playlist", command=self.add_to_playlist_from_library)
        context_menu.add_command(label="Add to Favorites", command=self.add_to_favorites_from_library)
        context_menu.add_separator()
        context_menu.add_command(label="Remove from Library", command=self.remove_from_library)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def show_playlist_context_menu(self, event):
        """Show context menu for playlist."""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Play", command=self.play_selected_playlist_song)
        context_menu.add_command(label="Move Up", command=self.move_playlist_item_up)
        context_menu.add_command(label="Move Down", command=self.move_playlist_item_down)
        context_menu.add_separator()
        context_menu.add_command(label="Remove from Playlist", command=self.remove_from_playlist)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def show_favorites_context_menu(self, event):
        """Show context menu for favorites."""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Play", command=self.play_selected_favorite)
        context_menu.add_command(label="Add to Playlist", command=lambda: self.add_selected_favorites_to_playlist())
        context_menu.add_separator()
        context_menu.add_command(label="Remove from Favorites", command=self.remove_selected_favorites)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def remove_selected_favorites(self):
        """Remove selected favorites."""
        selection = self.favorites_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select favorites to remove")
            return
        
        # Get indices to remove (reverse order)
        indices_to_remove = []
        for item_id in selection:
            index = self.favorites_tree.index(item_id)
            indices_to_remove.append(index)
        
        indices_to_remove.sort(reverse=True)
        
        # Remove favorites
        for index in indices_to_remove:
            if 0 <= index < len(self.favorites):
                del self.favorites[index]
        
        self.update_favorites_display()
        self.save_data()
        self.update_status(f"Removed {len(selection)} favorites")
    
    # Utility methods
    def scan_for_music(self):
        """Scan for music files in common directories."""
        common_dirs = [
            Path.home() / "Music",
            Path.home() / "Documents" / "Music",
            Path.home() / "Downloads"
        ]
        
        folder = filedialog.askdirectory(
            title="Select directory to scan for music",
            initialdir=str(common_dirs[0]) if common_dirs[0].exists() else str(Path.home())
        )
        
        if folder:
            self.add_folder()  # Reuse existing folder add functionality
    
    def show_equalizer(self):
        """Show equalizer dialog."""
        messagebox.showinfo("Equalizer", "Equalizer functionality would be implemented here")
    
    def show_sleep_timer(self):
        """Show sleep timer dialog."""
        messagebox.showinfo("Sleep Timer", "Sleep timer functionality would be implemented here")
    
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.root, self.settings)
        if dialog.result:
            self.settings.update(dialog.result)
            self.save_data()
            self.apply_theme()
    
    def apply_theme(self):
        """Apply current theme."""
        if self.settings.get("theme") == "dark":
            # Dark theme colors
            bg_color = "#2b2b2b"
            fg_color = "#ffffff"
            self.root.configure(bg=bg_color)
        else:
            # Light theme colors
            bg_color = "#ffffff"
            fg_color = "#000000"
            self.root.configure(bg=bg_color)
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        current_theme = self.settings.get("theme", "light")
        self.settings["theme"] = "dark" if current_theme == "light" else "light"
        self.apply_theme()
        self.save_data()
    
    def import_playlist(self):
        """Import playlist from file."""
        self.load_playlist()
    
    def export_playlist(self):
        """Export current playlist."""
        self.save_playlist()
    
    def update_status(self, message):
        """Update status bar."""
        self.status_label.config(text=message)
    
    def on_closing(self):
        """Handle application closing."""
        if self.position_update_job:
            self.root.after_cancel(self.position_update_job)
        
        self.stop_playback()
        self.save_data()
        
        if PYGAME_AVAILABLE:
            pygame.mixer.quit()
        
        self.root.destroy()
    
    def run(self):
        """Run the application."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initial display updates
        self.update_library_display()
        self.update_playlist_display()
        self.update_favorites_display()
        self.update_radio_display()
        
        self.root.mainloop()


class RadioStationDialog:
    """Dialog for adding/editing radio stations."""
    
    def __init__(self, parent, name="", url="", genre="", bitrate=""):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Radio Station" if not name else "Edit Radio Station")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Form fields
        form_frame = ttk.Frame(self.dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Name field
        ttk.Label(form_frame, text="Station Name:").pack(anchor=tk.W, pady=5)
        self.name_var = tk.StringVar(value=name)
        ttk.Entry(form_frame, textvariable=self.name_var, width=40).pack(fill=tk.X, pady=5)
        
        # URL field
        ttk.Label(form_frame, text="Stream URL:").pack(anchor=tk.W, pady=5)
        self.url_var = tk.StringVar(value=url)
        ttk.Entry(form_frame, textvariable=self.url_var, width=40).pack(fill=tk.X, pady=5)
        
        # Genre field
        ttk.Label(form_frame, text="Genre:").pack(anchor=tk.W, pady=5)
        self.genre_var = tk.StringVar(value=genre)
        genre_combo = ttk.Combobox(
            form_frame,
            textvariable=self.genre_var,
            values=["Pop", "Rock", "Jazz", "Classical", "Electronic", "Hip-Hop", "Country", "Other"],
            width=37
        )
        genre_combo.pack(fill=tk.X, pady=5)
        
        # Bitrate field
        ttk.Label(form_frame, text="Bitrate:").pack(anchor=tk.W, pady=5)
        self.bitrate_var = tk.StringVar(value=bitrate)
        bitrate_combo = ttk.Combobox(
            form_frame,
            textvariable=self.bitrate_var,
            values=["64", "128", "192", "256", "320"],
            width=37
        )
        bitrate_combo.pack(fill=tk.X, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.RIGHT, padx=5)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.dialog.wait_window()
    
    def ok_clicked(self):
        """Handle OK button click."""
        name = self.name_var.get().strip()
        url = self.url_var.get().strip()
        genre = self.genre_var.get().strip()
        bitrate = self.bitrate_var.get().strip()
        
        if not name or not url:
            messagebox.showerror("Error", "Please fill in name and URL fields")
            return
        
        self.result = (name, url, genre, bitrate)
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.dialog.destroy()


class SettingsDialog:
    """Settings dialog."""
    
    def __init__(self, parent, settings):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Settings form
        form_frame = ttk.Frame(self.dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Default volume
        volume_frame = ttk.Frame(form_frame)
        volume_frame.pack(fill=tk.X, pady=5)
        ttk.Label(volume_frame, text="Default volume:").pack(side=tk.LEFT)
        self.volume_var = tk.DoubleVar(value=settings.get("default_volume", 0.7) * 100)
        ttk.Scale(
            volume_frame,
            from_=0, to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            length=200
        ).pack(side=tk.RIGHT)
        
        # Crossfade
        self.crossfade_var = tk.BooleanVar(value=settings.get("auto_crossfade", False))
        ttk.Checkbutton(
            form_frame,
            text="Enable auto-crossfade",
            variable=self.crossfade_var
        ).pack(anchor=tk.W, pady=5)
        
        # Visualizations
        self.visualizations_var = tk.BooleanVar(value=settings.get("visualizations", True))
        ttk.Checkbutton(
            form_frame,
            text="Enable visualizations",
            variable=self.visualizations_var
        ).pack(anchor=tk.W, pady=5)
        
        # Theme
        theme_frame = ttk.Frame(form_frame)
        theme_frame.pack(fill=tk.X, pady=5)
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=settings.get("theme", "light"))
        ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=["light", "dark"],
            state="readonly",
            width=10
        ).pack(side=tk.RIGHT)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.RIGHT, padx=5)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self.dialog.wait_window()
    
    def ok_clicked(self):
        """Handle OK button click."""
        self.result = {
            "default_volume": self.volume_var.get() / 100.0,
            "auto_crossfade": self.crossfade_var.get(),
            "visualizations": self.visualizations_var.get(),
            "theme": self.theme_var.get()
        }
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.dialog.destroy()


def main():
    """Main function to run the music player."""
    if not PYGAME_AVAILABLE:
        print("Warning: pygame not available. Audio playback will be disabled.")
        print("Install with: pip install pygame")
    
    if not MUTAGEN_AVAILABLE:
        print("Warning: mutagen not available. Metadata reading will be limited.")
        print("Install with: pip install mutagen")
    
    app = MusicPlayer()
    app.run()


if __name__ == "__main__":
    main()
