import sqlite3
import datetime
import json
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading
import schedule
import time
from datetime import timedelta
import uuid
import bcrypt
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import smtplib
import pickle
import os
from textblob import TextBlob
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class AITaskManager:
    def __init__(self, db_path="ai_task_manager.db"):
        """Initialize the AI-powered task management system."""
        self.db_path = db_path
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.priority_model = LogisticRegression()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.model_trained = False
        
        self.init_database()
        self.train_ai_models()
        
    def init_database(self):
        """Create database tables for task management."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                timezone TEXT DEFAULT 'UTC',
                preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                owner_id INTEGER NOT NULL,
                status TEXT CHECK(status IN ('active', 'completed', 'archived')) DEFAULT 'active',
                priority INTEGER DEFAULT 3,
                deadline DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users (id)
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                project_id INTEGER,
                assigned_to INTEGER,
                created_by INTEGER NOT NULL,
                status TEXT CHECK(status IN ('todo', 'in_progress', 'review', 'done')) DEFAULT 'todo',
                priority INTEGER DEFAULT 3,
                ai_predicted_priority REAL,
                estimated_hours REAL,
                actual_hours REAL DEFAULT 0,
                due_date DATETIME,
                completed_at DATETIME,
                tags TEXT,
                dependencies TEXT,
                sentiment_score REAL,
                urgency_score REAL,
                complexity_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                FOREIGN KEY (assigned_to) REFERENCES users (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Time tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration REAL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT DEFAULT 'info',
                read BOOLEAN DEFAULT 0,
                related_task_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (related_task_id) REFERENCES tasks (id)
            )
        ''')
        
        # AI training data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_title TEXT NOT NULL,
                task_description TEXT,
                actual_priority INTEGER NOT NULL,
                completion_time REAL,
                user_feedback INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Create default admin user if none exists
        self.create_default_user()
    
    def create_default_user(self):
        """Create default admin user if database is empty."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name)
                VALUES (?, ?, ?, ?)
            ''', ("admin", "admin@taskmanager.com", password_hash, "Admin User"))
            conn.commit()
        
        conn.close()
    
    def create_user(self, username, email, password, full_name=""):
        """Create a new user account."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            conn.close()
            return None, "User already exists"
        
        # Hash password and create user
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, full_name))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return user_id, "User created successfully"
    
    def authenticate_user(self, username, password):
        """Authenticate user login."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, password_hash, full_name FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            return {"id": user[0], "username": username, "full_name": user[2]}
        
        return None
    
    def analyze_task_text(self, title, description=""):
        """Analyze task text for AI features."""
        full_text = f"{title} {description}".lower()
        
        # Sentiment analysis
        sentiment = self.sentiment_analyzer.polarity_scores(full_text)
        sentiment_score = sentiment['compound']
        
        # Urgency keywords
        urgency_keywords = [
            'urgent', 'asap', 'immediately', 'critical', 'emergency', 'deadline',
            'due today', 'overdue', 'high priority', 'important', 'rush'
        ]
        urgency_score = sum(1 for keyword in urgency_keywords if keyword in full_text)
        
        # Complexity indicators
        complexity_keywords = [
            'complex', 'difficult', 'research', 'analysis', 'design', 'architecture',
            'integration', 'optimization', 'algorithm', 'machine learning', 'database'
        ]
        complexity_score = sum(1 for keyword in complexity_keywords if keyword in full_text)
        
        # Extract time estimates from text
        time_pattern = r'(\d+)\s*(hour|hr|minute|min|day)'
        time_matches = re.findall(time_pattern, full_text)
        estimated_hours = 0
        
        for amount, unit in time_matches:
            if unit in ['hour', 'hr']:
                estimated_hours += int(amount)
            elif unit in ['minute', 'min']:
                estimated_hours += int(amount) / 60
            elif unit == 'day':
                estimated_hours += int(amount) * 8
        
        return {
            'sentiment_score': sentiment_score,
            'urgency_score': urgency_score,
            'complexity_score': complexity_score,
            'estimated_hours': estimated_hours if estimated_hours > 0 else None
        }
    
    def predict_task_priority(self, title, description=""):
        """Use AI to predict task priority."""
        if not self.model_trained:
            return 3  # Default priority
        
        try:
            # Analyze text features
            analysis = self.analyze_task_text(title, description)
            full_text = f"{title} {description}"
            
            # Vectorize text
            text_features = self.vectorizer.transform([full_text])
            
            # Create feature vector
            additional_features = np.array([[
                analysis['sentiment_score'],
                analysis['urgency_score'],
                analysis['complexity_score']
            ]])
            
            # Combine features
            if text_features.shape[1] > 0:
                combined_features = np.hstack([text_features.toarray(), additional_features])
            else:
                combined_features = additional_features
            
            # Predict priority
            predicted_priority = self.priority_model.predict(combined_features)[0]
            probability = self.priority_model.predict_proba(combined_features)[0]
            
            return {
                'priority': int(predicted_priority),
                'confidence': float(max(probability)),
                'analysis': analysis
            }
            
        except Exception as e:
            print(f"Priority prediction error: {e}")
            return 3
    
    def train_ai_models(self):
        """Train AI models with existing data."""
        conn = sqlite3.connect(self.db_path)
        
        # Get training data
        query = '''
            SELECT task_title, task_description, actual_priority
            FROM training_data
            UNION
            SELECT title, description, priority
            FROM tasks
            WHERE status = 'done' AND priority IS NOT NULL
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(df) < 10:
            # Generate synthetic training data if not enough real data
            self.generate_training_data()
            return
        
        try:
            # Prepare text data
            df['full_text'] = df['task_title'].fillna('') + ' ' + df['task_description'].fillna('')
            
            # Vectorize text
            X_text = self.vectorizer.fit_transform(df['full_text'])
            
            # Extract additional features
            additional_features = []
            for _, row in df.iterrows():
                analysis = self.analyze_task_text(row['task_title'], row['task_description'])
                additional_features.append([
                    analysis['sentiment_score'],
                    analysis['urgency_score'],
                    analysis['complexity_score']
                ])
            
            X_additional = np.array(additional_features)
            
            # Combine features
            X = np.hstack([X_text.toarray(), X_additional])
            y = df['actual_priority']
            
            # Train model
            if len(set(y)) > 1:  # Ensure we have multiple classes
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                self.priority_model.fit(X_train, y_train)
                
                # Test accuracy
                y_pred = self.priority_model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                print(f"AI Model trained with accuracy: {accuracy:.2f}")
                
                self.model_trained = True
                
                # Save model
                self.save_model()
            
        except Exception as e:
            print(f"Model training error: {e}")
            self.generate_training_data()
    
    def generate_training_data(self):
        """Generate synthetic training data for model training."""
        training_samples = [
            ("Fix critical bug", "System crashes on login", 5),
            ("Update documentation", "Add new API endpoints to docs", 2),
            ("Code review", "Review pull request for new feature", 3),
            ("Database optimization", "Improve query performance for reports", 4),
            ("Meeting preparation", "Prepare slides for client presentation", 3),
            ("Urgent customer issue", "Customer reports data loss", 5),
            ("Minor UI fix", "Adjust button alignment", 1),
            ("Security audit", "Review authentication system", 4),
            ("Write unit tests", "Add tests for payment module", 3),
            ("Deploy to production", "Release version 2.1.0", 4),
            ("Research new technology", "Evaluate machine learning frameworks", 2),
            ("Fix typo", "Correct spelling in email template", 1),
            ("Emergency server fix", "Server down, immediate attention needed", 5),
            ("Team meeting", "Weekly standup meeting", 2),
            ("Performance optimization", "Reduce page load times", 3),
            ("Data backup", "Create backup of user data", 4),
            ("Social media post", "Create content for product launch", 2),
            ("Critical deadline", "Submit proposal by end of day", 5),
            ("Refactor code", "Clean up legacy authentication code", 3),
            ("Customer feedback", "Analyze user survey responses", 2)
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for title, description, priority in training_samples:
            cursor.execute('''
                INSERT OR IGNORE INTO training_data (task_title, task_description, actual_priority)
                VALUES (?, ?, ?)
            ''', (title, description, priority))
        
        conn.commit()
        conn.close()
        
        # Retrain models
        self.train_ai_models()
    
    def save_model(self):
        """Save trained model to file."""
        try:
            model_data = {
                'vectorizer': self.vectorizer,
                'priority_model': self.priority_model,
                'model_trained': self.model_trained
            }
            with open('ai_task_model.pkl', 'wb') as f:
                pickle.dump(model_data, f)
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self):
        """Load trained model from file."""
        try:
            if os.path.exists('ai_task_model.pkl'):
                with open('ai_task_model.pkl', 'rb') as f:
                    model_data = pickle.load(f)
                    self.vectorizer = model_data['vectorizer']
                    self.priority_model = model_data['priority_model']
                    self.model_trained = model_data['model_trained']
                print("AI model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def create_task(self, title, description="", project_id=None, assigned_to=None, 
                   created_by=1, due_date=None, tags="", dependencies=""):
        """Create a new task with AI analysis."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # AI analysis
        ai_analysis = self.analyze_task_text(title, description)
        ai_priority = self.predict_task_priority(title, description)
        
        if isinstance(ai_priority, dict):
            predicted_priority = ai_priority['priority']
            ai_predicted_priority = ai_priority['confidence']
        else:
            predicted_priority = ai_priority
            ai_predicted_priority = 0.5
        
        cursor.execute('''
            INSERT INTO tasks (
                title, description, project_id, assigned_to, created_by,
                priority, ai_predicted_priority, due_date, tags, dependencies,
                sentiment_score, urgency_score, complexity_score, estimated_hours
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            title, description, project_id, assigned_to, created_by,
            predicted_priority, ai_predicted_priority, due_date, tags, dependencies,
            ai_analysis['sentiment_score'], ai_analysis['urgency_score'],
            ai_analysis['complexity_score'], ai_analysis['estimated_hours']
        ))
        
        task_id = cursor.lastrowid
        conn.commit()
        
        # Create notification if assigned to someone
        if assigned_to:
            self.create_notification(
                assigned_to,
                "New Task Assigned",
                f"You have been assigned a new task: {title}",
                "task_assigned",
                task_id
            )
        
        conn.close()
        return task_id
    
    def update_task(self, task_id, **kwargs):
        """Update task with specified fields."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build update query dynamically
        fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in ['title', 'description', 'status', 'priority', 'assigned_to', 
                        'due_date', 'tags', 'dependencies', 'actual_hours']:
                fields.append(f"{field} = ?")
                values.append(value)
        
        if fields:
            fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(task_id)
            
            query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            
            # Mark as completed if status is done
            if kwargs.get('status') == 'done':
                cursor.execute(
                    "UPDATE tasks SET completed_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (task_id,)
                )
            
            conn.commit()
        
        conn.close()
    
    def get_tasks(self, user_id=None, project_id=None, status=None, assigned_to=None):
        """Retrieve tasks with optional filtering."""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT t.*, p.name as project_name, u.username as assigned_username
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            LEFT JOIN users u ON t.assigned_to = u.id
            WHERE 1=1
        '''
        params = []
        
        if user_id:
            query += " AND (t.created_by = ? OR t.assigned_to = ?)"
            params.extend([user_id, user_id])
        if project_id:
            query += " AND t.project_id = ?"
            params.append(project_id)
        if status:
            query += " AND t.status = ?"
            params.append(status)
        if assigned_to:
            query += " AND t.assigned_to = ?"
            params.append(assigned_to)
        
        query += " ORDER BY t.priority DESC, t.due_date ASC, t.created_at DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df.to_dict('records') if not df.empty else []
    
    def get_smart_suggestions(self, user_id):
        """Get AI-powered task suggestions and insights."""
        conn = sqlite3.connect(self.db_path)
        
        # Get user's tasks
        query = '''
            SELECT * FROM tasks 
            WHERE assigned_to = ? OR created_by = ?
            ORDER BY created_at DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=[user_id, user_id])
        conn.close()
        
        suggestions = {
            'overdue_tasks': [],
            'high_priority_due_soon': [],
            'workload_insights': {},
            'productivity_tips': [],
            'time_estimates': {}
        }
        
        if df.empty:
            return suggestions
        
        now = datetime.datetime.now()
        
        # Find overdue tasks
        for _, task in df.iterrows():
            if task['due_date'] and task['status'] != 'done':
                due_date = datetime.datetime.fromisoformat(task['due_date'])
                if due_date < now:
                    suggestions['overdue_tasks'].append({
                        'id': task['id'],
                        'title': task['title'],
                        'days_overdue': (now - due_date).days
                    })
        
        # High priority tasks due soon
        for _, task in df.iterrows():
            if (task['due_date'] and task['priority'] >= 4 and 
                task['status'] not in ['done', 'review']):
                due_date = datetime.datetime.fromisoformat(task['due_date'])
                days_until_due = (due_date - now).days
                if 0 <= days_until_due <= 3:
                    suggestions['high_priority_due_soon'].append({
                        'id': task['id'],
                        'title': task['title'],
                        'days_until_due': days_until_due
                    })
        
        # Workload insights
        total_tasks = len(df)
        completed_tasks = len(df[df['status'] == 'done'])
        in_progress_tasks = len(df[df['status'] == 'in_progress'])
        
        suggestions['workload_insights'] = {
            'total_tasks': total_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'active_tasks': in_progress_tasks,
            'avg_priority': df['priority'].mean() if not df.empty else 0
        }
        
        # Productivity tips based on data
        if completed_tasks > 0:
            completed_df = df[df['status'] == 'done']
            avg_completion_time = completed_df['actual_hours'].mean()
            
            if avg_completion_time and avg_completion_time > 8:
                suggestions['productivity_tips'].append(
                    "Consider breaking down large tasks into smaller subtasks"
                )
            
            if len(suggestions['overdue_tasks']) > 3:
                suggestions['productivity_tips'].append(
                    "You have several overdue tasks. Consider setting more realistic deadlines"
                )
            
            high_priority_ratio = len(df[df['priority'] >= 4]) / total_tasks
            if high_priority_ratio > 0.7:
                suggestions['productivity_tips'].append(
                    "Most of your tasks are high priority. Consider reassessing priorities"
                )
        
        return suggestions
    
    def create_notification(self, user_id, title, message, notification_type="info", task_id=None):
        """Create a notification for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, related_task_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, title, message, notification_type, task_id))
        
        conn.commit()
        conn.close()
    
    def get_notifications(self, user_id, unread_only=False):
        """Get notifications for a user."""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM notifications WHERE user_id = ?"
        params = [user_id]
        
        if unread_only:
            query += " AND read = 0"
        
        query += " ORDER BY created_at DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df.to_dict('records') if not df.empty else []
    
    def mark_notification_read(self, notification_id):
        """Mark a notification as read."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notification_id,))
        conn.commit()
        conn.close()
    
    def get_analytics(self, user_id=None, days=30):
        """Get task analytics and insights."""
        conn = sqlite3.connect(self.db_path)
        
        base_query = '''
            SELECT * FROM tasks 
            WHERE created_at >= date('now', '-{} days')
        '''.format(days)
        
        params = []
        if user_id:
            base_query += " AND (created_by = ? OR assigned_to = ?)"
            params = [user_id, user_id]
        
        df = pd.read_sql_query(base_query, conn, params=params)
        conn.close()
        
        if df.empty:
            return {}
        
        analytics = {
            'task_completion_rate': len(df[df['status'] == 'done']) / len(df) * 100,
            'avg_completion_time': df[df['status'] == 'done']['actual_hours'].mean(),
            'priority_distribution': df['priority'].value_counts().to_dict(),
            'status_distribution': df['status'].value_counts().to_dict(),
            'tasks_by_day': df.groupby(df['created_at'].str[:10]).size().to_dict(),
            'overdue_tasks': len(df[
                (df['due_date'] < datetime.datetime.now().isoformat()) & 
                (df['status'] != 'done')
            ]),
            'ai_accuracy': self.calculate_ai_accuracy(df)
        }
        
        return analytics
    
    def calculate_ai_accuracy(self, df):
        """Calculate AI priority prediction accuracy."""
        if df.empty:
            return 0
        
        completed_tasks = df[df['status'] == 'done']
        if len(completed_tasks) < 5:
            return 0
        
        # Compare AI predicted priority with actual completion patterns
        # This is a simplified metric
        accurate_predictions = 0
        total_predictions = len(completed_tasks)
        
        for _, task in completed_tasks.iterrows():
            ai_priority = task.get('ai_predicted_priority', 0)
            actual_priority = task.get('priority', 3)
            
            # Consider prediction accurate if within 1 level
            if abs(ai_priority - actual_priority) <= 1:
                accurate_predictions += 1
        
        return (accurate_predictions / total_predictions) * 100 if total_predictions > 0 else 0

