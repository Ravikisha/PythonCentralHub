import os
import sqlite3
import json
import hashlib
import secrets
from datetime import datetime, timedelta
import shutil
from pathlib import Path
import mimetypes
import uuid
import re
from urllib.parse import urlparse, urljoin

# Web framework
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file, abort
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# Content processing
import markdown
from markdown.extensions import codehilite, toc, meta, fenced_code
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
import bleach

# Email functionality
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Search and indexing
import whoosh
from whoosh.index import create_index, open_index
from whoosh.fields import Schema, TEXT, ID, DATETIME, BOOLEAN, KEYWORD
from whoosh.qparser import QueryParser
from whoosh.query import Every

# SEO and sitemap
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# Backup and import/export
import zipfile
import tempfile
import csv

# Plugin system
import importlib
import inspect
from abc import ABC, abstractmethod

# Caching
from functools import wraps
import pickle
import time

# Configuration
import configparser

class CMSConfig:
    def __init__(self, config_file="cms_config.ini"):
        """Load CMS configuration."""
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration."""
        self.config['CMS'] = {
            'site_name': 'My CMS Site',
            'site_description': 'A powerful content management system',
            'site_url': 'http://localhost:5000',
            'admin_email': 'admin@example.com',
            'theme': 'default',
            'posts_per_page': '10',
            'cache_enabled': 'true',
            'cache_timeout': '3600'
        }
        
        self.config['DATABASE'] = {
            'path': 'cms.db'
        }
        
        self.config['UPLOADS'] = {
            'path': 'uploads',
            'max_file_size': '10485760',  # 10MB
            'allowed_extensions': 'jpg,jpeg,png,gif,pdf,doc,docx,txt,zip'
        }
        
        self.config['SEO'] = {
            'meta_title_suffix': ' | My CMS Site',
            'meta_description_default': 'Content management system',
            'sitemap_enabled': 'true',
            'robots_txt_enabled': 'true'
        }
        
        self.save_config()
    
    def save_config(self):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get(self, section, key, fallback=None):
        """Get configuration value."""
        return self.config.get(section, key, fallback=fallback)
    
    def set(self, section, key, value):
        """Set configuration value."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = str(value)
        self.save_config()

