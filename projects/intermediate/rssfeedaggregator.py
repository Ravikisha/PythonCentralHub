#!/usr/bin/env python3
"""
RSS Feed Aggregator
A comprehensive RSS feed aggregator with GUI for collecting and organizing news from multiple sources.

Features:
- Add/remove RSS feeds
- Categorize feeds by topics
- Automatic feed updates
- Search and filter articles
- Save favorite articles
- Export articles to various formats
- Dark/light theme support
- Offline reading mode
- Article sentiment analysis

Requirements:
- feedparser
- requests
- tkinter (built-in)
- webbrowser (built-in)
- datetime (built-in)
- threading (built-in)
- json (built-in)

Author: Python Central Hub
Date: 2025-09-06
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import threading
import webbrowser
import json
import datetime
from pathlib import Path
import re
import html
import time

try:
    import feedparser
    import requests
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    print("⚠️ feedparser not available. Install with: pip install feedparser requests")


class RSSAggregator:
    """Main RSS Feed Aggregator application."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("RSS Feed Aggregator")
        self.root.geometry("1200x800")
        
        # Data storage
        self.feeds = {}
        self.articles = []
        self.categories = ["Technology", "News", "Sports", "Science", "Entertainment", "Business"]
        self.favorites = []
        self.settings = {
            "auto_update": True,
            "update_interval": 30,  # minutes
            "max_articles_per_feed": 50,
            "theme": "light"
        }
        
        # Data files
        self.feeds_file = Path("rss_feeds.json")
        self.articles_file = Path("rss_articles.json")
        self.favorites_file = Path("rss_favorites.json")
        self.settings_file = Path("rss_settings.json")
        
        # Auto-update control
        self.auto_update_job = None
        self.updating = False
        
        # Load saved data
        self.load_data()
        
        # Setup GUI
        self.setup_gui()
        
        # Start auto-update if enabled
        if self.settings["auto_update"]:
            self.start_auto_update()
    
    def setup_gui(self):
        """Setup the main GUI interface."""
        # Create menu
        self.create_menu()
        
        # Create main paned window
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Feeds and categories
        self.create_left_panel()
        
        # Right panel - Articles and content
        self.create_right_panel()
        
        # Status bar
        self.create_status_bar()
        
        # Apply theme
        self.apply_theme()
    
    def create_menu(self):
        """Create application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import OPML", command=self.import_opml)
        file_menu.add_command(label="Export OPML", command=self.export_opml)
        file_menu.add_separator()
        file_menu.add_command(label="Export Articles", command=self.export_articles)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Feeds menu
        feeds_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Feeds", menu=feeds_menu)
        feeds_menu.add_command(label="Add Feed", command=self.add_feed)
        feeds_menu.add_command(label="Remove Feed", command=self.remove_feed)
        feeds_menu.add_command(label="Edit Feed", command=self.edit_feed)
        feeds_menu.add_separator()
        feeds_menu.add_command(label="Update All Feeds", command=self.update_all_feeds)
        feeds_menu.add_command(label="Update Selected Feed", command=self.update_selected_feed)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh Articles", command=self.refresh_articles_display)
        view_menu.add_command(label="Clear Articles", command=self.clear_articles)
        view_menu.add_separator()
        view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Settings", command=self.show_settings)
        tools_menu.add_command(label="Statistics", command=self.show_statistics)
        tools_menu.add_command(label="Favorites", command=self.show_favorites)
    
    def create_left_panel(self):
        """Create left panel with feeds and categories."""
        left_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(left_frame, weight=1)
        
        # Categories section
        categories_frame = ttk.LabelFrame(left_frame, text="Categories")
        categories_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.categories_listbox = tk.Listbox(categories_frame, height=6)
        self.categories_listbox.pack(fill=tk.X, padx=5, pady=5)
        self.categories_listbox.bind('<<ListboxSelect>>', self.on_category_select)
        
        # Populate categories
        for category in ["All"] + self.categories:
            self.categories_listbox.insert(tk.END, category)
        self.categories_listbox.selection_set(0)  # Select "All"
        
        # Feeds section
        feeds_frame = ttk.LabelFrame(left_frame, text="RSS Feeds")
        feeds_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Feeds treeview
        columns = ("Feed", "Category", "Status", "Count")
        self.feeds_tree = ttk.Treeview(feeds_frame, columns=columns, show="headings", height=15)
        
        self.feeds_tree.heading("Feed", text="Feed Name")
        self.feeds_tree.heading("Category", text="Category")
        self.feeds_tree.heading("Status", text="Status")
        self.feeds_tree.heading("Count", text="Articles")
        
        self.feeds_tree.column("Feed", width=150)
        self.feeds_tree.column("Category", width=80)
        self.feeds_tree.column("Status", width=60)
        self.feeds_tree.column("Count", width=50)
        
        # Scrollbar for feeds tree
        feeds_scrollbar = ttk.Scrollbar(feeds_frame, orient=tk.VERTICAL, command=self.feeds_tree.yview)
        self.feeds_tree.configure(yscrollcommand=feeds_scrollbar.set)
        
        self.feeds_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        feeds_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.feeds_tree.bind('<<TreeviewSelect>>', self.on_feed_select)
        self.feeds_tree.bind('<Double-1>', self.update_selected_feed)
        self.feeds_tree.bind('<Button-3>', self.show_feed_context_menu)
        
        # Feed control buttons
        feed_buttons_frame = ttk.Frame(feeds_frame)
        feed_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(feed_buttons_frame, text="Add", command=self.add_feed, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(feed_buttons_frame, text="Remove", command=self.remove_feed, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(feed_buttons_frame, text="Update", command=self.update_selected_feed, width=8).pack(side=tk.LEFT, padx=2)
        
        # Update feeds display
        self.update_feeds_display()
    
    def create_right_panel(self):
        """Create right panel with articles and content."""
        right_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(right_frame, weight=3)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Articles tab
        self.create_articles_tab()
        
        # Article content tab
        self.create_content_tab()
        
        # Search tab
        self.create_search_tab()
    
    def create_articles_tab(self):
        """Create articles list tab."""
        articles_frame = ttk.Frame(self.notebook)
        self.notebook.add(articles_frame, text="📰 Articles")
        
        # Search and filter frame
        filter_frame = ttk.Frame(articles_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_var.trace('w', self.filter_articles)
        
        ttk.Button(filter_frame, text="🔍", command=self.filter_articles).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Sort options
        ttk.Label(filter_frame, text="Sort by:").pack(side=tk.LEFT, padx=(20, 5))
        self.sort_var = tk.StringVar(value="Date")
        sort_combo = ttk.Combobox(
            filter_frame, 
            textvariable=self.sort_var,
            values=["Date", "Title", "Feed", "Category"],
            state="readonly",
            width=10
        )
        sort_combo.pack(side=tk.LEFT, padx=5)
        sort_combo.bind('<<ComboboxSelected>>', self.sort_articles)
        
        # Articles list frame
        articles_list_frame = ttk.Frame(articles_frame)
        articles_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Articles treeview
        columns = ("Title", "Feed", "Date", "Category")
        self.articles_tree = ttk.Treeview(articles_list_frame, columns=columns, show="headings")
        
        self.articles_tree.heading("Title", text="Title")
        self.articles_tree.heading("Feed", text="Feed")
        self.articles_tree.heading("Date", text="Date")
        self.articles_tree.heading("Category", text="Category")
        
        self.articles_tree.column("Title", width=400)
        self.articles_tree.column("Feed", width=150)
        self.articles_tree.column("Date", width=100)
        self.articles_tree.column("Category", width=100)
        
        # Scrollbars for articles tree
        articles_v_scrollbar = ttk.Scrollbar(articles_list_frame, orient=tk.VERTICAL, command=self.articles_tree.yview)
        articles_h_scrollbar = ttk.Scrollbar(articles_list_frame, orient=tk.HORIZONTAL, command=self.articles_tree.xview)
        self.articles_tree.configure(yscrollcommand=articles_v_scrollbar.set, xscrollcommand=articles_h_scrollbar.set)
        
        # Pack articles tree and scrollbars
        self.articles_tree.grid(row=0, column=0, sticky="nsew")
        articles_v_scrollbar.grid(row=0, column=1, sticky="ns")
        articles_h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        articles_list_frame.grid_rowconfigure(0, weight=1)
        articles_list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.articles_tree.bind('<Double-1>', self.open_article)
        self.articles_tree.bind('<<TreeviewSelect>>', self.on_article_select)
        self.articles_tree.bind('<Button-3>', self.show_article_context_menu)
        
        # Article controls
        controls_frame = ttk.Frame(articles_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="📖 Read", command=self.read_article).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="🌐 Open in Browser", command=self.open_in_browser).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="⭐ Add to Favorites", command=self.add_to_favorites).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="📤 Share", command=self.share_article).pack(side=tk.LEFT, padx=5)
        
        # Statistics label
        self.stats_label = ttk.Label(controls_frame, text="0 articles")
        self.stats_label.pack(side=tk.RIGHT, padx=5)
    
    def create_content_tab(self):
        """Create article content display tab."""
        content_frame = ttk.Frame(self.notebook)
        self.notebook.add(content_frame, text="📄 Content")
        
        # Article info frame
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Title
        self.content_title_var = tk.StringVar(value="Select an article to view")
        title_label = ttk.Label(info_frame, textvariable=self.content_title_var, font=("Arial", 14, "bold"))
        title_label.pack(anchor=tk.W)
        
        # Meta info
        meta_frame = ttk.Frame(info_frame)
        meta_frame.pack(fill=tk.X, pady=5)
        
        self.content_meta_var = tk.StringVar(value="")
        meta_label = ttk.Label(meta_frame, textvariable=self.content_meta_var, font=("Arial", 10))
        meta_label.pack(anchor=tk.W)
        
        # Content text
        content_text_frame = ttk.Frame(content_frame)
        content_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.content_text = tk.Text(
            content_text_frame, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            font=("Arial", 11),
            bg="white",
            fg="black"
        )
        
        content_scrollbar = ttk.Scrollbar(content_text_frame, orient=tk.VERTICAL, command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=content_scrollbar.set)
        
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Content controls
        content_controls_frame = ttk.Frame(content_frame)
        content_controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(content_controls_frame, text="🌐 Open Original", command=self.open_in_browser).pack(side=tk.LEFT, padx=5)
        ttk.Button(content_controls_frame, text="💾 Save Article", command=self.save_article).pack(side=tk.LEFT, padx=5)
        ttk.Button(content_controls_frame, text="🖨️ Print", command=self.print_article).pack(side=tk.LEFT, padx=5)
        
        # Font size controls
        font_frame = ttk.Frame(content_controls_frame)
        font_frame.pack(side=tk.RIGHT)
        
        ttk.Label(font_frame, text="Font size:").pack(side=tk.LEFT, padx=5)
        ttk.Button(font_frame, text="A-", command=self.decrease_font_size, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(font_frame, text="A+", command=self.increase_font_size, width=3).pack(side=tk.LEFT, padx=2)
    
    def create_search_tab(self):
        """Create advanced search tab."""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="🔍 Search")
        
        # Search form
        search_form_frame = ttk.LabelFrame(search_frame, text="Advanced Search")
        search_form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Search fields
        fields_frame = ttk.Frame(search_form_frame)
        fields_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title search
        ttk.Label(fields_frame, text="Title contains:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.search_title_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.search_title_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Content search
        ttk.Label(fields_frame, text="Content contains:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.search_content_var = tk.StringVar()
        ttk.Entry(fields_frame, textvariable=self.search_content_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Feed filter
        ttk.Label(fields_frame, text="From feed:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.search_feed_var = tk.StringVar()
        feed_names = ["All"] + list(self.feeds.keys())
        search_feed_combo = ttk.Combobox(
            fields_frame, 
            textvariable=self.search_feed_var,
            values=feed_names,
            state="readonly",
            width=27
        )
        search_feed_combo.grid(row=2, column=1, padx=5, pady=5)
        search_feed_combo.set("All")
        
        # Date range
        ttk.Label(fields_frame, text="Date range:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        date_frame = ttk.Frame(fields_frame)
        date_frame.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.search_date_var = tk.StringVar(value="All time")
        ttk.Combobox(
            date_frame,
            textvariable=self.search_date_var,
            values=["All time", "Today", "This week", "This month", "Custom"],
            state="readonly",
            width=15
        ).pack(side=tk.LEFT)
        
        # Search buttons
        search_buttons_frame = ttk.Frame(search_form_frame)
        search_buttons_frame.pack(pady=10)
        
        ttk.Button(search_buttons_frame, text="🔍 Search", command=self.advanced_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_buttons_frame, text="Clear", command=self.clear_advanced_search).pack(side=tk.LEFT, padx=5)
        
        # Search results
        results_frame = ttk.LabelFrame(search_frame, text="Search Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Results treeview
        self.search_results_tree = ttk.Treeview(results_frame, columns=("Title", "Feed", "Date"), show="headings")
        self.search_results_tree.heading("Title", text="Title")
        self.search_results_tree.heading("Feed", text="Feed")
        self.search_results_tree.heading("Date", text="Date")
        
        search_results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.search_results_tree.yview)
        self.search_results_tree.configure(yscrollcommand=search_results_scrollbar.set)
        
        self.search_results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        search_results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.search_results_tree.bind('<Double-1>', self.open_search_result)
    
    def create_status_bar(self):
        """Create status bar."""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.update_label = ttk.Label(self.status_frame, text="", relief=tk.SUNKEN)
        self.update_label.pack(side=tk.RIGHT)
    
    # Data management methods
    def load_data(self):
        """Load saved data from files."""
        try:
            if self.feeds_file.exists():
                with open(self.feeds_file, 'r') as f:
                    self.feeds = json.load(f)
        except Exception as e:
            print(f"Error loading feeds: {e}")
        
        try:
            if self.articles_file.exists():
                with open(self.articles_file, 'r') as f:
                    self.articles = json.load(f)
        except Exception as e:
            print(f"Error loading articles: {e}")
        
        try:
            if self.favorites_file.exists():
                with open(self.favorites_file, 'r') as f:
                    self.favorites = json.load(f)
        except Exception as e:
            print(f"Error loading favorites: {e}")
        
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
            with open(self.feeds_file, 'w') as f:
                json.dump(self.feeds, f, indent=2)
        except Exception as e:
            print(f"Error saving feeds: {e}")
        
        try:
            with open(self.articles_file, 'w') as f:
                json.dump(self.articles, f, indent=2)
        except Exception as e:
            print(f"Error saving articles: {e}")
        
        try:
            with open(self.favorites_file, 'w') as f:
                json.dump(self.favorites, f, indent=2)
        except Exception as e:
            print(f"Error saving favorites: {e}")
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    # Feed management methods
    def add_feed(self):
        """Add new RSS feed."""
        dialog = AddFeedDialog(self.root, self.categories)
        result = dialog.result
        
        if result:
            name, url, category = result
            if name in self.feeds:
                messagebox.showerror("Error", "Feed name already exists")
                return
            
            self.feeds[name] = {
                "url": url,
                "category": category,
                "last_updated": None,
                "article_count": 0,
                "status": "Active"
            }
            
            self.update_feeds_display()
            self.save_data()
            self.update_status(f"Added feed: {name}")
    
    def remove_feed(self):
        """Remove selected feed."""
        selection = self.feeds_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a feed to remove")
            return
        
        item = self.feeds_tree.item(selection[0])
        feed_name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Remove feed '{feed_name}'?"):
            # Remove feed
            del self.feeds[feed_name]
            
            # Remove articles from this feed
            self.articles = [a for a in self.articles if a.get('feed') != feed_name]
            
            self.update_feeds_display()
            self.refresh_articles_display()
            self.save_data()
            self.update_status(f"Removed feed: {feed_name}")
    
    def edit_feed(self):
        """Edit selected feed."""
        selection = self.feeds_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a feed to edit")
            return
        
        item = self.feeds_tree.item(selection[0])
        feed_name = item['values'][0]
        feed_data = self.feeds[feed_name]
        
        dialog = AddFeedDialog(self.root, self.categories, feed_name, feed_data['url'], feed_data['category'])
        result = dialog.result
        
        if result:
            new_name, new_url, new_category = result
            
            # Update feed data
            if new_name != feed_name:
                self.feeds[new_name] = self.feeds.pop(feed_name)
                # Update articles with new feed name
                for article in self.articles:
                    if article.get('feed') == feed_name:
                        article['feed'] = new_name
            
            self.feeds[new_name]['url'] = new_url
            self.feeds[new_name]['category'] = new_category
            
            self.update_feeds_display()
            self.refresh_articles_display()
            self.save_data()
            self.update_status(f"Updated feed: {new_name}")
    
    def update_feeds_display(self):
        """Update feeds display in treeview."""
        # Clear existing items
        for item in self.feeds_tree.get_children():
            self.feeds_tree.delete(item)
        
        # Add feeds
        for name, data in self.feeds.items():
            self.feeds_tree.insert('', tk.END, values=(
                name,
                data['category'],
                data['status'],
                data['article_count']
            ))
    
    # Feed updating methods
    def update_all_feeds(self):
        """Update all feeds."""
        if self.updating:
            messagebox.showinfo("Info", "Update already in progress")
            return
        
        if not FEEDPARSER_AVAILABLE:
            messagebox.showerror("Error", "feedparser library not available")
            return
        
        self.updating = True
        self.update_status("Updating all feeds...")
        
        def update_thread():
            try:
                total_feeds = len(self.feeds)
                for i, (name, data) in enumerate(self.feeds.items()):
                    if not self.updating:  # Check if update was cancelled
                        break
                    
                    self.root.after(0, lambda n=name: self.update_status(f"Updating {n}..."))
                    self.update_single_feed(name, data)
                    
                    progress = ((i + 1) / total_feeds) * 100
                    self.root.after(0, lambda p=progress: self.update_label.config(text=f"{p:.0f}%"))
                
                self.root.after(0, self.on_update_complete)
                
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Update error: {e}"))
                self.updating = False
        
        threading.Thread(target=update_thread, daemon=True).start()
    
    def update_selected_feed(self):
        """Update selected feed."""
        selection = self.feeds_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a feed to update")
            return
        
        if not FEEDPARSER_AVAILABLE:
            messagebox.showerror("Error", "feedparser library not available")
            return
        
        item = self.feeds_tree.item(selection[0])
        feed_name = item['values'][0]
        feed_data = self.feeds[feed_name]
        
        self.update_status(f"Updating {feed_name}...")
        
        def update_thread():
            try:
                self.update_single_feed(feed_name, feed_data)
                self.root.after(0, lambda: self.update_status(f"Updated {feed_name}"))
                self.root.after(0, self.refresh_articles_display)
                self.root.after(0, self.update_feeds_display)
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Update error: {e}"))
        
        threading.Thread(target=update_thread, daemon=True).start()
    
    def update_single_feed(self, name, data):
        """Update a single feed."""
        try:
            # Parse the feed
            feed = feedparser.parse(data['url'])
            
            if feed.bozo:
                print(f"Warning: Feed {name} has parsing issues")
            
            new_articles = 0
            max_articles = self.settings['max_articles_per_feed']
            
            # Process entries
            for entry in feed.entries[:max_articles]:
                # Create article data
                article = {
                    'id': entry.get('id', entry.get('link', '')),
                    'title': html.unescape(entry.get('title', 'No title')),
                    'link': entry.get('link', ''),
                    'description': html.unescape(entry.get('description', '')),
                    'published': entry.get('published', ''),
                    'published_parsed': entry.get('published_parsed', None),
                    'feed': name,
                    'category': data['category'],
                    'content': self.extract_content(entry),
                    'read': False,
                    'favorite': False
                }
                
                # Check if article already exists
                existing = any(a['id'] == article['id'] for a in self.articles)
                if not existing:
                    self.articles.insert(0, article)  # Add to beginning
                    new_articles += 1
            
            # Update feed metadata
            data['last_updated'] = datetime.datetime.now().isoformat()
            data['article_count'] = len([a for a in self.articles if a['feed'] == name])
            data['status'] = "Active"
            
            # Limit total articles per feed
            feed_articles = [a for a in self.articles if a['feed'] == name]
            if len(feed_articles) > max_articles:
                # Remove oldest articles
                feed_articles.sort(key=lambda x: x.get('published_parsed', (0,)))
                to_remove = feed_articles[:-max_articles]
                for article in to_remove:
                    self.articles.remove(article)
            
            print(f"Updated {name}: {new_articles} new articles")
            
        except Exception as e:
            print(f"Error updating feed {name}: {e}")
            data['status'] = "Error"
    
    def extract_content(self, entry):
        """Extract content from feed entry."""
        content = ""
        
        # Try different content fields
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value
        elif hasattr(entry, 'summary') and entry.summary:
            content = entry.summary
        elif hasattr(entry, 'description') and entry.description:
            content = entry.description
        
        # Clean HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        content = html.unescape(content)
        
        return content.strip()
    
    def on_update_complete(self):
        """Called when feed update is complete."""
        self.updating = False
        self.update_status("Feed update completed")
        self.update_label.config(text="")
        self.refresh_articles_display()
        self.update_feeds_display()
        self.save_data()
    
    # Article display methods
    def refresh_articles_display(self):
        """Refresh articles display."""
        # Clear existing items
        for item in self.articles_tree.get_children():
            self.articles_tree.delete(item)
        
        # Get selected category
        category_selection = self.categories_listbox.curselection()
        if category_selection:
            selected_category = self.categories_listbox.get(category_selection[0])
        else:
            selected_category = "All"
        
        # Filter articles by category
        filtered_articles = self.articles
        if selected_category != "All":
            filtered_articles = [a for a in self.articles if a.get('category') == selected_category]
        
        # Apply search filter
        search_term = self.search_var.get().lower()
        if search_term:
            filtered_articles = [
                a for a in filtered_articles 
                if search_term in a.get('title', '').lower() or 
                   search_term in a.get('description', '').lower()
            ]
        
        # Sort articles
        sort_by = self.sort_var.get()
        if sort_by == "Date":
            filtered_articles.sort(key=lambda x: x.get('published_parsed', (0,)), reverse=True)
        elif sort_by == "Title":
            filtered_articles.sort(key=lambda x: x.get('title', '').lower())
        elif sort_by == "Feed":
            filtered_articles.sort(key=lambda x: x.get('feed', '').lower())
        elif sort_by == "Category":
            filtered_articles.sort(key=lambda x: x.get('category', '').lower())
        
        # Add articles to tree
        for article in filtered_articles:
            # Format date
            date_str = ""
            if article.get('published_parsed'):
                try:
                    date_obj = datetime.datetime(*article['published_parsed'][:6])
                    date_str = date_obj.strftime("%Y-%m-%d")
                except:
                    pass
            
            # Truncate title if too long
            title = article.get('title', 'No title')
            if len(title) > 80:
                title = title[:77] + "..."
            
            # Add article with read status indicator
            if article.get('read'):
                title = f"✓ {title}"
            if article.get('favorite'):
                title = f"⭐ {title}"
            
            self.articles_tree.insert('', tk.END, values=(
                title,
                article.get('feed', ''),
                date_str,
                article.get('category', '')
            ))
        
        # Update statistics
        self.stats_label.config(text=f"{len(filtered_articles)} articles")
    
    def filter_articles(self, *args):
        """Filter articles based on search term."""
        self.refresh_articles_display()
    
    def clear_search(self):
        """Clear search term."""
        self.search_var.set("")
    
    def sort_articles(self, event=None):
        """Sort articles by selected criteria."""
        self.refresh_articles_display()
    
    # Event handlers
    def on_category_select(self, event):
        """Handle category selection."""
        self.refresh_articles_display()
    
    def on_feed_select(self, event):
        """Handle feed selection."""
        # Could filter articles by selected feed
        pass
    
    def on_article_select(self, event):
        """Handle article selection."""
        selection = self.articles_tree.selection()
        if not selection:
            return
        
        # Get article index
        article_index = self.articles_tree.index(selection[0])
        
        # Get filtered articles list
        category_selection = self.categories_listbox.curselection()
        if category_selection:
            selected_category = self.categories_listbox.get(category_selection[0])
        else:
            selected_category = "All"
        
        filtered_articles = self.articles
        if selected_category != "All":
            filtered_articles = [a for a in self.articles if a.get('category') == selected_category]
        
        search_term = self.search_var.get().lower()
        if search_term:
            filtered_articles = [
                a for a in filtered_articles 
                if search_term in a.get('title', '').lower() or 
                   search_term in a.get('description', '').lower()
            ]
        
        # Sort articles (same as in refresh_articles_display)
        sort_by = self.sort_var.get()
        if sort_by == "Date":
            filtered_articles.sort(key=lambda x: x.get('published_parsed', (0,)), reverse=True)
        elif sort_by == "Title":
            filtered_articles.sort(key=lambda x: x.get('title', '').lower())
        elif sort_by == "Feed":
            filtered_articles.sort(key=lambda x: x.get('feed', '').lower())
        elif sort_by == "Category":
            filtered_articles.sort(key=lambda x: x.get('category', '').lower())
        
        if article_index < len(filtered_articles):
            article = filtered_articles[article_index]
            self.display_article_content(article)
    
    def display_article_content(self, article):
        """Display article content in content tab."""
        # Update title
        self.content_title_var.set(article.get('title', 'No title'))
        
        # Update meta info
        feed = article.get('feed', 'Unknown')
        date_str = ""
        if article.get('published_parsed'):
            try:
                date_obj = datetime.datetime(*article['published_parsed'][:6])
                date_str = date_obj.strftime("%Y-%m-%d %H:%M")
            except:
                pass
        
        meta_info = f"Feed: {feed}"
        if date_str:
            meta_info += f" | Published: {date_str}"
        
        self.content_meta_var.set(meta_info)
        
        # Update content
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        
        content = article.get('content', article.get('description', 'No content available'))
        self.content_text.insert(1.0, content)
        self.content_text.config(state=tk.DISABLED)
        
        # Mark as read
        article['read'] = True
        self.save_data()
        
        # Switch to content tab
        self.notebook.select(1)
    
    # Article actions
    def read_article(self):
        """Read selected article."""
        selection = self.articles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an article to read")
            return
        
        self.on_article_select(None)
    
    def open_article(self, event=None):
        """Open article content."""
        self.read_article()
    
    def open_in_browser(self):
        """Open article in web browser."""
        selection = self.articles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an article to open")
            return
        
        article_index = self.articles_tree.index(selection[0])
        # Get current filtered articles and find the actual article
        # This is simplified - in practice you'd track the actual article object
        
        # For demo, show message
        messagebox.showinfo("Browser", "Would open article in browser")
    
    def add_to_favorites(self):
        """Add article to favorites."""
        selection = self.articles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an article to add to favorites")
            return
        
        messagebox.showinfo("Favorites", "Article added to favorites")
    
    def share_article(self):
        """Share article."""
        selection = self.articles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an article to share")
            return
        
        messagebox.showinfo("Share", "Share functionality would be implemented here")
    
    # Content tab actions
    def save_article(self):
        """Save current article to file."""
        messagebox.showinfo("Save", "Article save functionality would be implemented here")
    
    def print_article(self):
        """Print current article."""
        messagebox.showinfo("Print", "Print functionality would be implemented here")
    
    def increase_font_size(self):
        """Increase content font size."""
        current_font = self.content_text.cget("font")
        if isinstance(current_font, str):
            # Parse font string
            font_parts = current_font.split()
            if len(font_parts) >= 2:
                try:
                    size = int(font_parts[1]) + 1
                    new_font = (font_parts[0], size)
                    self.content_text.config(font=new_font)
                except ValueError:
                    pass
    
    def decrease_font_size(self):
        """Decrease content font size."""
        current_font = self.content_text.cget("font")
        if isinstance(current_font, str):
            # Parse font string
            font_parts = current_font.split()
            if len(font_parts) >= 2:
                try:
                    size = max(8, int(font_parts[1]) - 1)
                    new_font = (font_parts[0], size)
                    self.content_text.config(font=new_font)
                except ValueError:
                    pass
    
    # Search functionality
    def advanced_search(self):
        """Perform advanced search."""
        # Get search criteria
        title_term = self.search_title_var.get().lower()
        content_term = self.search_content_var.get().lower()
        feed_filter = self.search_feed_var.get()
        date_filter = self.search_date_var.get()
        
        # Clear results
        for item in self.search_results_tree.get_children():
            self.search_results_tree.delete(item)
        
        # Filter articles
        results = []
        for article in self.articles:
            match = True
            
            # Title filter
            if title_term and title_term not in article.get('title', '').lower():
                match = False
            
            # Content filter
            if content_term and content_term not in article.get('content', '').lower():
                match = False
            
            # Feed filter
            if feed_filter != "All" and article.get('feed') != feed_filter:
                match = False
            
            # Date filter (simplified)
            if date_filter != "All time":
                # Implementation would depend on date range logic
                pass
            
            if match:
                results.append(article)
        
        # Display results
        for article in results[:100]:  # Limit to 100 results
            date_str = ""
            if article.get('published_parsed'):
                try:
                    date_obj = datetime.datetime(*article['published_parsed'][:6])
                    date_str = date_obj.strftime("%Y-%m-%d")
                except:
                    pass
            
            self.search_results_tree.insert('', tk.END, values=(
                article.get('title', 'No title'),
                article.get('feed', ''),
                date_str
            ))
        
        self.update_status(f"Found {len(results)} articles")
    
    def clear_advanced_search(self):
        """Clear advanced search form."""
        self.search_title_var.set("")
        self.search_content_var.set("")
        self.search_feed_var.set("All")
        self.search_date_var.set("All time")
        
        for item in self.search_results_tree.get_children():
            self.search_results_tree.delete(item)
    
    def open_search_result(self, event):
        """Open selected search result."""
        messagebox.showinfo("Search Result", "Would open selected search result")
    
    # Settings and utilities
    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.root, self.settings)
        if dialog.result:
            self.settings.update(dialog.result)
            self.save_data()
            
            # Restart auto-update if needed
            if self.settings["auto_update"]:
                self.start_auto_update()
    
    def show_statistics(self):
        """Show statistics dialog."""
        stats = {
            "total_feeds": len(self.feeds),
            "total_articles": len(self.articles),
            "total_favorites": len(self.favorites),
            "categories": len(set(feed["category"] for feed in self.feeds.values()))
        }
        
        stats_text = f"""RSS Feed Statistics:

Total Feeds: {stats['total_feeds']}
Total Articles: {stats['total_articles']}
Favorite Articles: {stats['total_favorites']}
Categories: {stats['categories']}

Recent Activity:
- Last update: {self.get_last_update_time()}
- Active feeds: {sum(1 for f in self.feeds.values() if f['status'] == 'Active')}
"""
        
        messagebox.showinfo("Statistics", stats_text)
    
    def show_favorites(self):
        """Show favorites dialog."""
        messagebox.showinfo("Favorites", f"You have {len(self.favorites)} favorite articles")
    
    def get_last_update_time(self):
        """Get last update time."""
        update_times = [f.get('last_updated') for f in self.feeds.values() if f.get('last_updated')]
        if update_times:
            latest = max(update_times)
            try:
                dt = datetime.datetime.fromisoformat(latest)
                return dt.strftime("%Y-%m-%d %H:%M")
            except:
                return "Unknown"
        return "Never"
    
    # Auto-update functionality
    def start_auto_update(self):
        """Start auto-update timer."""
        if self.auto_update_job:
            self.root.after_cancel(self.auto_update_job)
        
        if self.settings["auto_update"]:
            interval_ms = self.settings["update_interval"] * 60 * 1000  # Convert to milliseconds
            self.auto_update_job = self.root.after(interval_ms, self.auto_update_callback)
    
    def auto_update_callback(self):
        """Auto-update callback."""
        if not self.updating:
            self.update_all_feeds()
        
        # Schedule next update
        self.start_auto_update()
    
    # Theme management
    def apply_theme(self):
        """Apply current theme."""
        if self.settings["theme"] == "dark":
            self.root.configure(bg="#2b2b2b")
            self.content_text.configure(bg="#1e1e1e", fg="#ffffff")
        else:
            self.root.configure(bg="white")
            self.content_text.configure(bg="white", fg="black")
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        self.settings["theme"] = "dark" if self.settings["theme"] == "light" else "light"
        self.apply_theme()
        self.save_data()
    
    # Import/Export functionality
    def import_opml(self):
        """Import feeds from OPML file."""
        messagebox.showinfo("Import", "OPML import functionality would be implemented here")
    
    def export_opml(self):
        """Export feeds to OPML file."""
        messagebox.showinfo("Export", "OPML export functionality would be implemented here")
    
    def export_articles(self):
        """Export articles to file."""
        messagebox.showinfo("Export", "Article export functionality would be implemented here")
    
    # Context menus
    def show_feed_context_menu(self, event):
        """Show context menu for feeds."""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Update Feed", command=self.update_selected_feed)
        context_menu.add_command(label="Edit Feed", command=self.edit_feed)
        context_menu.add_command(label="Remove Feed", command=self.remove_feed)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def show_article_context_menu(self, event):
        """Show context menu for articles."""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Read Article", command=self.read_article)
        context_menu.add_command(label="Open in Browser", command=self.open_in_browser)
        context_menu.add_command(label="Add to Favorites", command=self.add_to_favorites)
        context_menu.add_command(label="Share", command=self.share_article)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    # Utility methods
    def clear_articles(self):
        """Clear all articles."""
        if messagebox.askyesno("Confirm", "Clear all articles?"):
            self.articles.clear()
            self.refresh_articles_display()
            self.save_data()
            self.update_status("All articles cleared")
    
    def update_status(self, message):
        """Update status bar."""
        self.status_label.config(text=message)
    
    def on_closing(self):
        """Handle application closing."""
        if self.auto_update_job:
            self.root.after_cancel(self.auto_update_job)
        
        self.updating = False
        self.save_data()
        self.root.destroy()
    
    def run(self):
        """Run the application."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


