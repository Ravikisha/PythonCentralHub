# Simple Flask REST API

from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, timedelta
import hashlib
import secrets
import os
from functools import wraps
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
DATABASE = 'api_database.db'

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # API Keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    api_key VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Tasks table (example resource)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    completed BOOLEAN DEFAULT 0,
                    priority VARCHAR(10) DEFAULT 'medium',
                    due_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Products table (example resource)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    price DECIMAL(10,2) NOT NULL,
                    category VARCHAR(100),
                    stock_quantity INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # API Logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint VARCHAR(200),
                    method VARCHAR(10),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    api_key VARCHAR(255),
                    response_code INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            
        # Insert sample data
        self.insert_sample_data()
    
    def insert_sample_data(self):
        """Insert sample data for demonstration"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if sample data already exists
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] > 0:
                return
            
            # Sample users
            sample_users = [
                ('john_doe', 'john@example.com', hashlib.sha256('password123'.encode()).hexdigest()),
                ('jane_smith', 'jane@example.com', hashlib.sha256('password456'.encode()).hexdigest()),
                ('admin', 'admin@example.com', hashlib.sha256('admin123'.encode()).hexdigest())
            ]
            
            cursor.executemany(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                sample_users
            )
            
            # Sample API keys
            api_keys = [
                (1, 'demo_key_123456789', 'Demo Key'),
                (2, 'test_key_987654321', 'Test Key'),
                (3, 'admin_key_555666777', 'Admin Key')
            ]
            
            cursor.executemany(
                "INSERT INTO api_keys (user_id, api_key, name) VALUES (?, ?, ?)",
                api_keys
            )
            
            # Sample tasks
            sample_tasks = [
                ('Complete project documentation', 'Write comprehensive docs for the API', 0, 'high', '2023-12-31', 1),
                ('Fix bug in user authentication', 'Resolve login issues reported by users', 1, 'critical', '2023-12-15', 1),
                ('Implement new feature', 'Add search functionality to products', 0, 'medium', '2024-01-15', 2),
                ('Code review', 'Review pull requests from team members', 0, 'low', '2023-12-20', 2)
            ]
            
            cursor.executemany(
                "INSERT INTO tasks (title, description, completed, priority, due_date, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                sample_tasks
            )
            
            # Sample products
            sample_products = [
                ('Laptop', 'High-performance laptop for developers', 999.99, 'Electronics', 10),
                ('Smartphone', 'Latest model smartphone with advanced features', 599.99, 'Electronics', 25),
                ('Coffee Mug', 'Programmer-themed coffee mug', 14.99, 'Accessories', 50),
                ('Mechanical Keyboard', 'RGB mechanical keyboard for gaming', 149.99, 'Electronics', 15),
                ('Desk Lamp', 'Adjustable LED desk lamp', 39.99, 'Furniture', 30)
            ]
            
            cursor.executemany(
                "INSERT INTO products (name, description, price, category, stock_quantity) VALUES (?, ?, ?, ?, ?)",
                sample_products
            )
            
            conn.commit()

# Initialize database
db_manager = DatabaseManager(DATABASE)

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ak.id, ak.user_id, u.username 
                FROM api_keys ak 
                JOIN users u ON ak.user_id = u.id 
                WHERE ak.api_key = ? AND ak.is_active = 1 AND u.is_active = 1
            ''', (api_key,))
            
            result = cursor.fetchone()
            
            if not result:
                log_api_request(request, api_key, 401)
                return jsonify({'error': 'Invalid API key'}), 401
            
            # Update last used timestamp
            cursor.execute(
                "UPDATE api_keys SET last_used = CURRENT_TIMESTAMP WHERE api_key = ?",
                (api_key,)
            )
            conn.commit()
        
        # Log successful request
        log_api_request(request, api_key, 200)
        
        # Add user info to request context
        request.current_user_id = result[1]
        request.current_username = result[2]
        
        return f(*args, **kwargs)
    
    return decorated_function

def log_api_request(request_obj, api_key, response_code):
    """Log API request for monitoring"""
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO api_logs (endpoint, method, ip_address, user_agent, api_key, response_code)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                request_obj.endpoint,
                request_obj.method,
                request_obj.remote_addr,
                request_obj.headers.get('User-Agent', ''),
                api_key,
                response_code
            ))
            conn.commit()
    except Exception as e:
        logger.error(f"Error logging API request: {e}")

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# API Documentation endpoint
@app.route('/')
def api_documentation():
    """API Documentation"""
    docs = {
        "title": "Simple Flask REST API",
        "version": "1.0.0",
        "description": "A demonstration REST API with CRUD operations",
        "base_url": request.base_url,
        "authentication": {
            "type": "API Key",
            "header": "X-API-Key",
            "demo_keys": [
                "demo_key_123456789",
                "test_key_987654321",
                "admin_key_555666777"
            ]
        },
        "endpoints": {
            "Tasks": {
                "GET /api/tasks": "Get all tasks",
                "GET /api/tasks/<id>": "Get specific task",
                "POST /api/tasks": "Create new task",
                "PUT /api/tasks/<id>": "Update task",
                "DELETE /api/tasks/<id>": "Delete task"
            },
            "Products": {
                "GET /api/products": "Get all products",
                "GET /api/products/<id>": "Get specific product",
                "POST /api/products": "Create new product",
                "PUT /api/products/<id>": "Update product",
                "DELETE /api/products/<id>": "Delete product"
            },
            "Users": {
                "GET /api/users": "Get all users",
                "GET /api/users/<id>": "Get specific user",
                "POST /api/users": "Create new user"
            },
            "Statistics": {
                "GET /api/stats": "Get API usage statistics"
            }
        },
        "examples": {
            "create_task": {
                "method": "POST",
                "url": "/api/tasks",
                "headers": {"X-API-Key": "demo_key_123456789"},
                "body": {
                    "title": "New Task",
                    "description": "Task description",
                    "priority": "high",
                    "due_date": "2023-12-31"
                }
            }
        }
    }
    return jsonify(docs)

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Tasks API endpoints
@app.route('/api/tasks', methods=['GET'])
@require_api_key
def get_tasks():
    """Get all tasks with optional filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    completed = request.args.get('completed', type=bool)
    priority = request.args.get('priority')
    
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    
    if completed is not None:
        query += " AND completed = ?"
        params.append(completed)
    
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])
    
    with get_db_connection() as conn:
        tasks = conn.execute(query, params).fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM tasks WHERE 1=1"
        count_params = []
        if completed is not None:
            count_query += " AND completed = ?"
            count_params.append(completed)
        if priority:
            count_query += " AND priority = ?"
            count_params.append(priority)
        
        total = conn.execute(count_query, count_params).fetchone()[0]
    
    return jsonify({
        'tasks': [dict(task) for task in tasks],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    })

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@require_api_key
def get_task(task_id):
    """Get specific task"""
    with get_db_connection() as conn:
        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    
    if task is None:
        abort(404)
    
    return jsonify(dict(task))