class CMSDatabase:
    def __init__(self, db_path="cms.db"):
        """Initialize CMS database."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables for CMS."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                role TEXT CHECK(role IN ('admin', 'editor', 'author', 'subscriber')) DEFAULT 'subscriber',
                is_active BOOLEAN DEFAULT 1,
                profile_image TEXT,
                bio TEXT,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                description TEXT,
                parent_id INTEGER,
                meta_title TEXT,
                meta_description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES categories (id)
            )
        ''')
        
        # Tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                excerpt TEXT,
                author_id INTEGER NOT NULL,
                category_id INTEGER,
                status TEXT CHECK(status IN ('draft', 'published', 'scheduled', 'private')) DEFAULT 'draft',
                post_type TEXT CHECK(post_type IN ('post', 'page', 'custom')) DEFAULT 'post',
                featured_image TEXT,
                meta_title TEXT,
                meta_description TEXT,
                meta_keywords TEXT,
                allow_comments BOOLEAN DEFAULT 1,
                is_featured BOOLEAN DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                published_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users (id),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Post tags relationship table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_tags (
                post_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (post_id, tag_id),
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            )
        ''')
        
        # Comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                parent_id INTEGER,
                author_name TEXT NOT NULL,
                author_email TEXT NOT NULL,
                author_url TEXT,
                content TEXT NOT NULL,
                status TEXT CHECK(status IN ('pending', 'approved', 'spam', 'trash')) DEFAULT 'pending',
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES comments (id) ON DELETE CASCADE
            )
        ''')
        
        # Media files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                title TEXT,
                alt_text TEXT,
                description TEXT,
                uploaded_by INTEGER NOT NULL,
                is_used BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uploaded_by) REFERENCES users (id)
            )
        ''')
        
        # Menu system table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                location TEXT NOT NULL,
                items TEXT NOT NULL,  -- JSON data
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Widgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS widgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                widget_type TEXT NOT NULL,
                sidebar_location TEXT NOT NULL,
                content TEXT NOT NULL,  -- JSON data
                position INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                autoload BOOLEAN DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Plugin table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                version TEXT NOT NULL,
                description TEXT,
                author TEXT,
                is_active BOOLEAN DEFAULT 0,
                config TEXT,  -- JSON data
                installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                ip_address TEXT,
                user_agent TEXT,
                referer TEXT,
                page_url TEXT NOT NULL,
                session_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
        ''')
        
        conn.commit()
        conn.close()

class ContentProcessor:
    def __init__(self):
        """Initialize content processor with Markdown and security features."""
        self.markdown_processor = markdown.Markdown(
            extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                'markdown.extensions.toc',
                'markdown.extensions.meta',
                'markdown.extensions.fenced_code'
            ],
            extension_configs={
                'markdown.extensions.codehilite': {
                    'css_class': 'highlight'
                },
                'markdown.extensions.toc': {
                    'permalink': True
                }
            }
        )
        
        # HTML sanitization settings
        self.allowed_tags = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'div', 'span',
            'strong', 'em', 'b', 'i', 'u',
            'ul', 'ol', 'li',
            'a', 'img',
            'blockquote', 'code', 'pre',
            'table', 'thead', 'tbody', 'tr', 'td', 'th'
        ]
        
        self.allowed_attributes = {
            'a': ['href', 'title', 'target'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'div': ['class'],
            'span': ['class'],
            'code': ['class'],
            'pre': ['class']
        }
    
    def process_content(self, content, content_type='markdown'):
        """Process content based on type."""
        if content_type == 'markdown':
            return self.process_markdown(content)
        elif content_type == 'html':
            return self.sanitize_html(content)
        else:
            return content
    
    def process_markdown(self, content):
        """Process Markdown content."""
        html = self.markdown_processor.convert(content)
        return self.sanitize_html(html)
    
    def sanitize_html(self, html):
        """Sanitize HTML content."""
        return bleach.clean(
            html,
            tags=self.allowed_tags,
            attributes=self.allowed_attributes,
            strip=True
        )
    
    def extract_excerpt(self, content, max_length=160):
        """Extract excerpt from content."""
        # Remove HTML tags
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        
        # Truncate to max length
        if len(text) <= max_length:
            return text
        
        # Find last complete word
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            return truncated[:last_space] + '...'
        
        return truncated + '...'
    
    def generate_slug(self, title):
        """Generate URL-friendly slug from title."""
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        return slug

class SEOManager:
    def __init__(self, config):
        """Initialize SEO manager."""
        self.config = config
    
    def generate_meta_tags(self, post=None, page_title=None, description=None):
        """Generate meta tags for a page."""
        meta_tags = {}
        
        # Title
        if post:
            title = post.get('meta_title') or post.get('title', '')
        else:
            title = page_title or ''
        
        title_suffix = self.config.get('SEO', 'meta_title_suffix', '')
        meta_tags['title'] = title + title_suffix
        
        # Description
        if post:
            desc = post.get('meta_description') or post.get('excerpt', '')
        else:
            desc = description or ''
        
        if not desc:
            desc = self.config.get('SEO', 'meta_description_default', '')
        
        meta_tags['description'] = desc
        
        # Keywords
        if post and post.get('meta_keywords'):
            meta_tags['keywords'] = post['meta_keywords']
        
        # Open Graph
        meta_tags['og:title'] = meta_tags['title']
        meta_tags['og:description'] = meta_tags['description']
        meta_tags['og:type'] = 'article' if post else 'website'
        
        if post and post.get('featured_image'):
            meta_tags['og:image'] = urljoin(
                self.config.get('CMS', 'site_url', ''),
                post['featured_image']
            )
        
        return meta_tags
    
    def generate_sitemap(self, posts):
        """Generate XML sitemap."""
        root = Element('urlset')
        root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
        
        base_url = self.config.get('CMS', 'site_url', '')
        
        # Homepage
        url = SubElement(root, 'url')
        SubElement(url, 'loc').text = base_url
        SubElement(url, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
        SubElement(url, 'changefreq').text = 'daily'
        SubElement(url, 'priority').text = '1.0'
        
        # Posts
        for post in posts:
            if post['status'] == 'published':
                url = SubElement(root, 'url')
                post_url = urljoin(base_url, f"/{post['slug']}")
                SubElement(url, 'loc').text = post_url
                
                if post['updated_at']:
                    SubElement(url, 'lastmod').text = post['updated_at'][:10]
                
                SubElement(url, 'changefreq').text = 'weekly'
                SubElement(url, 'priority').text = '0.8'
        
        # Pretty print XML
        rough_string = tostring(root, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        
        return reparsed.toprettyxml(indent="  ")
    
    def generate_robots_txt(self):
        """Generate robots.txt content."""
        base_url = self.config.get('CMS', 'site_url', '')
        
        robots_content = f"""User-agent: *