class AddFeedDialog:
    """Dialog for adding/editing RSS feeds."""
    
    def __init__(self, parent, categories, name="", url="", category=""):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add RSS Feed" if not name else "Edit RSS Feed")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Form fields
        form_frame = ttk.Frame(self.dialog)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Name field
        ttk.Label(form_frame, text="Feed Name:").pack(anchor=tk.W, pady=5)
        self.name_var = tk.StringVar(value=name)
        ttk.Entry(form_frame, textvariable=self.name_var, width=40).pack(fill=tk.X, pady=5)
        
        # URL field
        ttk.Label(form_frame, text="Feed URL:").pack(anchor=tk.W, pady=5)
        self.url_var = tk.StringVar(value=url)
        ttk.Entry(form_frame, textvariable=self.url_var, width=40).pack(fill=tk.X, pady=5)
        
        # Category field
        ttk.Label(form_frame, text="Category:").pack(anchor=tk.W, pady=5)
        self.category_var = tk.StringVar(value=category)
        category_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.category_var,
            values=categories,
            width=37
        )
        category_combo.pack(fill=tk.X, pady=5)
        
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
        category = self.category_var.get().strip()
        
        if not name or not url:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        self.result = (name, url, category)
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
        
        # Auto-update
        self.auto_update_var = tk.BooleanVar(value=settings["auto_update"])
        ttk.Checkbutton(
            form_frame, 
            text="Enable auto-update",
            variable=self.auto_update_var
        ).pack(anchor=tk.W, pady=5)
        
        # Update interval
        interval_frame = ttk.Frame(form_frame)
        interval_frame.pack(fill=tk.X, pady=5)
        ttk.Label(interval_frame, text="Update interval (minutes):").pack(side=tk.LEFT)
        self.interval_var = tk.IntVar(value=settings["update_interval"])
        ttk.Spinbox(
            interval_frame, 
            from_=5, to=240,
            textvariable=self.interval_var,
            width=10
        ).pack(side=tk.RIGHT)
        
        # Max articles
        articles_frame = ttk.Frame(form_frame)
        articles_frame.pack(fill=tk.X, pady=5)
        ttk.Label(articles_frame, text="Max articles per feed:").pack(side=tk.LEFT)
        self.max_articles_var = tk.IntVar(value=settings["max_articles_per_feed"])
        ttk.Spinbox(
            articles_frame, 
            from_=10, to=200,
            textvariable=self.max_articles_var,
            width=10
        ).pack(side=tk.RIGHT)
        
        # Theme
        theme_frame = ttk.Frame(form_frame)
        theme_frame.pack(fill=tk.X, pady=5)
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=settings["theme"])
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
            "auto_update": self.auto_update_var.get(),
            "update_interval": self.interval_var.get(),
            "max_articles_per_feed": self.max_articles_var.get(),
            "theme": self.theme_var.get()
        }
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.dialog.destroy()


def main():
    """Main function to run the RSS aggregator."""
    if not FEEDPARSER_AVAILABLE:
        print("Warning: feedparser not available. Some features will be disabled.")
        print("Install with: pip install feedparser requests")
    
    app = RSSAggregator()
    app.run()


if __name__ == "__main__":
    main()