class TaskManagerWebApp:
    def __init__(self):
        """Initialize the Flask web application."""
        self.app = Flask(__name__)
        self.app.secret_key = 'ai_task_manager_secret_key_2024'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.task_manager = AITaskManager()
        
        self.setup_routes()
        self.setup_socket_events()
        
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def dashboard():
            if 'user_id' not in session:
                return render_template('login.html')
            return render_template('dashboard.html')
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                data = request.json
                user = self.task_manager.authenticate_user(
                    data['username'], data['password']
                )
                
                if user:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    return jsonify({'success': True, 'user': user})
                else:
                    return jsonify({'success': False, 'message': 'Invalid credentials'})
            
            return render_template('login.html')
        
        @self.app.route('/logout')
        def logout():
            session.clear()
            return render_template('login.html')
        
        @self.app.route('/api/tasks', methods=['GET', 'POST'])
        def api_tasks():
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            if request.method == 'POST':
                data = request.json
                task_id = self.task_manager.create_task(
                    title=data['title'],
                    description=data.get('description', ''),
                    project_id=data.get('project_id'),
                    assigned_to=data.get('assigned_to'),
                    created_by=session['user_id'],
                    due_date=data.get('due_date'),
                    tags=data.get('tags', ''),
                    dependencies=data.get('dependencies', '')
                )
                
                return jsonify({'success': True, 'task_id': task_id})
            
            else:
                tasks = self.task_manager.get_tasks(user_id=session['user_id'])
                return jsonify(tasks)
        
        @self.app.route('/api/tasks/<int:task_id>', methods=['PUT', 'DELETE'])
        def api_task_detail(task_id):
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            if request.method == 'PUT':
                data = request.json
                self.task_manager.update_task(task_id, **data)
                return jsonify({'success': True})
            
            elif request.method == 'DELETE':
                # For simplicity, we'll update status to 'archived'
                self.task_manager.update_task(task_id, status='archived')
                return jsonify({'success': True})
        
        @self.app.route('/api/suggestions')
        def api_suggestions():
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            suggestions = self.task_manager.get_smart_suggestions(session['user_id'])
            return jsonify(suggestions)
        
        @self.app.route('/api/analytics')
        def api_analytics():
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            analytics = self.task_manager.get_analytics(session['user_id'])
            return jsonify(analytics)
        
        @self.app.route('/api/notifications')
        def api_notifications():
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            notifications = self.task_manager.get_notifications(session['user_id'])
            return jsonify(notifications)
        
        @self.app.route('/api/predict-priority', methods=['POST'])
        def api_predict_priority():
            data = request.json
            prediction = self.task_manager.predict_task_priority(
                data['title'], data.get('description', '')
            )
            return jsonify(prediction)
    
    def setup_socket_events(self):
        """Setup SocketIO events for real-time updates."""
        
        @self.socketio.on('connect')
        def handle_connect():
            if 'user_id' in session:
                join_room(f"user_{session['user_id']}")
                emit('connected', {'message': 'Connected to real-time updates'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            if 'user_id' in session:
                leave_room(f"user_{session['user_id']}")
        
        @self.socketio.on('task_update')
        def handle_task_update(data):
            if 'user_id' in session:
                # Broadcast update to all connected clients
                self.socketio.emit('task_updated', data, room=f"user_{session['user_id']}")
    
    def create_templates(self):
        """Create HTML templates."""
        import os
        template_dir = 'templates'
        os.makedirs(template_dir, exist_ok=True)
        
        # Dashboard template
        dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Task Manager</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { background-color: #f8f9fa; }
        .task-card { transition: transform 0.2s; cursor: pointer; }
        .task-card:hover { transform: translateY(-2px); }
        .priority-1 { border-left: 4px solid #28a745; }
        .priority-2 { border-left: 4px solid #17a2b8; }
        .priority-3 { border-left: 4px solid #ffc107; }
        .priority-4 { border-left: 4px solid #fd7e14; }
        .priority-5 { border-left: 4px solid #dc3545; }
        .ai-badge { background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); }
        .suggestion-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <span class="navbar-brand">
                <i class="fas fa-brain"></i> AI Task Manager
            </span>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/logout"><i class="fas fa-sign-out-alt"></i> Logout</a>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-3">
                <!-- Quick Actions -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h6><i class="fas fa-plus"></i> Quick Actions</h6>
                    </div>
                    <div class="card-body">
                        <button class="btn btn-primary w-100 mb-2" onclick="showTaskModal()">
                            <i class="fas fa-plus"></i> New Task
                        </button>
                        <button class="btn btn-info w-100 mb-2" onclick="loadAnalytics()">
                            <i class="fas fa-chart-bar"></i> Analytics
                        </button>
                    </div>
                </div>

                <!-- AI Suggestions -->
                <div class="card mb-3 suggestion-card">
                    <div class="card-header">
                        <h6><i class="fas fa-lightbulb"></i> AI Suggestions</h6>
                    </div>
                    <div class="card-body" id="ai-suggestions">
                        <div class="text-center">
                            <div class="spinner-border text-light" role="status"></div>
                        </div>
                    </div>
                </div>

                <!-- Notifications -->
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-bell"></i> Notifications</h6>
                    </div>
                    <div class="card-body" id="notifications">
                        <div class="text-center text-muted">No new notifications</div>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="col-md-9">
                <!-- Task Filters -->
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <select class="form-select" id="status-filter">
                                    <option value="">All Statuses</option>
                                    <option value="todo">To Do</option>
                                    <option value="in_progress">In Progress</option>
                                    <option value="review">Review</option>
                                    <option value="done">Done</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <select class="form-select" id="priority-filter">
                                    <option value="">All Priorities</option>
                                    <option value="5">Critical</option>
                                    <option value="4">High</option>
                                    <option value="3">Medium</option>
                                    <option value="2">Low</option>
                                    <option value="1">Lowest</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <input type="text" class="form-control" id="search-tasks" 
                                       placeholder="Search tasks...">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Tasks Grid -->
                <div id="tasks-container">
                    <div class="text-center">
                        <div class="spinner-border text-primary" role="status"></div>
                        <p class="mt-2">Loading tasks...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Task Modal -->
    <div class="modal fade" id="taskModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create New Task</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="task-form">
                        <div class="mb-3">
                            <label class="form-label">Title *</label>
                            <input type="text" class="form-control" id="task-title" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Description</label>
                            <textarea class="form-control" id="task-description" rows="3"></textarea>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <label class="form-label">Due Date</label>
                                <input type="datetime-local" class="form-control" id="task-due-date">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Priority</label>
                                <select class="form-select" id="task-priority">
                                    <option value="1">Lowest</option>
                                    <option value="2">Low</option>
                                    <option value="3" selected>Medium</option>
                                    <option value="4">High</option>
                                    <option value="5">Critical</option>
                                </select>
                            </div>
                        </div>
                        <div class="mt-3">
                            <label class="form-label">Tags (comma separated)</label>
                            <input type="text" class="form-control" id="task-tags">
                        </div>
                        <div class="mt-3" id="ai-prediction" style="display: none;">
                            <div class="alert alert-info">
                                <i class="fas fa-brain"></i> <strong>AI Prediction:</strong>
                                <span id="ai-prediction-text"></span>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="createTask()">Create Task</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Initialize Socket.IO
        const socket = io();
        
        // Load initial data
        $(document).ready(function() {
            loadTasks();
            loadSuggestions();
            loadNotifications();
            
            // Setup real-time updates
            socket.on('task_updated', function(data) {
                loadTasks();
                loadSuggestions();
            });
            
            // Task filters
            $('#status-filter, #priority-filter').change(loadTasks);
            $('#search-tasks').on('input', debounce(loadTasks, 300));
            
            // AI prediction on task form
            $('#task-title, #task-description').on('input', debounce(predictPriority, 500));
        });

        function loadTasks() {
            $.get('/api/tasks', function(tasks) {
                displayTasks(tasks);
            });
        }

        function displayTasks(tasks) {
            const container = $('#tasks-container');
            
            if (tasks.length === 0) {
                container.html(`
                    <div class="text-center text-muted">
                        <i class="fas fa-tasks fa-3x mb-3"></i>
                        <h5>No tasks found</h5>
                        <p>Create your first task to get started!</p>
                    </div>
                `);
                return;
            }

            let html = '<div class="row">';
            
            tasks.forEach(task => {
                const priorityClass = `priority-${task.priority}`;
                const statusBadge = getStatusBadge(task.status);
                const aiScore = task.ai_predicted_priority ? 
                    `<span class="badge ai-badge ms-1">AI: ${(task.ai_predicted_priority * 100).toFixed(0)}%</span>` : '';
                
                html += `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card task-card ${priorityClass}" onclick="editTask(${task.id})">
                            <div class="card-body">
                                <h6 class="card-title">${task.title}</h6>
                                <p class="card-text text-muted small">${task.description || 'No description'}</p>
                                <div class="d-flex justify-content-between align-items-center">
                                    ${statusBadge}
                                    <div>
                                        <span class="badge bg-secondary">P${task.priority}</span>
                                        ${aiScore}
                                    </div>
                                </div>
                                ${task.due_date ? `<small class="text-muted">Due: ${formatDate(task.due_date)}</small>` : ''}
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            container.html(html);
        }

        function getStatusBadge(status) {
            const badges = {
                'todo': '<span class="badge bg-secondary">To Do</span>',
                'in_progress': '<span class="badge bg-primary">In Progress</span>',
                'review': '<span class="badge bg-warning">Review</span>',
                'done': '<span class="badge bg-success">Done</span>'
            };
            return badges[status] || '<span class="badge bg-secondary">Unknown</span>';
        }

        function loadSuggestions() {
            $.get('/api/suggestions', function(suggestions) {
                displaySuggestions(suggestions);
            });
        }

        function displaySuggestions(suggestions) {
            const container = $('#ai-suggestions');
            let html = '';

            if (suggestions.overdue_tasks && suggestions.overdue_tasks.length > 0) {
                html += `<div class="alert alert-warning mb-2">
                    <strong>⚠️ ${suggestions.overdue_tasks.length} overdue tasks</strong>
                </div>`;
            }

            if (suggestions.high_priority_due_soon && suggestions.high_priority_due_soon.length > 0) {
                html += `<div class="alert alert-info mb-2">
                    <strong>🔥 ${suggestions.high_priority_due_soon.length} high priority tasks due soon</strong>
                </div>`;
            }

            if (suggestions.productivity_tips && suggestions.productivity_tips.length > 0) {
                html += `<div class="mt-2">
                    <strong>💡 Tips:</strong>
                    <ul class="mb-0 mt-1">`;
                suggestions.productivity_tips.forEach(tip => {
                    html += `<li><small>${tip}</small></li>`;
                });
                html += '</ul></div>';
            }

            container.html(html || '<div class="text-center"><small>No suggestions at the moment</small></div>');
        }

        function loadNotifications() {
            $.get('/api/notifications', function(notifications) {
                displayNotifications(notifications.slice(0, 5));
            });
        }

        function displayNotifications(notifications) {
            const container = $('#notifications');
            
            if (notifications.length === 0) {
                container.html('<div class="text-center text-muted"><small>No new notifications</small></div>');
                return;
            }

            let html = '';
            notifications.forEach(notif => {
                html += `
                    <div class="border-bottom py-2">
                        <h6 class="mb-1">${notif.title}</h6>
                        <p class="mb-1 small">${notif.message}</p>
                        <small class="text-muted">${formatDate(notif.created_at)}</small>
                    </div>
                `;
            });
            
            container.html(html);
        }

        function showTaskModal() {
            $('#taskModal').modal('show');
        }

        function predictPriority() {
            const title = $('#task-title').val();
            const description = $('#task-description').val();
            
            if (title.length > 3) {
                $.post('/api/predict-priority', {
                    title: title,
                    description: description
                }, function(prediction) {
                    if (prediction.priority) {
                        $('#task-priority').val(prediction.priority);
                        $('#ai-prediction-text').text(
                            `Priority ${prediction.priority} (${(prediction.confidence * 100).toFixed(1)}% confidence)`
                        );
                        $('#ai-prediction').show();
                    }
                });
            }
        }

        function createTask() {
            const taskData = {
                title: $('#task-title').val(),
                description: $('#task-description').val(),
                due_date: $('#task-due-date').val(),
                priority: $('#task-priority').val(),
                tags: $('#task-tags').val()
            };

            $.post('/api/tasks', taskData, function(response) {
                if (response.success) {
                    $('#taskModal').modal('hide');
                    $('#task-form')[0].reset();
                    loadTasks();
                    loadSuggestions();
                }
            });
        }

        function editTask(taskId) {
            // Simplified - would open edit modal in full implementation
            const newStatus = prompt('Update status (todo/in_progress/review/done):');
            if (newStatus) {
                $.ajax({
                    url: `/api/tasks/${taskId}`,
                    method: 'PUT',
                    data: JSON.stringify({status: newStatus}),
                    contentType: 'application/json',
                    success: function() {
                        loadTasks();
                        loadSuggestions();
                    }
                });
            }
        }

        function formatDate(dateString) {
            return new Date(dateString).toLocaleDateString();
        }

        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }

        function loadAnalytics() {
            $.get('/api/analytics', function(analytics) {
                alert('Analytics: ' + JSON.stringify(analytics, null, 2));
            });
        }
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
    <title>AI Task Manager - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .login-card { background: rgba(255, 255, 255, 0.95); }
    </style>
</head>
<body class="d-flex align-items-center">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
                <div class="card login-card">
                    <div class="card-body p-5">
                        <div class="text-center mb-4">
                            <i class="fas fa-brain fa-3x text-primary mb-3"></i>
                            <h3>AI Task Manager</h3>
                            <p class="text-muted">Smart task management with AI insights</p>
                        </div>
                        
                        <form id="login-form">
                            <div class="mb-3">
                                <label class="form-label">Username</label>
                                <input type="text" class="form-control" id="username" value="admin" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input type="password" class="form-control" id="password" value="admin123" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">
                                <i class="fas fa-sign-in-alt"></i> Login
                            </button>
                        </form>
                        
                        <div class="text-center mt-3">
                            <small class="text-muted">
                                Default: admin / admin123
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        $('#login-form').submit(function(e) {
            e.preventDefault();
            
            $.post('/login', {
                username: $('#username').val(),
                password: $('#password').val()
            }, function(response) {
                if (response.success) {
                    window.location.href = '/';
                } else {
                    alert('Login failed: ' + response.message);
                }
            });
        });
    </script>
</body>
</html>
        '''
        
        with open(os.path.join(template_dir, 'dashboard.html'), 'w') as f:
            f.write(dashboard_html)
        
        with open(os.path.join(template_dir, 'login.html'), 'w') as f:
            f.write(login_html)
    
    def run(self, host='localhost', port=5000, debug=True):
        """Run the Flask application."""
        self.create_templates()
        
        print("🤖 AI-Powered Task Management System")
        print("=" * 50)
        print(f"🚀 Starting web application...")
        print(f"🌐 Access the dashboard at: http://{host}:{port}")
        print("🔑 Default login: admin / admin123")
        print("\n🤖 AI Features:")
        print("   - Smart priority prediction")
        print("   - Sentiment analysis")
        print("   - Workload insights")
        print("   - Productivity recommendations")
        print("   - Real-time notifications")
        
        self.socketio.run(self.app, host=host, port=port, debug=debug)

def main():
    """Main function to run the AI Task Manager."""
    print("🤖 AI-Powered Task Management System")
    print("=" * 50)
    
    choice = input("\nChoose interface:\n1. Web Application (Recommended)\n2. CLI Demo\nEnter choice (1-2): ")
    
    if choice == '2':
        # Command line demo
        task_manager = AITaskManager()
        
        print("\n🤖 AI Task Manager - CLI Demo")
        print("Creating sample tasks with AI analysis...")
        
        # Create sample tasks
        sample_tasks = [
            ("Fix critical bug in login system", "Users cannot login, system crashes on authentication", None, None),
            ("Write documentation for new API", "Document the new REST API endpoints for the mobile app", None, None),
            ("Plan team meeting", "Organize weekly standup meeting agenda", None, None),
            ("Optimize database queries", "Improve performance of slow reporting queries", None, None),
            ("Emergency server maintenance", "Server down, needs immediate attention", None, None)
        ]
        
        for title, description, project_id, assigned_to in sample_tasks:
            task_id = task_manager.create_task(title, description, project_id, assigned_to)
            print(f"✅ Created task {task_id}: {title}")
        
        # Show AI analysis
        print("\n🧠 AI Analysis Results:")
        tasks = task_manager.get_tasks()
        
        for task in tasks:
            print(f"\nTask: {task['title']}")
            print(f"  AI Priority: {task['priority']}")
            print(f"  Sentiment: {task['sentiment_score']:.2f}")
            print(f"  Urgency: {task['urgency_score']}")
            print(f"  Complexity: {task['complexity_score']}")
        
        # Show suggestions
        print("\n💡 AI Suggestions:")
        suggestions = task_manager.get_smart_suggestions(1)
        
        for category, items in suggestions.items():
            if items:
                print(f"  {category.replace('_', ' ').title()}:")
                if isinstance(items, list):
                    for item in items:
                        print(f"    - {item}")
                else:
                    print(f"    {items}")
        
        print("\n📊 Analytics:")
        analytics = task_manager.get_analytics(1)
        for key, value in analytics.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
    else:
        # Run web application
        app = TaskManagerWebApp()
        app.run()

if __name__ == "__main__":
    main()