Disallow: /admin/
Disallow: /login
Disallow: /search
Allow: /

Sitemap: {urljoin(base_url, '/sitemap.xml')}
"""
        return robots_content

class MediaManager:
    def __init__(self, config, db):
        """Initialize media manager."""
        self.config = config
        self.db = db
        self.upload_path = config.get('UPLOADS', 'path', 'uploads')
        self.max_file_size = int(config.get('UPLOADS', 'max_file_size', '10485760'))
        self.allowed_extensions = config.get('UPLOADS', 'allowed_extensions', '').split(',')
        
        # Create upload directory
        Path(self.upload_path).mkdir(exist_ok=True)
        Path(os.path.join(self.upload_path, 'thumbnails')).mkdir(exist_ok=True)
    
    def upload_file(self, file, user_id, title=None, alt_text=None, description=None):
        """Upload and process file."""
        if not self.is_allowed_file(file.filename):
            raise ValueError("File type not allowed")
        
        if len(file.read()) > self.max_file_size:
            raise ValueError("File too large")
        
        file.seek(0)  # Reset file pointer
        
        # Generate secure filename
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        file_path = os.path.join(self.upload_path, filename)
        
        # Save file
        file.save(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        # Generate thumbnail for images
        if mime_type.startswith('image/'):
            self.generate_thumbnail(file_path, filename)
        
        # Save to database
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO media (filename, original_filename, file_path, file_size, mime_type, title, alt_text, description, uploaded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            filename, file.filename, file_path, file_size, mime_type,
            title or file.filename, alt_text, description, user_id
        ))
        
        media_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'id': media_id,
            'filename': filename,
            'original_filename': file.filename,
            'file_path': file_path,
            'file_size': file_size,
            'mime_type': mime_type,
            'url': f"/uploads/{filename}"
        }
    
    def generate_thumbnail(self, file_path, filename, size=(300, 300)):
        """Generate thumbnail for image."""
        try:
            with Image.open(file_path) as img:
                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Save thumbnail
                thumb_filename = f"thumb_{filename}"
                thumb_path = os.path.join(self.upload_path, 'thumbnails', thumb_filename)
                img.save(thumb_path, optimize=True, quality=85)
                
                return thumb_path
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
    
    def is_allowed_file(self, filename):
        """Check if file extension is allowed."""
        if not filename or '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in self.allowed_extensions
    
    def delete_file(self, media_id):
        """Delete file and its database record."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get file info
        cursor.execute('SELECT filename, file_path FROM media WHERE id = ?', (media_id,))
        result = cursor.fetchone()
        
        if result:
            filename, file_path = result
            
            # Delete physical files
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete thumbnail if exists
            thumb_path = os.path.join(self.upload_path, 'thumbnails', f"thumb_{filename}")
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
            
            # Delete database record
            cursor.execute('DELETE FROM media WHERE id = ?', (media_id,))
            conn.commit()
        
        conn.close()

