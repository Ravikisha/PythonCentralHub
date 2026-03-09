#!/usr/bin/env python3
"""
URL Shortener with Analytics
A comprehensive URL shortening service with click tracking, analytics, and management features.
Features: URL shortening, click analytics, QR code generation, expiration dates, custom aliases
"""

import sqlite3
import hashlib
import random
import string
import datetime
import json
import webbrowser
from urllib.parse import urlparse
import qrcode
from io import BytesIO
import base64
from flask import Flask, request, jsonify, redirect, render_template_string
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict

class URLShortenerAnalytics:
    def __init__(self, db_path="url_shortener.db"):
        self.db_path = db_path
        self.base_url = "http://localhost:5000/"
        self.init_database()
        
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # URLs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_url TEXT NOT NULL,
                    short_code TEXT UNIQUE NOT NULL,
                    custom_alias TEXT UNIQUE,
                    title TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    total_clicks INTEGER DEFAULT 0,
                    unique_clicks INTEGER DEFAULT 0,
                    creator_ip TEXT,
                    password_hash TEXT
                )
            ''')
            
            # Clicks table for analytics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clicks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url_id INTEGER,
                    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    referrer TEXT,
                    country TEXT,
                    device_type TEXT,
                    browser TEXT,
                    FOREIGN KEY (url_id) REFERENCES urls (id)
                )
            ''')
            
            conn.commit()
    
    def generate_short_code(self, length=6):
        """Generate a random short code"""
        characters = string.ascii_letters + string.digits
        while True:
            short_code = ''.join(random.choice(characters) for _ in range(length))
            if not self.get_url_by_code(short_code):
                return short_code
    
    def validate_url(self, url):
        """Validate if the URL is properly formatted"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def create_short_url(self, original_url, custom_alias=None, title=None, 
                        description=None, expires_days=None, password=None, creator_ip=None):
        """Create a shortened URL"""
        if not self.validate_url(original_url):
            return {"success": False, "error": "Invalid URL format"}
        
        # Use custom alias or generate short code
        if custom_alias:
            if self.get_url_by_code(custom_alias):
                return {"success": False, "error": "Custom alias already exists"}
            short_code = custom_alias
        else:
            short_code = self.generate_short_code()
        
        # Calculate expiration date
        expires_at = None
        if expires_days:
            expires_at = datetime.datetime.now() + datetime.timedelta(days=expires_days)
        
        # Hash password if provided
        password_hash = None
        if password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO urls (original_url, short_code, custom_alias, title, 
                                    description, expires_at, creator_ip, password_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (original_url, short_code, custom_alias, title, description, 
                     expires_at, creator_ip, password_hash))
                
                url_id = cursor.lastrowid
                conn.commit()
                
                # Generate QR code
                qr_code = self.generate_qr_code(self.base_url + short_code)
                
                return {
                    "success": True,
                    "short_url": self.base_url + short_code,
                    "short_code": short_code,
                    "original_url": original_url,
                    "qr_code": qr_code,
                    "expires_at": expires_at.isoformat() if expires_at else None,
                    "id": url_id
                }
        except sqlite3.Error as e:
            return {"success": False, "error": str(e)}
    
    def get_url_by_code(self, short_code):
        """Get URL information by short code"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM urls WHERE short_code = ? OR custom_alias = ?
            ''', (short_code, short_code))
            return cursor.fetchone()
    
    def track_click(self, url_id, ip_address=None, user_agent=None, referrer=None):
        """Track a click for analytics"""
        # Parse user agent for device/browser info
        device_type = self.parse_device_type(user_agent) if user_agent else "Unknown"
        browser = self.parse_browser(user_agent) if user_agent else "Unknown"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert click record
            cursor.execute('''
                INSERT INTO clicks (url_id, ip_address, user_agent, referrer, device_type, browser)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (url_id, ip_address, user_agent, referrer, device_type, browser))
            
            # Update URL click counts
            cursor.execute('''
                UPDATE urls SET total_clicks = total_clicks + 1 WHERE id = ?
            ''', (url_id,))
            
            # Update unique clicks (simplified - based on IP)
            cursor.execute('''
                SELECT COUNT(DISTINCT ip_address) FROM clicks WHERE url_id = ?
            ''', (url_id,))
            unique_count = cursor.fetchone()[0]
            
            cursor.execute('''
                UPDATE urls SET unique_clicks = ? WHERE id = ?
            ''', (unique_count, url_id))
            
            conn.commit()
    
    def parse_device_type(self, user_agent):
        """Parse device type from user agent"""
        if not user_agent:
            return "Unknown"
        
        user_agent = user_agent.lower()
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            return "Mobile"
        elif 'tablet' in user_agent or 'ipad' in user_agent:
            return "Tablet"
        else:
            return "Desktop"
    
    def parse_browser(self, user_agent):
        """Parse browser from user agent"""
        if not user_agent:
            return "Unknown"
        
        user_agent = user_agent.lower()
        if 'chrome' in user_agent:
            return "Chrome"
        elif 'firefox' in user_agent:
            return "Firefox"
        elif 'safari' in user_agent and 'chrome' not in user_agent:
            return "Safari"
        elif 'edge' in user_agent:
            return "Edge"
        else:
            return "Other"
    
    def generate_qr_code(self, url):
        """Generate QR code for the URL"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Convert to base64 for web display
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def get_analytics(self, url_id):
        """Get comprehensive analytics for a URL"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Basic URL info
            cursor.execute('SELECT * FROM urls WHERE id = ?', (url_id,))
            url_info = cursor.fetchone()
            
            if not url_info:
                return None
            
            # Click analytics
            cursor.execute('''
                SELECT 
                    DATE(clicked_at) as date,
                    COUNT(*) as clicks
                FROM clicks 
                WHERE url_id = ? 
                GROUP BY DATE(clicked_at)
                ORDER BY date
            ''', (url_id,))
            daily_clicks = cursor.fetchall()
            
            # Device analytics
            cursor.execute('''
                SELECT device_type, COUNT(*) as count
                FROM clicks 
                WHERE url_id = ? 
                GROUP BY device_type
            ''', (url_id,))
            device_stats = cursor.fetchall()
            
            # Browser analytics
            cursor.execute('''
                SELECT browser, COUNT(*) as count
                FROM clicks 
                WHERE url_id = ? 
                GROUP BY browser
            ''', (url_id,))
            browser_stats = cursor.fetchall()
            
            # Referrer analytics
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN referrer IS NULL OR referrer = '' THEN 'Direct'
                        ELSE referrer 
                    END as ref,
                    COUNT(*) as count
                FROM clicks 
                WHERE url_id = ? 
                GROUP BY ref
                ORDER BY count DESC
                LIMIT 10
            ''', (url_id,))
            referrer_stats = cursor.fetchall()
            
            return {
                "url_info": {
                    "id": url_info[0],
                    "original_url": url_info[1],
                    "short_code": url_info[2],
                    "title": url_info[4],
                    "created_at": url_info[6],
                    "total_clicks": url_info[9],
                    "unique_clicks": url_info[10]
                },
                "daily_clicks": daily_clicks,
                "device_stats": device_stats,
                "browser_stats": browser_stats,
                "referrer_stats": referrer_stats
            }
    
    def list_urls(self, creator_ip=None, limit=50):
        """List all URLs with basic stats"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT id, original_url, short_code, title, created_at, 
                       total_clicks, unique_clicks, is_active, expires_at
                FROM urls
            '''
            params = []
            
            if creator_ip:
                query += ' WHERE creator_ip = ?'
                params.append(creator_ip)
            
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def delete_url(self, url_id, creator_ip=None):
        """Delete a URL and its analytics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Verify ownership if creator_ip provided
            if creator_ip:
                cursor.execute('SELECT creator_ip FROM urls WHERE id = ?', (url_id,))
                result = cursor.fetchone()
                if not result or result[0] != creator_ip:
                    return False
            
            # Delete clicks first (foreign key constraint)
            cursor.execute('DELETE FROM clicks WHERE url_id = ?', (url_id,))
            
            # Delete URL
            cursor.execute('DELETE FROM urls WHERE id = ?', (url_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def generate_analytics_chart(self, url_id, chart_type="daily_clicks"):
        """Generate analytics charts"""
        analytics = self.get_analytics(url_id)
        if not analytics:
            return None
        
        plt.style.use('seaborn-v0_8')
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == "daily_clicks":
            dates = [datetime.datetime.strptime(row[0], '%Y-%m-%d').date() 
                    for row in analytics['daily_clicks']]
            clicks = [row[1] for row in analytics['daily_clicks']]
            
            ax.plot(dates, clicks, marker='o', linewidth=2, markersize=6)
            ax.set_title('Daily Clicks Over Time', fontsize=16, fontweight='bold')
            ax.set_xlabel('Date')
            ax.set_ylabel('Clicks')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.xticks(rotation=45)
            
        elif chart_type == "device_stats":
            devices = [row[0] for row in analytics['device_stats']]
            counts = [row[1] for row in analytics['device_stats']]
            
            ax.pie(counts, labels=devices, autopct='%1.1f%%', startangle=90)
            ax.set_title('Device Type Distribution', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        # Save to bytes
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        # Convert to base64
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"

# Flask Web Interface
app = Flask(__name__)
shortener = URLShortenerAnalytics()

# HTML Templates
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>URL Shortener with Analytics</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea, select { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { background: #f8f9fa; padding: 15px; border-radius: 4px; margin: 15px 0; }
        .qr-code { text-align: center; margin: 15px 0; }
        .error { background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; padding: 10px; border-radius: 4px; }
        .urls-list { margin-top: 30px; }
        .url-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #007bff; }
        .stats { display: flex; gap: 20px; margin: 10px 0; }
        .stat { background: white; padding: 10px; border-radius: 4px; text-align: center; flex: 1; }
    </style>
</head>
<body>
    <h1>🔗 URL Shortener with Analytics</h1>
    
    <form method="post" action="/shorten">
        <div class="form-group">
            <label>Original URL:</label>
            <input type="url" name="url" required placeholder="https://example.com">
        </div>
        
        <div class="form-group">
            <label>Custom Alias (optional):</label>
            <input type="text" name="alias" placeholder="my-custom-link">
        </div>
        
        <div class="form-group">
            <label>Title (optional):</label>
            <input type="text" name="title" placeholder="Link title">
        </div>
        
        <div class="form-group">
            <label>Description (optional):</label>
            <textarea name="description" placeholder="Link description"></textarea>
        </div>
        
        <div class="form-group">
            <label>Expires in (days, optional):</label>
            <input type="number" name="expires_days" placeholder="30">
        </div>
        
        <button type="submit">🔗 Create Short URL</button>
    </form>
    
    <div class="urls-list">
        <h2>📊 Recent URLs</h2>
        {% for url in urls %}
        <div class="url-item">
            <h3>{{ url[3] or 'Untitled' }}</h3>
            <p><strong>Short URL:</strong> <a href="/{{ url[2] }}" target="_blank">{{ base_url }}{{ url[2] }}</a></p>
            <p><strong>Original:</strong> <a href="{{ url[1] }}" target="_blank">{{ url[1] }}</a></p>
            <div class="stats">
                <div class="stat">
                    <strong>{{ url[5] }}</strong><br>Total Clicks
                </div>
                <div class="stat">
                    <strong>{{ url[6] }}</strong><br>Unique Clicks
                </div>
                <div class="stat">
                    <strong>{{ url[4][:10] }}</strong><br>Created
                </div>
            </div>
            <a href="/analytics/{{ url[0] }}">📈 View Analytics</a>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

ANALYTICS_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Analytics - URL Shortener</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
        .chart-container { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .chart { text-align: center; margin: 20px 0; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
        .back-link { color: #007bff; text-decoration: none; margin-bottom: 20px; display: inline-block; }
    </style>
</head>
<body>
    <a href="/" class="back-link">← Back to Home</a>
    
    <div class="header">
        <h1>📊 Analytics Dashboard</h1>
        <h2>{{ analytics.url_info.title or 'Untitled' }}</h2>
        <p><strong>Short URL:</strong> {{ base_url }}{{ analytics.url_info.short_code }}</p>
        <p><strong>Original URL:</strong> <a href="{{ analytics.url_info.original_url }}" target="_blank">{{ analytics.url_info.original_url }}</a></p>
        <p><strong>Created:</strong> {{ analytics.url_info.created_at }}</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{{ analytics.url_info.total_clicks }}</div>
            <div>Total Clicks</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ analytics.url_info.unique_clicks }}</div>
            <div>Unique Clicks</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ analytics.daily_clicks|length }}</div>
            <div>Active Days</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ '%.1f'|format((analytics.url_info.total_clicks / analytics.daily_clicks|length) if analytics.daily_clicks else 0) }}</div>
            <div>Avg. Daily Clicks</div>
        </div>
    </div>
    
    {% if daily_chart %}
    <div class="chart-container">
        <h3>📈 Daily Clicks</h3>
        <div class="chart">
            <img src="{{ daily_chart }}" alt="Daily Clicks Chart" style="max-width: 100%;">
        </div>
    </div>
    {% endif %}
    
    {% if device_chart %}
    <div class="chart-container">
        <h3>📱 Device Distribution</h3>
        <div class="chart">
            <img src="{{ device_chart }}" alt="Device Distribution Chart" style="max-width: 100%;">
        </div>
    </div>
    {% endif %}
    
    <div class="chart-container">
        <h3>🌐 Browser Statistics</h3>
        <table>
            <tr><th>Browser</th><th>Clicks</th><th>Percentage</th></tr>
            {% for browser, count in analytics.browser_stats %}
            <tr>
                <td>{{ browser }}</td>
                <td>{{ count }}</td>
                <td>{{ '%.1f'|format((count / analytics.url_info.total_clicks * 100) if analytics.url_info.total_clicks > 0 else 0) }}%</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    
    <div class="chart-container">
        <h3>🔗 Top Referrers</h3>
        <table>
            <tr><th>Referrer</th><th>Clicks</th><th>Percentage</th></tr>
            {% for referrer, count in analytics.referrer_stats %}
            <tr>
                <td>{{ referrer }}</td>
                <td>{{ count }}</td>
                <td>{{ '%.1f'|format((count / analytics.url_info.total_clicks * 100) if analytics.url_info.total_clicks > 0 else 0) }}%</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    urls = shortener.list_urls(limit=10)
    return render_template_string(HOME_TEMPLATE, urls=urls, base_url=shortener.base_url)

@app.route('/shorten', methods=['POST'])
def create_short_url():
    original_url = request.form.get('url')
    custom_alias = request.form.get('alias')
    title = request.form.get('title')
    description = request.form.get('description')
    expires_days = request.form.get('expires_days')
    creator_ip = request.remote_addr
    
    expires_days = int(expires_days) if expires_days else None
    
    result = shortener.create_short_url(
        original_url=original_url,
        custom_alias=custom_alias or None,
        title=title or None,
        description=description or None,
        expires_days=expires_days,
        creator_ip=creator_ip
    )
    
    if result['success']:
        return f'''
        <div style="max-width: 600px; margin: 50px auto; padding: 20px; font-family: Arial;">
            <div style="background: #d4edda; color: #155724; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h2>✅ URL Shortened Successfully!</h2>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Short URL:</strong> <a href="{result['short_url']}" target="_blank">{result['short_url']}</a></p>
                <p><strong>Original URL:</strong> {result['original_url']}</p>
                
                <div style="text-align: center; margin: 20px 0;">
                    <h3>📱 QR Code</h3>
                    <img src="{result['qr_code']}" alt="QR Code" style="max-width: 200px;">
                </div>
                
                <div style="text-align: center; margin: 20px 0;">
                    <a href="/" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Create Another</a>
                    <a href="/analytics/{result['id']}" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-left: 10px;">View Analytics</a>
                </div>
            </div>
        </div>
        '''
    else:
        return f'''
        <div style="max-width: 600px; margin: 50px auto; padding: 20px; font-family: Arial;">
            <div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 8px;">
                <h2>❌ Error</h2>
                <p>{result['error']}</p>
                <a href="/" style="color: #721c24;">← Go Back</a>
            </div>
        </div>
        '''

@app.route('/<short_code>')
def redirect_url(short_code):
    url_data = shortener.get_url_by_code(short_code)
    
    if not url_data:
        return "URL not found", 404
    
    # Check if expired
    if url_data[7]:  # expires_at
        expires_at = datetime.datetime.fromisoformat(url_data[7])
        if datetime.datetime.now() > expires_at:
            return "URL has expired", 410
    
    # Track the click
    shortener.track_click(
        url_id=url_data[0],
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        referrer=request.headers.get('Referer')
    )
    
    return redirect(url_data[1])  # original_url

@app.route('/analytics/<int:url_id>')
def analytics(url_id):
    analytics_data = shortener.get_analytics(url_id)
    
    if not analytics_data:
        return "URL not found", 404
    
    # Generate charts
    daily_chart = shortener.generate_analytics_chart(url_id, "daily_clicks")
    device_chart = shortener.generate_analytics_chart(url_id, "device_stats")
    
    return render_template_string(
        ANALYTICS_TEMPLATE,
        analytics=analytics_data,
        base_url=shortener.base_url,
        daily_chart=daily_chart,
        device_chart=device_chart
    )

@app.route('/api/shorten', methods=['POST'])
def api_shorten():
    data = request.get_json()
    result = shortener.create_short_url(
        original_url=data.get('url'),
        custom_alias=data.get('alias'),
        title=data.get('title'),
        description=data.get('description'),
        expires_days=data.get('expires_days'),
        creator_ip=request.remote_addr
    )
    return jsonify(result)

@app.route('/api/analytics/<int:url_id>')
def api_analytics(url_id):
    analytics_data = shortener.get_analytics(url_id)
    if not analytics_data:
        return jsonify({"error": "URL not found"}), 404
    return jsonify(analytics_data)

def main():
    print("🔗 URL Shortener with Analytics")
    print("=" * 40)
    
    while True:
        print("\n📋 Menu:")
        print("1. Create Short URL")
        print("2. View Analytics")
        print("3. List All URLs")
        print("4. Start Web Server")
        print("5. Delete URL")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            original_url = input("Enter the URL to shorten: ").strip()
            custom_alias = input("Custom alias (optional): ").strip() or None
            title = input("Title (optional): ").strip() or None
            description = input("Description (optional): ").strip() or None
            
            expires_input = input("Expires in days (optional): ").strip()
            expires_days = int(expires_input) if expires_input else None
            
            result = shortener.create_short_url(
                original_url=original_url,
                custom_alias=custom_alias,
                title=title,
                description=description,
                expires_days=expires_days
            )
            
            if result['success']:
                print(f"\n✅ Short URL created!")
                print(f"Short URL: {result['short_url']}")
                print(f"QR Code generated: Yes")
                if result['expires_at']:
                    print(f"Expires: {result['expires_at']}")
            else:
                print(f"\n❌ Error: {result['error']}")
        
        elif choice == '2':
            url_id = input("Enter URL ID for analytics: ").strip()
            try:
                url_id = int(url_id)
                analytics = shortener.get_analytics(url_id)
                
                if analytics:
                    info = analytics['url_info']
                    print(f"\n📊 Analytics for: {info['title'] or 'Untitled'}")
                    print(f"Short Code: {info['short_code']}")
                    print(f"Original URL: {info['original_url']}")
                    print(f"Total Clicks: {info['total_clicks']}")
                    print(f"Unique Clicks: {info['unique_clicks']}")
                    print(f"Created: {info['created_at']}")
                    
                    if analytics['daily_clicks']:
                        print("\n📈 Daily Clicks:")
                        for date, clicks in analytics['daily_clicks'][-7:]:  # Last 7 days
                            print(f"  {date}: {clicks} clicks")
                    
                    if analytics['device_stats']:
                        print("\n📱 Device Stats:")
                        for device, count in analytics['device_stats']:
                            print(f"  {device}: {count} clicks")
                else:
                    print("❌ URL not found")
            except ValueError:
                print("❌ Invalid URL ID")
        
        elif choice == '3':
            urls = shortener.list_urls(limit=20)
            print(f"\n📋 URLs (showing last 20):")
            print("-" * 80)
            for url in urls:
                status = "✅ Active" if url[7] else "❌ Inactive"
                print(f"ID: {url[0]} | {url[2]} | Clicks: {url[5]} | {status}")
                print(f"   Title: {url[3] or 'Untitled'}")
                print(f"   URL: {url[1][:60]}{'...' if len(url[1]) > 60 else ''}")
                print("-" * 80)
        
        elif choice == '4':
            print("\n🌐 Starting web server...")
            print("Access the web interface at: http://localhost:5000")
            print("Press Ctrl+C to stop the server")
            try:
                app.run(debug=True, host='0.0.0.0', port=5000)
            except KeyboardInterrupt:
                print("\n🛑 Server stopped")
        
        elif choice == '5':
            url_id = input("Enter URL ID to delete: ").strip()
            try:
                url_id = int(url_id)
                if shortener.delete_url(url_id):
                    print("✅ URL deleted successfully")
                else:
                    print("❌ URL not found or couldn't be deleted")
            except ValueError:
                print("❌ Invalid URL ID")
        
        elif choice == '6':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