@app.route('/api/tasks', methods=['POST'])
@require_api_key
def create_task():
    """Create new task"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    title = data['title']
    description = data.get('description', '')
    priority = data.get('priority', 'medium')
    due_date = data.get('due_date')
    user_id = request.current_user_id
    
    # Validate priority
    if priority not in ['low', 'medium', 'high', 'critical']:
        return jsonify({'error': 'Invalid priority. Use: low, medium, high, critical'}), 400
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (title, description, priority, due_date, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, priority, due_date, user_id))
        
        task_id = cursor.lastrowid
        conn.commit()
        
        # Get the created task
        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    
    return jsonify(dict(task)), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@require_api_key
def update_task(task_id):
    """Update task"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Check if task exists
    with get_db_connection() as conn:
        existing_task = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        
        if existing_task is None:
            abort(404)
        
        # Build update query
        update_fields = []
        params = []
        
        for field in ['title', 'description', 'completed', 'priority', 'due_date']:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(task_id)
            
            query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
            conn.execute(query, params)
            conn.commit()
        
        # Get updated task
        updated_task = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
    
    return jsonify(dict(updated_task))

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@require_api_key
def delete_task(task_id):
    """Delete task"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        
        if cursor.rowcount == 0:
            abort(404)
        
        conn.commit()
    
    return '', 204

# Products API endpoints
@app.route('/api/products', methods=['GET'])
@require_api_key
def get_products():
    """Get all products with optional filtering"""
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    in_stock = request.args.get('in_stock', type=bool)
    
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    if min_price is not None:
        query += " AND price >= ?"
        params.append(min_price)
    
    if max_price is not None:
        query += " AND price <= ?"
        params.append(max_price)
    
    if in_stock is not None:
        if in_stock:
            query += " AND stock_quantity > 0"
        else:
            query += " AND stock_quantity = 0"
    
    query += " ORDER BY name"
    
    with get_db_connection() as conn:
        products = conn.execute(query, params).fetchall()
    
    return jsonify({
        'products': [dict(product) for product in products]
    })

@app.route('/api/products/<int:product_id>', methods=['GET'])
@require_api_key
def get_product(product_id):
    """Get specific product"""
    with get_db_connection() as conn:
        product = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
    
    if product is None:
        abort(404)
    
    return jsonify(dict(product))

@app.route('/api/products', methods=['POST'])
@require_api_key
def create_product():
    """Create new product"""
    data = request.get_json()
    
    required_fields = ['name', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    name = data['name']
    description = data.get('description', '')
    price = data['price']
    category = data.get('category', '')
    stock_quantity = data.get('stock_quantity', 0)
    
    # Validate price
    try:
        price = float(price)
        if price < 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({'error': 'Price must be a valid positive number'}), 400
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, description, price, category, stock_quantity)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, description, price, category, stock_quantity))
        
        product_id = cursor.lastrowid
        conn.commit()
        
        # Get the created product
        product = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
    
    return jsonify(dict(product)), 201

@app.route('/api/products/<int:product_id>', methods=['PUT'])
@require_api_key
def update_product(product_id):
    """Update product"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    with get_db_connection() as conn:
        existing_product = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        
        if existing_product is None:
            abort(404)
        
        # Build update query
        update_fields = []
        params = []
        
        for field in ['name', 'description', 'price', 'category', 'stock_quantity']:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(product_id)
            
            query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
            conn.execute(query, params)
            conn.commit()
        
        # Get updated product
        updated_product = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
    
    return jsonify(dict(updated_product))

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@require_api_key
def delete_product(product_id):
    """Delete product"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        
        if cursor.rowcount == 0:
            abort(404)
        
        conn.commit()
    
    return '', 204

# Users API endpoints
@app.route('/api/users', methods=['GET'])
@require_api_key
def get_users():
    """Get all users (limited info)"""
    with get_db_connection() as conn:
        users = conn.execute(
            "SELECT id, username, email, created_at, is_active FROM users ORDER BY created_at DESC"
        ).fetchall()
    
    return jsonify({
        'users': [dict(user) for user in users]
    })

@app.route('/api/users/<int:user_id>', methods=['GET'])
@require_api_key
def get_user(user_id):
    """Get specific user"""
    with get_db_connection() as conn:
        user = conn.execute(
            "SELECT id, username, email, created_at, is_active FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
    
    if user is None:
        abort(404)
    
    return jsonify(dict(user))

@app.route('/api/users', methods=['POST'])
@require_api_key
def create_user():
    """Create new user"""
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    username = data['username']
    email = data['email']
    password = data['password']
    
    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Get the created user (without password)
            user = conn.execute(
                "SELECT id, username, email, created_at, is_active FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
        
        return jsonify(dict(user)), 201
    
    except sqlite3.IntegrityError as e:
        if 'username' in str(e):
            return jsonify({'error': 'Username already exists'}), 400
        elif 'email' in str(e):
            return jsonify({'error': 'Email already exists'}), 400
        else:
            return jsonify({'error': 'Database constraint violation'}), 400

# Statistics endpoint
@app.route('/api/stats', methods=['GET'])
@require_api_key
def get_statistics():
    """Get API usage statistics"""
    with get_db_connection() as conn:
        # Basic counts
        task_count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        product_count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        
        # API usage stats
        total_requests = conn.execute("SELECT COUNT(*) FROM api_logs").fetchone()[0]
        
        # Recent activity (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        recent_requests = conn.execute(
            "SELECT COUNT(*) FROM api_logs WHERE timestamp > ?", (yesterday,)
        ).fetchone()[0]
        
        # Top endpoints
        top_endpoints = conn.execute('''
            SELECT endpoint, COUNT(*) as count 
            FROM api_logs 
            GROUP BY endpoint 
            ORDER BY count DESC 
            LIMIT 5
        ''').fetchall()
        
        # Response code distribution
        response_codes = conn.execute('''
            SELECT response_code, COUNT(*) as count 
            FROM api_logs 
            GROUP BY response_code 
            ORDER BY response_code
        ''').fetchall()
    
    return jsonify({
        'database_stats': {
            'tasks': task_count,
            'products': product_count,
            'users': user_count
        },
        'api_usage': {
            'total_requests': total_requests,
            'requests_last_24h': recent_requests,
            'top_endpoints': [dict(row) for row in top_endpoints],
            'response_codes': [dict(row) for row in response_codes]
        },
        'timestamp': datetime.now().isoformat()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def main():
    """Main function to run the Flask REST API"""
    print("Simple Flask REST API")
    print("=====================")
    print("\nAPI Documentation: http://localhost:5000/")
    print("Health Check: http://localhost:5000/health")
    print("\nDemo API Keys:")
    print("- demo_key_123456789")
    print("- test_key_987654321") 
    print("- admin_key_555666777")
    print("\nExample usage:")
    print("curl -H 'X-API-Key: demo_key_123456789' http://localhost:5000/api/tasks")
    print("\nStarting server...")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