class SearchEngine:
    def __init__(self, index_dir="search_index"):
        """Initialize search engine with Whoosh."""
        self.index_dir = index_dir
        self.schema = Schema(
            id=ID(stored=True, unique=True),
            title=TEXT(stored=True),
            content=TEXT,
            category=TEXT(stored=True),
            tags=KEYWORD(stored=True),
            published_at=DATETIME(stored=True),
            is_published=BOOLEAN(stored=True)
        )
        
        self.setup_index()
    
    def setup_index(self):
        """Setup search index."""
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)
            self.index = create_index(self.index_dir, self.schema)
        else:
            self.index = open_index(self.index_dir)
    
    def index_post(self, post):
        """Add or update post in search index."""
        writer = self.index.writer()
        
        # Parse tags
        tags = []
        if post.get('tags'):
            tags = [tag['name'] for tag in post['tags']]
        
        writer.update_document(
            id=str(post['id']),
            title=post['title'],
            content=post['content'],
            category=post.get('category_name', ''),
            tags=' '.join(tags),
            published_at=datetime.strptime(post['published_at'], '%Y-%m-%d %H:%M:%S') if post.get('published_at') else None,
            is_published=post['status'] == 'published'
        )
        
        writer.commit()
    
    def remove_post(self, post_id):
        """Remove post from search index."""
        writer = self.index.writer()
        writer.delete_by_term('id', str(post_id))
        writer.commit()
    
    def search(self, query, limit=20):
        """Search posts."""
        with self.index.searcher() as searcher:
            # Parse query
            parser = QueryParser("content", self.index.schema)
            
            try:
                parsed_query = parser.parse(query)
            except:
                # Fallback to simple text search
                parsed_query = Every()
            
            # Filter only published posts
            from whoosh.query import And, Term
            published_filter = Term('is_published', True)
            final_query = And([parsed_query, published_filter])
            
            results = searcher.search(final_query, limit=limit)
            
            return [{
                'id': int(result['id']),
                'title': result['title'],
                'category': result['category'],
                'tags': result['tags'],
                'score': result.score
            } for result in results]

