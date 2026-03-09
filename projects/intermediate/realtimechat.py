import sqlite3
import bcrypt
import os
import json
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
import time
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect, send
from cryptography.fernet import Fernet
import logging
from werkzeug.utils import secure_filename
import uuid
import mimetypes
from pathlib import Path

class ChatSecurity:
    def __init__(self):
        """Initialize chat security with encryption."""
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self):
        """Get or create encryption key."""
        key_file = 'chat_encryption.key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def encrypt_message(self, message):
        """Encrypt a message."""
        try:
            encrypted = self.cipher.encrypt(message.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logging.error(f"Encryption error: {e}")
            return None
    
    def decrypt_message(self, encrypted_message):
        """Decrypt a message."""
        try:
            encrypted_bytes = base64.b64decode(encrypted_message.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logging.error(f"Decryption error: {e}")
            return encrypted_message
    
    def hash_password(self, password):
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    def verify_password(self, password, hashed):
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

class ChatDatabase:
    def __init__(self, db_path="realtime_chat.db"):
        """Initialize the chat database."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables for the chat application."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL,
                display_name TEXT NOT NULL,
                avatar_url TEXT,
                bio TEXT,
                status TEXT CHECK(status IN ('online', 'away', 'busy', 'offline')) DEFAULT 'offline',
                last_seen TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Chat rooms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                room_type TEXT CHECK(room_type IN ('public', 'private', 'direct')) DEFAULT 'public',
                created_by INTEGER NOT NULL,
                max_members INTEGER DEFAULT 100,
                is_active BOOLEAN DEFAULT 1,
                password_hash BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Room members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS room_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT CHECK(role IN ('admin', 'moderator', 'member')) DEFAULT 'member',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                UNIQUE(room_id, user_id),
                FOREIGN KEY (room_id) REFERENCES chat_rooms (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                message_type TEXT CHECK(message_type IN ('text', 'file', 'image', 'system')) DEFAULT 'text',
                file_url TEXT,
                file_name TEXT,
                file_size INTEGER,
                reply_to INTEGER,
                is_edited BOOLEAN DEFAULT 0,
                is_deleted BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES chat_rooms (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (reply_to) REFERENCES messages (id)
            )
        ''')
        
        # Message reactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS message_reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                emoji TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(message_id, user_id, emoji),
                FOREIGN KEY (message_id) REFERENCES messages (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                socket_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Private conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS private_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,
                room_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user1_id, user2_id),
                FOREIGN KEY (user1_id) REFERENCES users (id),
                FOREIGN KEY (user2_id) REFERENCES users (id),
                FOREIGN KEY (room_id) REFERENCES chat_rooms (id)
            )
        ''')
        
        # User blocked list
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocked_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blocker_id INTEGER NOT NULL,
                blocked_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(blocker_id, blocked_id),
                FOREIGN KEY (blocker_id) REFERENCES users (id),
                FOREIGN KEY (blocked_id) REFERENCES users (id)
            )
        ''')
        
        # File uploads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                mime_type TEXT NOT NULL,
                upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Create default rooms
        self._create_default_rooms()
    
    def _create_default_rooms(self):
        """Create default chat rooms."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if default rooms exist
        cursor.execute("SELECT COUNT(*) FROM chat_rooms WHERE name = 'General'")
        if cursor.fetchone()[0] == 0:
            # Create system user
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, email, password_hash, display_name, status)
                VALUES (?, ?, ?, ?, ?)
            ''', ('system', 'system@chat.local', b'', 'System', 'online'))
            
            system_user_id = cursor.lastrowid or 1
            
            # Create default rooms
            default_rooms = [
                ('General', 'General discussion for all users', 'public'),
                ('Random', 'Random conversations and off-topic discussions', 'public'),
                ('Help', 'Get help and support from the community', 'public')
            ]
            
            for name, description, room_type in default_rooms:
                cursor.execute('''
                    INSERT OR IGNORE INTO chat_rooms (name, description, room_type, created_by)
                    VALUES (?, ?, ?, ?)
                ''', (name, description, room_type, system_user_id))
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, email, password, display_name):
        """Create a new user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            security = ChatSecurity()
            password_hash = security.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, display_name)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, display_name))
            
            user_id = cursor.lastrowid
            
            # Join user to default public rooms
            cursor.execute('''
                INSERT INTO room_members (room_id, user_id)
                SELECT id, ? FROM chat_rooms WHERE room_type = 'public'
            ''', (user_id,))
            
            conn.commit()
            return user_id
            
        except sqlite3.IntegrityError as e:
            if 'username' in str(e):
                raise ValueError("Username already exists")
            elif 'email' in str(e):
                raise ValueError("Email already exists")
            else:
                raise ValueError("User creation failed")
        finally:
            conn.close()
    
    def authenticate_user(self, username, password):
        """Authenticate a user and return user info."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, password_hash, display_name, email, status, avatar_url
            FROM users 
            WHERE username = ? AND is_active = 1
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            security = ChatSecurity()
            if security.verify_password(password, user[1]):
                return {
                    'id': user[0],
                    'username': username,
                    'display_name': user[2],
                    'email': user[3],
                    'status': user[4],
                    'avatar_url': user[5]
                }
        
        return None
    
    def get_user_rooms(self, user_id):
        """Get all rooms for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cr.id, cr.name, cr.description, cr.room_type, rm.role
            FROM chat_rooms cr
            JOIN room_members rm ON cr.id = rm.room_id
            WHERE rm.user_id = ? AND rm.is_active = 1 AND cr.is_active = 1
            ORDER BY cr.name
        ''', (user_id,))
        
        rooms = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': room[0],
                'name': room[1],
                'description': room[2],
                'type': room[3],
                'role': room[4]
            }
            for room in rooms
        ]
    
    def get_room_messages(self, room_id, limit=50):
        """Get messages for a room."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.id, m.content, m.message_type, m.file_url, m.file_name,
                   m.created_at, u.username, u.display_name, u.avatar_url,
                   m.reply_to, m.is_edited
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.room_id = ? AND m.is_deleted = 0
            ORDER BY m.created_at DESC
            LIMIT ?
        ''', (room_id, limit))
        
        messages = cursor.fetchall()
        
        # Get reactions for messages
        message_ids = [str(msg[0]) for msg in messages]
        if message_ids:
            cursor.execute(f'''
                SELECT mr.message_id, mr.emoji, COUNT(*) as count,
                       GROUP_CONCAT(u.username) as users
                FROM message_reactions mr
                JOIN users u ON mr.user_id = u.id
                WHERE mr.message_id IN ({','.join(['?'] * len(message_ids))})
                GROUP BY mr.message_id, mr.emoji
            ''', message_ids)
            
            reactions_data = cursor.fetchall()
            reactions = {}
            for reaction in reactions_data:
                msg_id = reaction[0]
                if msg_id not in reactions:
                    reactions[msg_id] = []
                reactions[msg_id].append({
                    'emoji': reaction[1],
                    'count': reaction[2],
                    'users': reaction[3].split(',') if reaction[3] else []
                })
        else:
            reactions = {}
        
        conn.close()
        
        # Format messages
        formatted_messages = []
        for msg in reversed(messages):  # Reverse to show oldest first
            formatted_messages.append({
                'id': msg[0],
                'content': msg[1],
                'type': msg[2],
                'file_url': msg[3],
                'file_name': msg[4],
                'timestamp': msg[5],
                'username': msg[6],
                'display_name': msg[7],
                'avatar_url': msg[8],
                'reply_to': msg[9],
                'is_edited': msg[10],
                'reactions': reactions.get(msg[0], [])
            })
        
        return formatted_messages
    
    def save_message(self, room_id, user_id, content, message_type='text', file_url=None, file_name=None, file_size=None):
        """Save a message to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Encrypt message content if it's text
        if message_type == 'text':
            security = ChatSecurity()
            encrypted_content = security.encrypt_message(content)
            if encrypted_content:
                content = encrypted_content
        
        cursor.execute('''
            INSERT INTO messages (room_id, user_id, content, message_type, file_url, file_name, file_size)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (room_id, user_id, content, message_type, file_url, file_name, file_size))
        
        message_id = cursor.lastrowid
        
        # Get the message with user info
        cursor.execute('''
            SELECT m.id, m.content, m.message_type, m.file_url, m.file_name,
                   m.created_at, u.username, u.display_name, u.avatar_url
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.id = ?
        ''', (message_id,))
        
        message = cursor.fetchone()
        conn.commit()
        conn.close()
        
        if message:
            # Decrypt content for display if it's text
            display_content = message[1]
            if message[2] == 'text':
                security = ChatSecurity()
                display_content = security.decrypt_message(message[1])
            
            return {
                'id': message[0],
                'content': display_content,
                'type': message[2],
                'file_url': message[3],
                'file_name': message[4],
                'timestamp': message[5],
                'username': message[6],
                'display_name': message[7],
                'avatar_url': message[8],
                'reactions': []
            }
        
        return None

class FileManager:
    def __init__(self, upload_folder='uploads'):
        """Initialize file manager."""
        self.upload_folder = upload_folder
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {
            'images': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
            'documents': {'pdf', 'doc', 'docx', 'txt', 'rtf'},
            'archives': {'zip', 'rar', '7z', 'tar', 'gz'}
        }
        
        # Create upload directory
        Path(self.upload_folder).mkdir(exist_ok=True)
    
    def is_allowed_file(self, filename):
        """Check if file type is allowed."""
        if '.' not in filename:
            return False
        
        ext = filename.rsplit('.', 1)[1].lower()
        all_allowed = set()
        for exts in self.allowed_extensions.values():
            all_allowed.update(exts)
        
        return ext in all_allowed
    
    def save_file(self, file, user_id):
        """Save uploaded file."""
        if not file or not file.filename:
            return None
        
        if not self.is_allowed_file(file.filename):
            raise ValueError("File type not allowed")
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > self.max_file_size:
            raise ValueError(f"File too large. Maximum size is {self.max_file_size // (1024*1024)}MB")
        
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(self.upload_folder, unique_filename)
        
        try:
            file.save(file_path)
            
            # Save to database
            db = ChatDatabase()
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO file_uploads (user_id, original_filename, stored_filename, 
                                        file_path, file_size, mime_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, file.filename, unique_filename, file_path, 
                  file_size, mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'))
            
            conn.commit()
            conn.close()
            
            return {
                'filename': unique_filename,
                'original_name': file.filename,
                'size': file_size,
                'url': f'/uploads/{unique_filename}'
            }
            
        except Exception as e:
            # Clean up file if database save fails
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e

class RealtimeChatApp:
    def __init__(self):
        """Initialize the real-time chat application."""
        self.app = Flask(__name__)
        self.app.secret_key = secrets.token_hex(32)
        self.app.config['UPLOAD_FOLDER'] = 'uploads'
        self.app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB
        
        # Initialize SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize components
        self.db = ChatDatabase()
        self.security = ChatSecurity()
        self.file_manager = FileManager()
        
        # Track active users
        self.active_users = {}
        self.user_rooms = {}
        
        # Setup routes and events
        self.setup_routes()
        self.setup_socket_events()
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return render_template('chat.html')
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
                
                user = self.db.authenticate_user(username, password)
                if user:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['display_name'] = user['display_name']
                    return jsonify({'success': True, 'user': user})
                else:
                    return jsonify({'success': False, 'error': 'Invalid credentials'})
            
            return render_template('login.html')
        
        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'POST':
                data = request.get_json()
                username = data.get('username')
                email = data.get('email')
                password = data.get('password')
                display_name = data.get('display_name')
                
                try:
                    user_id = self.db.create_user(username, email, password, display_name)
                    session['user_id'] = user_id
                    session['username'] = username
                    session['display_name'] = display_name
                    return jsonify({'success': True})
                except ValueError as e:
                    return jsonify({'success': False, 'error': str(e)})
            
            return render_template('register.html')
        
        @self.app.route('/logout')
        def logout():
            session.clear()
            return redirect(url_for('login'))
        
        @self.app.route('/api/rooms')
        def get_rooms():
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            rooms = self.db.get_user_rooms(session['user_id'])
            return jsonify(rooms)
        
        @self.app.route('/api/rooms/<int:room_id>/messages')
        def get_room_messages(room_id):
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            messages = self.db.get_room_messages(room_id)
            
            # Decrypt text messages for display
            for message in messages:
                if message['type'] == 'text':
                    message['content'] = self.security.decrypt_message(message['content'])
            
            return jsonify(messages)
        
        @self.app.route('/api/upload', methods=['POST'])
        def upload_file():
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            
            try:
                file_info = self.file_manager.save_file(file, session['user_id'])
                return jsonify(file_info)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                logging.error(f"File upload error: {e}")
                return jsonify({'error': 'Upload failed'}), 500
        
        @self.app.route('/uploads/<filename>')
        def uploaded_file(filename):
            return self.app.send_static_file(f'uploads/{filename}')
    
    def setup_socket_events(self):
        """Setup SocketIO events."""
        
        @self.socketio.on('connect')
        def handle_connect():
            if 'user_id' not in session:
                disconnect()
                return
            
            user_id = session['user_id']
            username = session['username']
            
            # Track active user
            self.active_users[request.sid] = {
                'user_id': user_id,
                'username': username,
                'display_name': session['display_name']
            }
            
            # Get user's rooms and join them
            rooms = self.db.get_user_rooms(user_id)
            self.user_rooms[request.sid] = []
            
            for room in rooms:
                room_name = f"room_{room['id']}"
                join_room(room_name)
                self.user_rooms[request.sid].append(room_name)
            
            # Notify other users
            emit('user_connected', {
                'username': username,
                'display_name': session['display_name']
            }, broadcast=True)
            
            logging.info(f"User {username} connected")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            if request.sid in self.active_users:
                user_info = self.active_users[request.sid]
                
                # Leave all rooms
                if request.sid in self.user_rooms:
                    for room in self.user_rooms[request.sid]:
                        leave_room(room)
                    del self.user_rooms[request.sid]
                
                # Notify other users
                emit('user_disconnected', {
                    'username': user_info['username'],
                    'display_name': user_info['display_name']
                }, broadcast=True)
                
                del self.active_users[request.sid]
                logging.info(f"User {user_info['username']} disconnected")
        
        @self.socketio.on('send_message')
        def handle_message(data):
            if 'user_id' not in session:
                return
            
            room_id = data.get('room_id')
            content = data.get('content')
            message_type = data.get('type', 'text')
            file_url = data.get('file_url')
            file_name = data.get('file_name')
            
            if not room_id or not content:
                return
            
            # Save message to database
            message = self.db.save_message(
                room_id=room_id,
                user_id=session['user_id'],
                content=content,
                message_type=message_type,
                file_url=file_url,
                file_name=file_name
            )
            
            if message:
                # Emit to all users in the room
                room_name = f"room_{room_id}"
                emit('new_message', message, room=room_name)
                
                logging.info(f"Message sent in room {room_id} by {session['username']}")
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            room_id = data.get('room_id')
            if room_id and 'user_id' in session:
                room_name = f"room_{room_id}"
                join_room(room_name)
                
                if request.sid in self.user_rooms:
                    if room_name not in self.user_rooms[request.sid]:
                        self.user_rooms[request.sid].append(room_name)
                
                emit('room_joined', {'room_id': room_id})
        
        @self.socketio.on('leave_room')
        def handle_leave_room(data):
            room_id = data.get('room_id')
            if room_id:
                room_name = f"room_{room_id}"
                leave_room(room_name)
                
                if request.sid in self.user_rooms:
                    if room_name in self.user_rooms[request.sid]:
                        self.user_rooms[request.sid].remove(room_name)
                
                emit('room_left', {'room_id': room_id})
        
        @self.socketio.on('typing_start')
        def handle_typing_start(data):
            room_id = data.get('room_id')
            if room_id and 'user_id' in session:
                room_name = f"room_{room_id}"
                emit('user_typing', {
                    'username': session['username'],
                    'display_name': session['display_name']
                }, room=room_name, include_self=False)
        
        @self.socketio.on('typing_stop')
        def handle_typing_stop(data):
            room_id = data.get('room_id')
            if room_id and 'user_id' in session:
                room_name = f"room_{room_id}"
                emit('user_stopped_typing', {
                    'username': session['username'],
                    'display_name': session['display_name']
                }, room=room_name, include_self=False)
        
        @self.socketio.on('add_reaction')
        def handle_add_reaction(data):
            message_id = data.get('message_id')
            emoji = data.get('emoji')
            
            if message_id and emoji and 'user_id' in session:
                # Add reaction to database
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO message_reactions (message_id, user_id, emoji)
                        VALUES (?, ?, ?)
                    ''', (message_id, session['user_id'], emoji))
                    
                    # Get updated reaction count
                    cursor.execute('''
                        SELECT COUNT(*) FROM message_reactions 
                        WHERE message_id = ? AND emoji = ?
                    ''', (message_id, emoji))
                    
                    count = cursor.fetchone()[0]
                    conn.commit()
                    
                    # Get room_id for the message to emit to correct room
                    cursor.execute('SELECT room_id FROM messages WHERE id = ?', (message_id,))
                    room_result = cursor.fetchone()
                    
                    if room_result:
                        room_name = f"room_{room_result[0]}"
                        emit('reaction_added', {
                            'message_id': message_id,
                            'emoji': emoji,
                            'count': count,
                            'username': session['username']
                        }, room=room_name)
                    
                except Exception as e:
                    logging.error(f"Error adding reaction: {e}")
                finally:
                    conn.close()
    
    def create_templates(self):
        """Create HTML templates for the chat application."""
        template_dir = 'templates'
        static_dir = 'static'
        os.makedirs(template_dir, exist_ok=True)
        os.makedirs(static_dir, exist_ok=True)
        
        # Main chat template
        chat_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Real-time Chat</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; height: 100vh; overflow: hidden; }
        .chat-container { height: 100vh; display: flex; }
        .sidebar { width: 300px; background: #fff; border-right: 1px solid #dee2e6; }
        .chat-area { flex: 1; display: flex; flex-direction: column; }
        .messages-container { flex: 1; overflow-y: auto; padding: 20px; background: #fff; }
        .message { margin-bottom: 15px; }
        .message-content { max-width: 70%; }
        .message.own { text-align: right; }
        .message.own .message-content { margin-left: auto; background: #007bff; color: white; }
        .message-bubble { padding: 10px 15px; border-radius: 18px; background: #e9ecef; display: inline-block; }
        .message-info { font-size: 0.8em; color: #6c757d; margin-bottom: 5px; }
        .input-area { padding: 20px; background: #fff; border-top: 1px solid #dee2e6; }
        .typing-indicator { font-style: italic; color: #6c757d; padding: 10px 20px; }
        .room-item { padding: 15px; cursor: pointer; border-bottom: 1px solid #f8f9fa; }
        .room-item:hover, .room-item.active { background: #e9ecef; }
        .file-upload { position: relative; overflow: hidden; display: inline-block; }
        .file-upload input[type=file] { position: absolute; left: -9999px; }
        .emoji-picker { display: none; position: absolute; bottom: 50px; right: 20px; 
                       background: white; border: 1px solid #ddd; border-radius: 8px; 
                       padding: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .emoji { cursor: pointer; padding: 5px; border-radius: 4px; }
        .emoji:hover { background: #f8f9fa; }
        .reaction { display: inline-block; margin: 2px; padding: 2px 6px; 
                   background: #f8f9fa; border-radius: 12px; font-size: 0.8em; cursor: pointer; }
        .reaction:hover { background: #e9ecef; }
    </style>
</head>
<body>
    <div class="chat-container">
        <!-- Sidebar -->
        <div class="sidebar">
            <div class="p-3 border-bottom">
                <h5><i class="fas fa-comments"></i> Chat Rooms</h5>
                <small class="text-muted">{{ session.display_name }}</small>
            </div>
            <div id="rooms-list">
                <!-- Rooms will be loaded here -->
            </div>
        </div>
        
        <!-- Chat Area -->
        <div class="chat-area">
            <div class="p-3 border-bottom bg-light">
                <h6 id="current-room-name">Select a room</h6>
                <div id="online-users" class="text-muted"></div>
            </div>
            
            <div class="messages-container" id="messages">
                <!-- Messages will appear here -->
            </div>
            
            <div id="typing-indicator" class="typing-indicator" style="display: none;"></div>
            
            <div class="input-area">
                <div class="row g-2">
                    <div class="col">
                        <input type="text" id="message-input" class="form-control" 
                               placeholder="Type a message..." maxlength="1000">
                    </div>
                    <div class="col-auto">
                        <div class="file-upload">
                            <button class="btn btn-outline-secondary" type="button">
                                <i class="fas fa-paperclip"></i>
                            </button>
                            <input type="file" id="file-input" accept="image/*,.pdf,.doc,.docx,.txt">
                        </div>
                    </div>
                    <div class="col-auto">
                        <button id="emoji-btn" class="btn btn-outline-secondary" type="button">
                            <i class="fas fa-smile"></i>
                        </button>
                    </div>
                    <div class="col-auto">
                        <button id="send-btn" class="btn btn-primary" type="button">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
                
                <div id="emoji-picker" class="emoji-picker">
                    <div>😀 😃 😄 😁 😆 😅 😂 🤣 😊 😇</div>
                    <div>🙂 🙃 😉 😌 😍 🥰 😘 😗 😙 😚</div>
                    <div>😋 😛 😝 😜 🤪 🤨 🧐 🤓 😎 🤩</div>
                    <div>👍 👎 👌 ✌️ 🤞 🤟 🤘 🤙 👈 👉</div>
                    <div>❤️ 🧡 💛 💚 💙 💜 🖤 🤍 🤎 💔</div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        const socket = io();
        let currentRoom = null;
        let typingTimer = null;
        let isTyping = false;
        
        // Initialize
        $(document).ready(function() {
            loadRooms();
            setupEventHandlers();
        });
        
        function loadRooms() {
            $.get('/api/rooms', function(rooms) {
                const roomsList = $('#rooms-list');
                roomsList.empty();
                
                rooms.forEach(room => {
                    const roomHtml = `
                        <div class="room-item" data-room-id="${room.id}">
                            <div class="fw-bold">${room.name}</div>
                            <small class="text-muted">${room.description || ''}</small>
                        </div>
                    `;
                    roomsList.append(roomHtml);
                });
                
                // Auto-select first room
                if (rooms.length > 0) {
                    selectRoom(rooms[0].id, rooms[0].name);
                }
            });
        }
        
        function selectRoom(roomId, roomName) {
            if (currentRoom) {
                socket.emit('leave_room', {room_id: currentRoom});
            }
            
            currentRoom = roomId;
            $('#current-room-name').text(roomName);
            $('.room-item').removeClass('active');
            $(`.room-item[data-room-id="${roomId}"]`).addClass('active');
            
            socket.emit('join_room', {room_id: roomId});
            loadMessages(roomId);
        }
        
        function loadMessages(roomId) {
            $.get(`/api/rooms/${roomId}/messages`, function(messages) {
                const messagesContainer = $('#messages');
                messagesContainer.empty();
                
                messages.forEach(message => {
                    displayMessage(message);
                });
                
                scrollToBottom();
            });
        }
        
        function displayMessage(message) {
            const isOwn = message.username === '{{ session.username }}';
            const messageClass = isOwn ? 'message own' : 'message';
            
            let content = '';
            if (message.type === 'text') {
                content = `<div class="message-bubble">${escapeHtml(message.content)}</div>`;
            } else if (message.type === 'file') {
                if (message.file_url.match(/\\.(jpg|jpeg|png|gif|webp)$/i)) {
                    content = `
                        <div class="message-bubble">
                            <img src="${message.file_url}" alt="${message.file_name}" 
                                 style="max-width: 300px; max-height: 300px; border-radius: 8px;">
                            <div class="mt-1"><small>${message.file_name}</small></div>
                        </div>
                    `;
                } else {
                    content = `
                        <div class="message-bubble">
                            <i class="fas fa-file"></i> 
                            <a href="${message.file_url}" target="_blank">${message.file_name}</a>
                        </div>
                    `;
                }
            }
            
            const reactions = message.reactions.map(r => 
                `<span class="reaction" data-emoji="${r.emoji}">${r.emoji} ${r.count}</span>`
            ).join('');
            
            const messageHtml = `
                <div class="${messageClass}" data-message-id="${message.id}">
                    <div class="message-content">
                        ${!isOwn ? `<div class="message-info">${message.display_name}</div>` : ''}
                        ${content}
                        <div class="reactions mt-1">${reactions}</div>
                        <div class="message-time text-muted" style="font-size: 0.7em;">
                            ${new Date(message.timestamp).toLocaleTimeString()}
                        </div>
                    </div>
                </div>
            `;
            
            $('#messages').append(messageHtml);
        }
        
        function sendMessage() {
            const input = $('#message-input');
            const content = input.val().trim();
            
            if (content && currentRoom) {
                socket.emit('send_message', {
                    room_id: currentRoom,
                    content: content,
                    type: 'text'
                });
                
                input.val('');
                stopTyping();
            }
        }
        
        function startTyping() {
            if (!isTyping && currentRoom) {
                isTyping = true;
                socket.emit('typing_start', {room_id: currentRoom});
            }
            
            clearTimeout(typingTimer);
            typingTimer = setTimeout(stopTyping, 3000);
        }
        
        function stopTyping() {
            if (isTyping && currentRoom) {
                isTyping = false;
                socket.emit('typing_stop', {room_id: currentRoom});
            }
            clearTimeout(typingTimer);
        }
        
        function scrollToBottom() {
            const container = $('#messages');
            container.scrollTop(container[0].scrollHeight);
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function setupEventHandlers() {
            // Room selection
            $(document).on('click', '.room-item', function() {
                const roomId = $(this).data('room-id');
                const roomName = $(this).find('.fw-bold').text();
                selectRoom(roomId, roomName);
            });
            
            // Message input
            $('#message-input').on('keypress', function(e) {
                if (e.which === 13) {
                    sendMessage();
                } else {
                    startTyping();
                }
            });
            
            $('#send-btn').click(sendMessage);
            
            // File upload
            $('#file-input').change(function(e) {
                const file = e.target.files[0];
                if (file && currentRoom) {
                    uploadFile(file);
                }
            });
            
            // Emoji picker
            $('#emoji-btn').click(function() {
                $('#emoji-picker').toggle();
            });
            
            $(document).on('click', '.emoji', function() {
                const emoji = $(this).text();
                const input = $('#message-input');
                input.val(input.val() + emoji);
                $('#emoji-picker').hide();
            });
            
            // Message reactions
            $(document).on('dblclick', '.message-bubble', function() {
                const messageId = $(this).closest('.message').data('message-id');
                addReaction(messageId, '❤️');
            });
        }
        
        function uploadFile(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            $.ajax({
                url: '/api/upload',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    socket.emit('send_message', {
                        room_id: currentRoom,
                        content: response.original_name,
                        type: 'file',
                        file_url: response.url,
                        file_name: response.original_name
                    });
                },
                error: function(xhr) {
                    alert('File upload failed: ' + xhr.responseJSON.error);
                }
            });
        }
        
        function addReaction(messageId, emoji) {
            socket.emit('add_reaction', {
                message_id: messageId,
                emoji: emoji
            });
        }
        
        // Socket event handlers
        socket.on('new_message', function(message) {
            displayMessage(message);
            scrollToBottom();
        });
        
        socket.on('user_typing', function(data) {
            $('#typing-indicator').text(`${data.display_name} is typing...`).show();
        });
        
        socket.on('user_stopped_typing', function(data) {
            $('#typing-indicator').hide();
        });
        
        socket.on('reaction_added', function(data) {
            const messageElement = $(`.message[data-message-id="${data.message_id}"]`);
            const reactionsContainer = messageElement.find('.reactions');
            const existingReaction = reactionsContainer.find(`[data-emoji="${data.emoji}"]`);
            
            if (existingReaction.length) {
                existingReaction.text(`${data.emoji} ${data.count}`);
            } else {
                reactionsContainer.append(`<span class="reaction" data-emoji="${data.emoji}">${data.emoji} ${data.count}</span>`);
            }
        });
        
        socket.on('user_connected', function(data) {
            console.log(`${data.display_name} joined the chat`);
        });
        
        socket.on('user_disconnected', function(data) {
            console.log(`${data.display_name} left the chat`);
        });
    </script>
</body>
</html>
        '''
        
        # Login template
        login_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; }
        .login-container { height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-card { max-width: 400px; width: 100%; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="card login-card shadow">
            <div class="card-body p-4">
                <h3 class="text-center mb-4"><i class="fas fa-comments"></i> Real-time Chat</h3>
                
                <form id="login-form">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100 mb-3">Login</button>
                </form>
                
                <div class="text-center">
                    <small>Don't have an account? <a href="/register">Register here</a></small>
                </div>
                
                <div id="error-message" class="alert alert-danger mt-3" style="display: none;"></div>
            </div>
        </div>
    </div>
    
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $('#login-form').on('submit', function(e) {
            e.preventDefault();
            
            const username = $('#username').val();
            const password = $('#password').val();
            
            $.ajax({
                url: '/login',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({username, password}),
                success: function(response) {
                    if (response.success) {
                        window.location.href = '/';
                    } else {
                        $('#error-message').text(response.error).show();
                    }
                },
                error: function() {
                    $('#error-message').text('Login failed. Please try again.').show();
                }
            });
        });
    </script>
</body>
</html>
        '''
        
        # Register template
        register_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Registration</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; }
        .register-container { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .register-card { max-width: 400px; width: 100%; }
    </style>
</head>
<body>
    <div class="register-container">
        <div class="card register-card shadow">
            <div class="card-body p-4">
                <h3 class="text-center mb-4"><i class="fas fa-user-plus"></i> Join Chat</h3>
                
                <form id="register-form">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" required>
                    </div>
                    <div class="mb-3">
                        <label for="display_name" class="form-label">Display Name</label>
                        <input type="text" class="form-control" id="display_name" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" required>
                    </div>
                    <div class="mb-3">
                        <label for="confirm_password" class="form-label">Confirm Password</label>
                        <input type="password" class="form-control" id="confirm_password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100 mb-3">Register</button>
                </form>
                
                <div class="text-center">
                    <small>Already have an account? <a href="/login">Login here</a></small>
                </div>
                
                <div id="error-message" class="alert alert-danger mt-3" style="display: none;"></div>
            </div>
        </div>
    </div>
    
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $('#register-form').on('submit', function(e) {
            e.preventDefault();
            
            const password = $('#password').val();
            const confirmPassword = $('#confirm_password').val();
            
            if (password !== confirmPassword) {
                $('#error-message').text('Passwords do not match').show();
                return;
            }
            
            const data = {
                username: $('#username').val(),
                email: $('#email').val(),
                display_name: $('#display_name').val(),
                password: password
            };
            
            $.ajax({
                url: '/register',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function(response) {
                    if (response.success) {
                        window.location.href = '/';
                    } else {
                        $('#error-message').text(response.error).show();
                    }
                },
                error: function() {
                    $('#error-message').text('Registration failed. Please try again.').show();
                }
            });
        });
    </script>
</body>
</html>
        '''
        
        # Save templates
        with open(os.path.join(template_dir, 'chat.html'), 'w') as f:
            f.write(chat_html)
        
        with open(os.path.join(template_dir, 'login.html'), 'w') as f:
            f.write(login_html)
        
        with open(os.path.join(template_dir, 'register.html'), 'w') as f:
            f.write(register_html)
    
    def run(self, host='localhost', port=5000, debug=True):
        """Run the chat application."""
        self.create_templates()
        
        print("💬 Real-time Chat Application")
        print("=" * 50)
        print(f"🚀 Starting chat server...")
        print(f"🌐 Access the application at: http://{host}:{port}")
        print("\n🔥 Chat Features:")
        print("   - Real-time messaging with WebSocket")
        print("   - User authentication and registration")
        print("   - Multiple chat rooms support")
        print("   - File sharing and image upload")
        print("   - Message reactions and emoji")
        print("   - Typing indicators")
        print("   - Message encryption")
        print("   - User status tracking")
        print(f"\n💡 Default Rooms: General, Random, Help")
        print(f"🔒 Security: Encrypted messages, secure authentication")
        
        self.socketio.run(self.app, host=host, port=port, debug=debug)

def main():
    """Main function to run the chat application."""
    print("💬 Real-time Chat Application")
    print("=" * 50)
    
    try:
        app = RealtimeChatApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Chat application stopped")
    except Exception as e:
        print(f"\n❌ Error starting chat application: {e}")
        logging.error(f"Application error: {e}")

if __name__ == "__main__":
    main()