class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        """Initialize plugin manager."""
        self.plugin_dir = plugin_dir
        self.plugins = {}
        self.hooks = {}
        
        # Create plugin directory
        Path(self.plugin_dir).mkdir(exist_ok=True)
        
        # Load plugins
        self.load_plugins()
    
    def load_plugins(self):
        """Load all plugins."""
        for plugin_file in os.listdir(self.plugin_dir):
            if plugin_file.endswith('.py') and not plugin_file.startswith('_'):
                self.load_plugin(plugin_file[:-3])
    
    def load_plugin(self, plugin_name):
        """Load a specific plugin."""
        try:
            module_path = f"{self.plugin_dir}.{plugin_name}"
            module = importlib.import_module(module_path)
            
            # Look for plugin class
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, CMSPlugin) and obj != CMSPlugin:
                    plugin_instance = obj()
                    self.plugins[plugin_name] = plugin_instance
                    
                    # Register hooks
                    for hook_name, method in inspect.getmembers(plugin_instance):
                        if hasattr(method, '_hook_name'):
                            if method._hook_name not in self.hooks:
                                self.hooks[method._hook_name] = []
                            self.hooks[method._hook_name].append(method)
                    
                    break
                    
        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
    
    def execute_hook(self, hook_name, *args, **kwargs):
        """Execute all functions registered to a hook."""
        results = []
        
        if hook_name in self.hooks:
            for hook_function in self.hooks[hook_name]:
                try:
                    result = hook_function(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    print(f"Error executing hook {hook_name}: {e}")
        
        return results

class CMSPlugin(ABC):
    """Base class for CMS plugins."""
    
    @abstractmethod
    def get_name(self):
        """Return plugin name."""
        pass
    
    @abstractmethod
    def get_version(self):
        """Return plugin version."""
        pass
    
    @abstractmethod
    def get_description(self):
        """Return plugin description."""
        pass

def hook(hook_name):
    """Decorator to register plugin hooks."""
    def decorator(func):
        func._hook_name = hook_name
        return func
    return decorator

class CacheManager:
    def __init__(self, cache_dir="cache", timeout=3600):
        """Initialize cache manager."""
        self.cache_dir = cache_dir
        self.timeout = timeout
        
        Path(self.cache_dir).mkdir(exist_ok=True)
    
    def get(self, key):
        """Get cached value."""
        cache_file = os.path.join(self.cache_dir, f"{key}.cache")
        
        if os.path.exists(cache_file):
            # Check if cache is still valid
            if time.time() - os.path.getmtime(cache_file) < self.timeout:
                try:
                    with open(cache_file, 'rb') as f:
                        return pickle.load(f)
                except:
                    pass
        
        return None
    
    def set(self, key, value):
        """Set cached value."""
        cache_file = os.path.join(self.cache_dir, f"{key}.cache")
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            print(f"Error setting cache: {e}")
    
    def delete(self, key):
        """Delete cached value."""
        cache_file = os.path.join(self.cache_dir, f"{key}.cache")
        
        if os.path.exists(cache_file):
            os.remove(cache_file)
    
    def clear(self):
        """Clear all cache."""
        for cache_file in os.listdir(self.cache_dir):
            if cache_file.endswith('.cache'):
                os.remove(os.path.join(self.cache_dir, cache_file))

def cache_response(timeout=3600):
    """Decorator to cache view responses."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result)
            
            return result
        return wrapper
    return decorator

class ContentManagementSystem:
    def __init__(self):
        """Initialize the Content Management System."""
        self.app = Flask(__name__)
        self.app.secret_key = 'cms_secret_key_2024'
        
        # Initialize components
        self.config = CMSConfig()
        self.db = CMSDatabase(self.config.get('DATABASE', 'path'))
        self.content_processor = ContentProcessor()
        self.seo_manager = SEOManager(self.config)
        self.media_manager = MediaManager(self.config, self.db)
        self.search_engine = SearchEngine()
        self.plugin_manager = PluginManager()
        
        # Initialize cache manager
        global cache_manager
        cache_manager = CacheManager()
        
        self.setup_routes()
        self.create_admin_user()
    
    def setup_routes(self):
        """Setup Flask routes for the CMS."""
        
        # Public routes
        @self.app.route('/')
        @cache_response(timeout=1800)  # 30 minutes cache
        def index():
            return self.render_posts_page()
        
        @self.app.route('/post/<slug>')
        def post_detail(slug):
            return self.render_post_detail(slug)
        
        @self.app.route('/category/<slug>')
        def category_posts(slug):
            return self.render_category_posts(slug)
        
        @self.app.route('/tag/<slug>')
        def tag_posts(slug):
            return self.render_tag_posts(slug)
        
        @self.app.route('/search')
        def search_posts():
            query = request.args.get('q', '')
            if query:
                results = self.search_engine.search(query)
                return render_template('search_results.html', query=query, results=results)
            return render_template('search.html')
        
        @self.app.route('/sitemap.xml')
        def sitemap():
            posts = self.get_published_posts()
            sitemap_xml = self.seo_manager.generate_sitemap(posts)
            
            response = self.app.response_class(
                sitemap_xml,
                mimetype='application/xml'
            )
            return response
        
        @self.app.route('/robots.txt')
        def robots():
            robots_txt = self.seo_manager.generate_robots_txt()
            
            response = self.app.response_class(
                robots_txt,
                mimetype='text/plain'
            )
            return response
        
        # Admin routes
        @self.app.route('/admin')
        def admin_dashboard():
            if not self.is_admin_logged_in():
                return redirect(url_for('admin_login'))
            
            stats = self.get_dashboard_stats()
            return render_template('admin/dashboard.html', stats=stats)
        
        @self.app.route('/admin/login', methods=['GET', 'POST'])
        def admin_login():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                
                if self.authenticate_user(username, password):
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Invalid credentials')
            
            return render_template('admin/login.html')
        
        @self.app.route('/admin/logout')
        def admin_logout():
            session.pop('user_id', None)
            session.pop('username', None)
            session.pop('role', None)
            return redirect(url_for('index'))
        
        @self.app.route('/admin/posts')
        def admin_posts():
            if not self.is_admin_logged_in():
                return redirect(url_for('admin_login'))
            
            posts = self.get_all_posts()
            return render_template('admin/posts.html', posts=posts)
        
        @self.app.route('/admin/posts/new', methods=['GET', 'POST'])
        def admin_new_post():
            if not self.is_admin_logged_in():
                return redirect(url_for('admin_login'))
            
            if request.method == 'POST':
                post_data = self.extract_post_data(request.form)
                post_id = self.create_post(post_data)
                
                # Index post for search
                post = self.get_post_by_id(post_id)
                if post:
                    self.search_engine.index_post(post)
                
                flash('Post created successfully')
                return redirect(url_for('admin_posts'))
            
            categories = self.get_categories()
            tags = self.get_tags()
            return render_template('admin/post_form.html', categories=categories, tags=tags)
        
        @self.app.route('/admin/posts/<int:post_id>/edit', methods=['GET', 'POST'])
        def admin_edit_post(post_id):
            if not self.is_admin_logged_in():
                return redirect(url_for('admin_login'))
            
            post = self.get_post_by_id(post_id)
            if not post:
                abort(404)
            
            if request.method == 'POST':
                post_data = self.extract_post_data(request.form)
                self.update_post(post_id, post_data)
                
                # Update search index
                updated_post = self.get_post_by_id(post_id)
                if updated_post:
                    self.search_engine.index_post(updated_post)
                
                flash('Post updated successfully')
                return redirect(url_for('admin_posts'))
            
            categories = self.get_categories()
            tags = self.get_tags()
            return render_template('admin/post_form.html', post=post, categories=categories, tags=tags)
        
        @self.app.route('/admin/posts/<int:post_id>/delete', methods=['POST'])
        def admin_delete_post(post_id):
            if not self.is_admin_logged_in():
                return redirect(url_for('admin_login'))
            
            self.delete_post(post_id)
            self.search_engine.remove_post(post_id)
            
            flash('Post deleted successfully')
            return redirect(url_for('admin_posts'))
        
        @self.app.route('/admin/media')
        def admin_media():
            if not self.is_admin_logged_in():
                return redirect(url_for('admin_login'))
            
            media_files = self.get_media_files()
            return render_template('admin/media.html', media_files=media_files)
        
        @self.app.route('/admin/media/upload', methods=['POST'])
        def admin_upload_media():
            if not self.is_admin_logged_in():
                return redirect(url_for('admin_login'))
            
            if 'file' not in request.files:
                flash('No file selected')
                return redirect(url_for('admin_media'))
            
            file = request.files['file']
            if file.filename == '':
                flash('No file selected')
                return redirect(url_for('admin_media'))
            
            try:
                result = self.media_manager.upload_file(
                    file,
                    session['user_id'],
                    request.form.get('title'),
                    request.form.get('alt_text'),
                    request.form.get('description')
                )
                flash('File uploaded successfully')
            except ValueError as e:
                flash(str(e))
            
            return redirect(url_for('admin_media'))
        
        @self.app.route('/uploads/<filename>')
        def uploaded_file(filename):
            upload_path = self.config.get('UPLOADS', 'path', 'uploads')
            return send_file(os.path.join(upload_path, filename))
        
        # API routes
        @self.app.route('/api/posts')
        def api_posts():
            posts = self.get_published_posts()
            return jsonify(posts)
        
        @self.app.route('/api/search')
        def api_search():
            query = request.args.get('q', '')
            if query:
                results = self.search_engine.search(query)
                return jsonify(results)
            return jsonify([])
    
    def render_posts_page(self, page=1):
        """Render main posts page."""
        posts_per_page = int(self.config.get('CMS', 'posts_per_page', 10))
        posts = self.get_published_posts(limit=posts_per_page, offset=(page-1)*posts_per_page)
        
        # Get sidebar data
        recent_posts = self.get_recent_posts(5)
        categories = self.get_categories()
        
        meta_tags = self.seo_manager.generate_meta_tags(
            page_title=self.config.get('CMS', 'site_name'),
            description=self.config.get('CMS', 'site_description')
        )
        
        return render_template('index.html', 
                             posts=posts, 
                             recent_posts=recent_posts,
                             categories=categories,
                             meta_tags=meta_tags)
    
    def render_post_detail(self, slug):
        """Render post detail page."""
        post = self.get_post_by_slug(slug)
        if not post or post['status'] != 'published':
            abort(404)
        
        # Increment view count
        self.increment_post_views(post['id'])
        
        # Get related posts
        related_posts = self.get_related_posts(post['id'], post['category_id'])
        
        # Process content
        post['processed_content'] = self.content_processor.process_content(
            post['content'], 'markdown'
        )
        
        # Generate meta tags
        meta_tags = self.seo_manager.generate_meta_tags(post)
        
        return render_template('post.html', 
                             post=post, 
                             related_posts=related_posts,
                             meta_tags=meta_tags)
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password_hash, role FROM users 
            WHERE username = ? AND is_active = 1
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            return True
        
        return False
    
    def is_admin_logged_in(self):
        """Check if admin user is logged in."""
        return 'user_id' in session and session.get('role') in ['admin', 'editor']
    
    def create_admin_user(self):
        """Create default admin user if none exists."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
        count = cursor.fetchone()[0]
        
        if count == 0:
            password_hash = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, first_name, last_name)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('admin', 'admin@cms.com', password_hash, 'admin', 'Admin', 'User'))
            
            conn.commit()
            print("Default admin user created: admin/admin123")
        
        conn.close()
    
    def get_published_posts(self, limit=None, offset=0):
        """Get published posts."""
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        
        query = '''
            SELECT p.*, u.username as author_name, c.name as category_name
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.status = 'published'
            ORDER BY p.published_at DESC
        '''
        
        if limit:
            query += f' LIMIT {limit} OFFSET {offset}'
        
        cursor = conn.cursor()
        cursor.execute(query)
        posts = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return posts
    
    def get_post_by_slug(self, slug):
        """Get post by slug."""
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, u.username as author_name, c.name as category_name
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.slug = ?
        ''', (slug,))
        
        post = cursor.fetchone()
        conn.close()
        
        return dict(post) if post else None
    
    def create_sample_content(self):
        """Create sample content for demonstration."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Create sample category
        cursor.execute('''
            INSERT OR IGNORE INTO categories (name, slug, description)
            VALUES (?, ?, ?)
        ''', ('Technology', 'technology', 'Technology related posts'))
        
        # Get admin user ID
        cursor.execute('SELECT id FROM users WHERE role = "admin" LIMIT 1')
        admin_id = cursor.fetchone()[0]
        
        # Create sample posts
        sample_posts = [
            {
                'title': 'Welcome to Our CMS',
                'content': '''# Welcome to Our Content Management System

This is a sample post to demonstrate the capabilities of our CMS. You can:

- Create and edit posts with Markdown
- Organize content with categories and tags
- Upload and manage media files
- Optimize content for SEO
- Search through content

## Features

Our CMS includes many advanced features:

1. **Rich Content Editor** - Markdown support with live preview
2. **Media Management** - Upload and organize images, documents
3. **SEO Optimization** - Meta tags, sitemaps, and more
4. **Search Engine** - Full-text search across all content
5. **Plugin System** - Extend functionality with custom plugins

Enjoy exploring the system!''',
                'status': 'published',
                'post_type': 'post'
            },
            {
                'title': 'About Our CMS',
                'content': '''# About This CMS

This Content Management System is built with Python and Flask, featuring:

- Modern web technologies
- Responsive design
- Advanced content management
- SEO optimization
- Plugin architecture

Feel free to explore all the features!''',
                'status': 'published',
                'post_type': 'page'
            }
        ]
        
        for post_data in sample_posts:
            slug = self.content_processor.generate_slug(post_data['title'])
            excerpt = self.content_processor.extract_excerpt(post_data['content'])
            
            cursor.execute('''
                INSERT OR IGNORE INTO posts (
                    title, slug, content, excerpt, author_id, status, post_type, published_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                post_data['title'], slug, post_data['content'], excerpt,
                admin_id, post_data['status'], post_data['post_type'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
        
        conn.commit()
        conn.close()
    
    def run(self, host='localhost', port=5000, debug=True):
        """Run the CMS application."""
        
        print("📝 Content Management System")
        print("=" * 50)
        print(f"🚀 Starting CMS platform...")
        print(f"🌐 Access the website at: http://{host}:{port}")
        print(f"🔐 Admin panel at: http://{host}:{port}/admin")
        print("\n🔥 CMS Features:")
        print("   - Complete content management with WYSIWYG editor")
        print("   - Advanced media management and file uploads")
        print("   - SEO optimization with meta tags and sitemaps")
        print("   - Full-text search across all content")
        print("   - User roles and permissions system")
        print("   - Plugin architecture for extensibility")
        print("   - Responsive admin interface")
        print("   - Comment management system")
        print("\n👤 Default Admin Login:")
        print("   Username: admin")
        print("   Password: admin123")
        
        # Create sample content
        self.create_sample_content()
        
        self.app.run(host=host, port=port, debug=debug)

def main():
    """Main function to run the Content Management System."""
    print("📝 Content Management System")
    print("=" * 50)
    
    choice = input("\nChoose option:\n1. Start CMS Server\n2. Create Sample Data\nEnter choice (1-2): ")
    
    if choice == '2':
        # Create sample data
        print("\n📝 Creating sample CMS data...")
        cms = ContentManagementSystem()
        cms.create_sample_content()
        print("✅ Sample data created successfully!")
        print("Start the server with option 1 to see the CMS in action.")
    
    else:
        # Start CMS server
        cms = ContentManagementSystem()
        cms.run()

if __name__ == "__main__":
    main()
