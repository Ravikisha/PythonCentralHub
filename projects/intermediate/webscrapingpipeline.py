import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import json
import time
import random
import logging
from datetime import datetime, timedelta
import schedule
import threading
from urllib.parse import urljoin, urlparse, parse_qs
from urllib.robotparser import RobotFileParser
import hashlib
import re
import csv
import os
from pathlib import Path
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders

# Advanced scraping libraries
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Data processing and analysis
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import nltk
from textblob import TextBlob

# Web framework for monitoring dashboard
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

# Rate limiting and caching
from functools import wraps
from collections import defaultdict, deque
import pickle

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

class RateLimiter:
    def __init__(self, max_requests=10, time_window=60):
        """Initialize rate limiter with requests per time window."""
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(deque)
    
    def is_allowed(self, domain):
        """Check if request to domain is allowed based on rate limit."""
        now = time.time()
        domain_requests = self.requests[domain]
        
        # Remove old requests outside time window
        while domain_requests and domain_requests[0] <= now - self.time_window:
            domain_requests.popleft()
        
        # Check if under limit
        if len(domain_requests) < self.max_requests:
            domain_requests.append(now)
            return True
        
        return False
    
    def wait_time(self, domain):
        """Get wait time until next request is allowed."""
        if not self.requests[domain]:
            return 0
        
        oldest_request = self.requests[domain][0]
        wait_time = self.time_window - (time.time() - oldest_request)
        return max(0, wait_time)

class ScrapingDatabase:
    def __init__(self, db_path="web_scraping.db"):
        """Initialize the web scraping database."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables for web scraping pipeline."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Scraping projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                target_urls TEXT NOT NULL,
                scraping_rules TEXT NOT NULL,
                schedule_config TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Scraped data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                data_hash TEXT NOT NULL,
                raw_data TEXT NOT NULL,
                processed_data TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT CHECK(status IN ('success', 'failed', 'duplicate')) DEFAULT 'success',
                FOREIGN KEY (project_id) REFERENCES scraping_projects (id)
            )
        ''')
        
        # Scraping logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                status TEXT CHECK(status IN ('success', 'failed', 'skipped', 'rate_limited')) NOT NULL,
                response_code INTEGER,
                error_message TEXT,
                execution_time REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES scraping_projects (id)
            )
        ''')
        
        # Data validation rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                field_name TEXT NOT NULL,
                validation_type TEXT CHECK(validation_type IN ('required', 'type', 'format', 'range', 'custom')) NOT NULL,
                validation_config TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES scraping_projects (id)
            )
        ''')
        
        # Monitoring alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                alert_type TEXT CHECK(alert_type IN ('error_rate', 'data_quality', 'schedule_failure', 'rate_limit')) NOT NULL,
                threshold_config TEXT NOT NULL,
                notification_config TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                last_triggered TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES scraping_projects (id)
            )
        ''')
        
        # Exported reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exported_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                report_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                record_count INTEGER NOT NULL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES scraping_projects (id)
            )
        ''')
        
        # Site metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS site_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT UNIQUE NOT NULL,
                robots_txt TEXT,
                crawl_delay REAL DEFAULT 1.0,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_accessible BOOLEAN DEFAULT 1,
                error_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()

class WebScraper:
    def __init__(self, rate_limiter=None, use_selenium=False):
        """Initialize web scraper with optional rate limiting and browser automation."""
        self.rate_limiter = rate_limiter or RateLimiter()
        self.use_selenium = use_selenium
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        # Selenium driver (lazy initialization)
        self.driver = None
        
        # Cache for robots.txt
        self.robots_cache = {}
        
    def _init_selenium(self):
        """Initialize Selenium WebDriver."""
        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except:
                logging.warning("Chrome driver not found. Selenium features disabled.")
                self.use_selenium = False
    
    def check_robots_txt(self, url):
        """Check robots.txt compliance for URL."""
        try:
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            if domain not in self.robots_cache:
                robots_url = urljoin(domain, '/robots.txt')
                rp = RobotFileParser()
                rp.set_url(robots_url)
                rp.read()
                self.robots_cache[domain] = rp
            
            return self.robots_cache[domain].can_fetch('*', url)
        except:
            return True  # Allow if can't check robots.txt
    
    def scrape_url(self, url, scraping_config):
        """Scrape a single URL with given configuration."""
        try:
            # Check robots.txt compliance
            if not self.check_robots_txt(url):
                return {
                    'status': 'skipped',
                    'error': 'Robots.txt disallows crawling',
                    'data': None
                }
            
            # Check rate limiting
            domain = urlparse(url).netloc
            if not self.rate_limiter.is_allowed(domain):
                wait_time = self.rate_limiter.wait_time(domain)
                return {
                    'status': 'rate_limited',
                    'error': f'Rate limited. Wait {wait_time:.1f} seconds',
                    'data': None
                }
            
            # Random delay to be respectful
            delay = random.uniform(1, 3)
            time.sleep(delay)
            
            start_time = time.time()
            
            # Choose scraping method
            if scraping_config.get('use_selenium', False) and self.use_selenium:
                response_data = self._scrape_with_selenium(url, scraping_config)
            else:
                response_data = self._scrape_with_requests(url, scraping_config)
            
            execution_time = time.time() - start_time
            
            if response_data['status'] == 'success':
                # Extract data using rules
                extracted_data = self._extract_data(response_data['content'], scraping_config['extraction_rules'])
                
                return {
                    'status': 'success',
                    'data': extracted_data,
                    'execution_time': execution_time,
                    'response_code': response_data.get('status_code', 200)
                }
            else:
                return {
                    'status': 'failed',
                    'error': response_data['error'],
                    'execution_time': execution_time,
                    'response_code': response_data.get('status_code', 0)
                }
                
        except Exception as e:
            logging.error(f"Error scraping {url}: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'data': None
            }
    
    def _scrape_with_requests(self, url, config):
        """Scrape URL using requests library."""
        try:
            timeout = config.get('timeout', 30)
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            return {
                'status': 'success',
                'content': response.text,
                'status_code': response.status_code
            }
        except requests.RequestException as e:
            return {
                'status': 'failed',
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0
            }
    
    def _scrape_with_selenium(self, url, config):
        """Scrape URL using Selenium WebDriver."""
        try:
            if self.driver is None:
                self._init_selenium()
            
            if not self.use_selenium:
                return self._scrape_with_requests(url, config)
            
            timeout = config.get('timeout', 30)
            self.driver.get(url)
            
            # Wait for specific elements if configured
            if 'wait_for' in config:
                wait = WebDriverWait(self.driver, timeout)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, config['wait_for'])))
            
            # Handle infinite scroll if configured
            if config.get('infinite_scroll', False):
                self._handle_infinite_scroll()
            
            content = self.driver.page_source
            
            return {
                'status': 'success',
                'content': content,
                'status_code': 200
            }
        except TimeoutException:
            return {
                'status': 'failed',
                'error': 'Page load timeout',
                'status_code': 0
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'status_code': 0
            }
    
    def _handle_infinite_scroll(self):
        """Handle infinite scroll pages."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    def _extract_data(self, html_content, extraction_rules):
        """Extract data from HTML content using extraction rules."""
        soup = BeautifulSoup(html_content, 'html.parser')
        extracted_data = {}
        
        for field_name, rule in extraction_rules.items():
            try:
                if rule['type'] == 'css_selector':
                    elements = soup.select(rule['selector'])
                    
                    if rule.get('multiple', False):
                        extracted_data[field_name] = [self._extract_element_data(elem, rule) for elem in elements]
                    else:
                        extracted_data[field_name] = self._extract_element_data(elements[0], rule) if elements else None
                
                elif rule['type'] == 'xpath':
                    # XPath extraction would require additional library like lxml
                    extracted_data[field_name] = None
                
                elif rule['type'] == 'regex':
                    pattern = re.compile(rule['pattern'], re.IGNORECASE | re.DOTALL)
                    matches = pattern.findall(html_content)
                    
                    if rule.get('multiple', False):
                        extracted_data[field_name] = matches
                    else:
                        extracted_data[field_name] = matches[0] if matches else None
                
            except Exception as e:
                logging.error(f"Error extracting {field_name}: {e}")
                extracted_data[field_name] = None
        
        return extracted_data
    
    def _extract_element_data(self, element, rule):
        """Extract data from a single HTML element."""
        if rule.get('attribute'):
            return element.get(rule['attribute'])
        elif rule.get('text_only', True):
            return element.get_text(strip=True)
        else:
            return str(element)
    
    def close(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()

class DataProcessor:
    def __init__(self):
        """Initialize data processor for scraped data."""
        self.text_processors = {
            'clean': self._clean_text,
            'sentiment': self._analyze_sentiment,
            'keywords': self._extract_keywords,
            'length': lambda x: len(str(x)) if x else 0
        }
    
    def process_scraped_data(self, raw_data, processing_rules):
        """Process raw scraped data using processing rules."""
        processed_data = {}
        
        for field_name, value in raw_data.items():
            if field_name in processing_rules:
                processed_data[field_name] = self._apply_processing_rules(value, processing_rules[field_name])
            else:
                processed_data[field_name] = value
        
        # Add derived fields
        if 'derived_fields' in processing_rules:
            for derived_field, rule in processing_rules['derived_fields'].items():
                processed_data[derived_field] = self._calculate_derived_field(processed_data, rule)
        
        return processed_data
    
    def _apply_processing_rules(self, value, rules):
        """Apply processing rules to a field value."""
        processed_value = value
        
        for rule in rules:
            if rule['type'] == 'text_processing':
                if rule['method'] in self.text_processors:
                    processed_value = self.text_processors[rule['method']](processed_value)
            
            elif rule['type'] == 'data_type':
                processed_value = self._convert_data_type(processed_value, rule['target_type'])
            
            elif rule['type'] == 'validation':
                if not self._validate_data(processed_value, rule):
                    processed_value = rule.get('default', None)
            
            elif rule['type'] == 'transformation':
                processed_value = self._apply_transformation(processed_value, rule)
        
        return processed_value
    
    def _clean_text(self, text):
        """Clean text data."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', str(text)).strip()
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?]', '', text)
        
        return text
    
    def _analyze_sentiment(self, text):
        """Analyze sentiment of text."""
        try:
            blob = TextBlob(str(text))
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except:
            return {'polarity': 0, 'subjectivity': 0}
    
    def _extract_keywords(self, text):
        """Extract keywords from text."""
        try:
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            
            stop_words = set(stopwords.words('english'))
            words = word_tokenize(str(text).lower())
            keywords = [word for word in words if word.isalpha() and word not in stop_words and len(word) > 3]
            
            # Get top 10 most frequent keywords
            from collections import Counter
            return [word for word, count in Counter(keywords).most_common(10)]
        except:
            return []
    
    def _convert_data_type(self, value, target_type):
        """Convert value to target data type."""
        try:
            if target_type == 'int':
                return int(float(str(value)))
            elif target_type == 'float':
                return float(str(value))
            elif target_type == 'str':
                return str(value)
            elif target_type == 'bool':
                return bool(value)
            elif target_type == 'date':
                return pd.to_datetime(value)
        except:
            return None
        
        return value
    
    def _validate_data(self, value, rule):
        """Validate data against rule."""
        if rule['validation'] == 'required' and (value is None or value == ''):
            return False
        
        if rule['validation'] == 'min_length' and len(str(value)) < rule['threshold']:
            return False
        
        if rule['validation'] == 'max_length' and len(str(value)) > rule['threshold']:
            return False
        
        if rule['validation'] == 'pattern' and not re.match(rule['pattern'], str(value)):
            return False
        
        return True
    
    def _apply_transformation(self, value, rule):
        """Apply transformation to value."""
        if rule['transformation'] == 'lowercase':
            return str(value).lower()
        elif rule['transformation'] == 'uppercase':
            return str(value).upper()
        elif rule['transformation'] == 'title_case':
            return str(value).title()
        elif rule['transformation'] == 'remove_html':
            return BeautifulSoup(str(value), 'html.parser').get_text()
        
        return value
    
    def _calculate_derived_field(self, data, rule):
        """Calculate derived field from existing data."""
        if rule['type'] == 'concatenation':
            fields = rule['fields']
            separator = rule.get('separator', ' ')
            return separator.join([str(data.get(field, '')) for field in fields])
        
        elif rule['type'] == 'calculation':
            # Simple calculations (could be extended)
            if rule['operation'] == 'sum':
                return sum([float(data.get(field, 0)) for field in rule['fields']])
            elif rule['operation'] == 'average':
                values = [float(data.get(field, 0)) for field in rule['fields']]
                return sum(values) / len(values) if values else 0
        
        return None

class ScrapingScheduler:
    def __init__(self, scraper, db, data_processor):
        """Initialize scraping scheduler."""
        self.scraper = scraper
        self.db = db
        self.data_processor = data_processor
        self.active_jobs = {}
        self.running = False
    
    def start(self):
        """Start the scheduler."""
        self.running = True
        
        # Load scheduled projects from database
        self._load_scheduled_projects()
        
        # Start scheduler thread
        scheduler_thread = threading.Thread(target=self._run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        logging.info("Scraping scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        schedule.clear()
        logging.info("Scraping scheduler stopped")
    
    def _load_scheduled_projects(self):
        """Load scheduled projects from database."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, schedule_config FROM scraping_projects 
            WHERE is_active = 1 AND schedule_config IS NOT NULL
        ''')
        
        projects = cursor.fetchall()
        conn.close()
        
        for project_id, project_name, schedule_config in projects:
            self._schedule_project(project_id, project_name, json.loads(schedule_config))
    
    def _schedule_project(self, project_id, project_name, schedule_config):
        """Schedule a scraping project."""
        try:
            if schedule_config['type'] == 'interval':
                if schedule_config['unit'] == 'minutes':
                    schedule.every(schedule_config['value']).minutes.do(
                        self._run_scraping_project, project_id
                    )
                elif schedule_config['unit'] == 'hours':
                    schedule.every(schedule_config['value']).hours.do(
                        self._run_scraping_project, project_id
                    )
                elif schedule_config['unit'] == 'days':
                    schedule.every(schedule_config['value']).days.do(
                        self._run_scraping_project, project_id
                    )
            
            elif schedule_config['type'] == 'daily':
                schedule.every().day.at(schedule_config['time']).do(
                    self._run_scraping_project, project_id
                )
            
            elif schedule_config['type'] == 'weekly':
                getattr(schedule.every(), schedule_config['day'].lower()).at(
                    schedule_config['time']
                ).do(self._run_scraping_project, project_id)
            
            logging.info(f"Scheduled project: {project_name}")
            
        except Exception as e:
            logging.error(f"Error scheduling project {project_name}: {e}")
    
    def _run_scheduler(self):
        """Run the scheduler loop."""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _run_scraping_project(self, project_id):
        """Run a scraping project."""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Get project details
            cursor.execute('''
                SELECT name, target_urls, scraping_rules FROM scraping_projects 
                WHERE id = ? AND is_active = 1
            ''', (project_id,))
            
            project = cursor.fetchone()
            if not project:
                return
            
            project_name, target_urls, scraping_rules = project
            urls = json.loads(target_urls)
            rules = json.loads(scraping_rules)
            
            logging.info(f"Starting scheduled scraping: {project_name}")
            
            # Scrape each URL
            for url in urls:
                result = self.scraper.scrape_url(url, rules)
                
                # Log result
                cursor.execute('''
                    INSERT INTO scraping_logs (project_id, url, status, response_code, error_message, execution_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    project_id, url, result['status'],
                    result.get('response_code'), result.get('error'),
                    result.get('execution_time')
                ))
                
                # Save data if successful
                if result['status'] == 'success' and result['data']:
                    # Process data
                    if 'processing_rules' in rules:
                        processed_data = self.data_processor.process_scraped_data(
                            result['data'], rules['processing_rules']
                        )
                    else:
                        processed_data = result['data']
                    
                    # Create data hash for duplicate detection
                    data_str = json.dumps(result['data'], sort_keys=True)
                    data_hash = hashlib.md5(data_str.encode()).hexdigest()
                    
                    # Check for duplicates
                    cursor.execute(
                        'SELECT id FROM scraped_data WHERE project_id = ? AND data_hash = ?',
                        (project_id, data_hash)
                    )
                    
                    if not cursor.fetchone():
                        cursor.execute('''
                            INSERT INTO scraped_data (project_id, url, data_hash, raw_data, processed_data)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            project_id, url, data_hash,
                            json.dumps(result['data']),
                            json.dumps(processed_data)
                        ))
                    else:
                        cursor.execute('''
                            INSERT INTO scraping_logs (project_id, url, status, response_code, error_message)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (project_id, url, 'duplicate', 200, 'Duplicate data detected'))
            
            conn.commit()
            conn.close()
            
            logging.info(f"Completed scheduled scraping: {project_name}")
            
        except Exception as e:
            logging.error(f"Error in scheduled scraping for project {project_id}: {e}")

class ScrapingAnalyzer:
    def __init__(self, db):
        """Initialize scraping data analyzer."""
        self.db = db
    
    def generate_project_report(self, project_id, days_back=30):
        """Generate comprehensive report for a scraping project."""
        conn = sqlite3.connect(self.db.db_path)
        
        # Get project info
        project_info = pd.read_sql_query('''
            SELECT * FROM scraping_projects WHERE id = ?
        ''', conn, params=[project_id])
        
        if project_info.empty:
            conn.close()
            return None
        
        # Get scraping statistics
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        stats_query = '''
            SELECT 
                COUNT(*) as total_attempts,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_scrapes,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_scrapes,
                SUM(CASE WHEN status = 'rate_limited' THEN 1 ELSE 0 END) as rate_limited,
                AVG(execution_time) as avg_execution_time,
                MAX(execution_time) as max_execution_time
            FROM scraping_logs 
            WHERE project_id = ? AND timestamp >= ?
        '''
        
        stats = pd.read_sql_query(stats_query, conn, params=[project_id, start_date])
        
        # Get daily scraping trends
        daily_stats = pd.read_sql_query('''
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total_scrapes,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_scrapes,
                AVG(execution_time) as avg_time
            FROM scraping_logs 
            WHERE project_id = ? AND timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', conn, params=[project_id, start_date])
        
        # Get error analysis
        error_analysis = pd.read_sql_query('''
            SELECT 
                error_message,
                COUNT(*) as error_count,
                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM scraping_logs WHERE project_id = ?) as error_percentage
            FROM scraping_logs 
            WHERE project_id = ? AND status = 'failed' AND timestamp >= ?
            GROUP BY error_message
            ORDER BY error_count DESC
            LIMIT 10
        ''', conn, params=[project_id, project_id, start_date])
        
        # Get data quality metrics
        data_quality = pd.read_sql_query('''
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT data_hash) as unique_records,
                AVG(LENGTH(raw_data)) as avg_data_size
            FROM scraped_data 
            WHERE project_id = ? AND scraped_at >= ?
        ''', conn, params=[project_id, start_date])
        
        conn.close()
        
        # Calculate success rate
        success_rate = (stats.iloc[0]['successful_scrapes'] / stats.iloc[0]['total_attempts'] * 100) if stats.iloc[0]['total_attempts'] > 0 else 0
        
        return {
            'project_info': project_info.iloc[0].to_dict(),
            'summary_stats': {
                'total_attempts': int(stats.iloc[0]['total_attempts']),
                'successful_scrapes': int(stats.iloc[0]['successful_scrapes']),
                'failed_scrapes': int(stats.iloc[0]['failed_scrapes']),
                'success_rate': round(success_rate, 2),
                'avg_execution_time': round(stats.iloc[0]['avg_execution_time'] or 0, 3),
                'max_execution_time': round(stats.iloc[0]['max_execution_time'] or 0, 3)
            },
            'daily_trends': daily_stats.to_dict('records'),
            'error_analysis': error_analysis.to_dict('records'),
            'data_quality': data_quality.iloc[0].to_dict() if not data_quality.empty else {}
        }
    
    def export_data(self, project_id, format='csv', days_back=None):
        """Export scraped data in various formats."""
        conn = sqlite3.connect(self.db.db_path)
        
        query = '''
            SELECT sd.*, sp.name as project_name
            FROM scraped_data sd
            JOIN scraping_projects sp ON sd.project_id = sp.id
            WHERE sd.project_id = ?
        '''
        params = [project_id]
        
        if days_back:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            query += ' AND sd.scraped_at >= ?'
            params.append(cutoff_date)
        
        query += ' ORDER BY sd.scraped_at DESC'
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if df.empty:
            return None
        
        # Expand JSON data
        if 'processed_data' in df.columns:
            processed_data_list = []
            for _, row in df.iterrows():
                try:
                    processed_data = json.loads(row['processed_data']) if row['processed_data'] else {}
                    processed_data['scraped_at'] = row['scraped_at']
                    processed_data['url'] = row['url']
                    processed_data_list.append(processed_data)
                except:
                    pass
            
            if processed_data_list:
                expanded_df = pd.DataFrame(processed_data_list)
            else:
                expanded_df = df
        else:
            expanded_df = df
        
        # Export based on format
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        project_name = df.iloc[0]['project_name'].replace(' ', '_')
        
        if format == 'csv':
            filename = f"exports/{project_name}_{timestamp}.csv"
            Path("exports").mkdir(exist_ok=True)
            expanded_df.to_csv(filename, index=False)
        elif format == 'json':
            filename = f"exports/{project_name}_{timestamp}.json"
            Path("exports").mkdir(exist_ok=True)
            expanded_df.to_json(filename, orient='records', indent=2)
        elif format == 'excel':
            filename = f"exports/{project_name}_{timestamp}.xlsx"
            Path("exports").mkdir(exist_ok=True)
            expanded_df.to_excel(filename, index=False)
        
        # Save export record
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO exported_reports (project_id, report_type, file_path, record_count)
            VALUES (?, ?, ?, ?)
        ''', (project_id, format, filename, len(expanded_df)))
        conn.commit()
        conn.close()
        
        return filename

class ScrapingWebInterface:
    def __init__(self):
        """Initialize Flask web interface for scraping pipeline."""
        self.app = Flask(__name__)
        self.app.secret_key = 'scraping_pipeline_secret_2024'
        
        self.db = ScrapingDatabase()
        self.scraper = WebScraper()
        self.data_processor = DataProcessor()
        self.scheduler = ScrapingScheduler(self.scraper, self.db, self.data_processor)
        self.analyzer = ScrapingAnalyzer(self.db)
        
        self.setup_routes()
        
        # Start scheduler
        self.scheduler.start()
    
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def dashboard():
            return render_template('scraping_dashboard.html')
        
        @self.app.route('/projects')
        def projects():
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.*, 
                       (SELECT COUNT(*) FROM scraped_data WHERE project_id = p.id) as data_count,
                       (SELECT COUNT(*) FROM scraping_logs WHERE project_id = p.id AND timestamp > datetime('now', '-24 hours')) as last_24h_runs
                FROM scraping_projects p
                ORDER BY p.updated_at DESC
            ''')
            
            projects = cursor.fetchall()
            conn.close()
            
            return render_template('projects.html', projects=projects)
        
        @self.app.route('/project/<int:project_id>')
        def project_detail(project_id):
            report = self.analyzer.generate_project_report(project_id)
            return render_template('project_detail.html', project_id=project_id, report=report)
        
        @self.app.route('/create_project', methods=['GET', 'POST'])
        def create_project():
            if request.method == 'POST':
                data = request.form
                
                # Build scraping configuration
                scraping_config = {
                    'extraction_rules': {},
                    'use_selenium': 'use_selenium' in data,
                    'timeout': int(data.get('timeout', 30))
                }
                
                # Add extraction rules (simplified for demo)
                if data.get('css_selector'):
                    scraping_config['extraction_rules']['main_content'] = {
                        'type': 'css_selector',
                        'selector': data['css_selector'],
                        'text_only': True
                    }
                
                # Save to database
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO scraping_projects (name, description, target_urls, scraping_rules)
                    VALUES (?, ?, ?, ?)
                ''', (
                    data['name'],
                    data['description'],
                    json.dumps([url.strip() for url in data['urls'].split('\n') if url.strip()]),
                    json.dumps(scraping_config)
                ))
                
                conn.commit()
                conn.close()
                
                flash('Project created successfully!')
                return redirect(url_for('projects'))
            
            return render_template('create_project.html')
        
        @self.app.route('/run_project/<int:project_id>')
        def run_project(project_id):
            try:
                self.scheduler._run_scraping_project(project_id)
                flash('Project executed successfully!')
            except Exception as e:
                flash(f'Error running project: {str(e)}')
            
            return redirect(url_for('project_detail', project_id=project_id))
        
        @self.app.route('/export_data/<int:project_id>/<format>')
        def export_data(project_id, format):
            try:
                filename = self.analyzer.export_data(project_id, format)
                if filename:
                    flash(f'Data exported successfully: {filename}')
                else:
                    flash('No data to export')
            except Exception as e:
                flash(f'Export failed: {str(e)}')
            
            return redirect(url_for('project_detail', project_id=project_id))
        
        @self.app.route('/api/project_stats/<int:project_id>')
        def api_project_stats(project_id):
            report = self.analyzer.generate_project_report(project_id)
            return jsonify(report)
    
    def create_templates(self):
        """Create HTML templates."""
        template_dir = 'templates'
        os.makedirs(template_dir, exist_ok=True)
        
        # Dashboard template (simplified)
        dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Scraping Pipeline</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 100px 0; }
        .feature-card { height: 100%; transition: transform 0.3s; }
        .feature-card:hover { transform: translateY(-5px); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-spider"></i> Web Scraping Pipeline</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/projects">Projects</a>
                <a class="nav-link" href="/create_project">Create Project</a>
            </div>
        </div>
    </nav>

    <section class="hero text-center">
        <div class="container">
            <h1 class="display-4 mb-4">Web Scraping Pipeline</h1>
            <p class="lead mb-4">Automated data extraction with scheduling, monitoring, and analytics</p>
            <a href="/create_project" class="btn btn-light btn-lg">
                <i class="fas fa-plus"></i> Create New Project
            </a>
        </div>
    </section>

    <div class="container py-5">
        <div class="row">
            <div class="col-md-4 mb-4">
                <div class="card feature-card">
                    <div class="card-body text-center">
                        <i class="fas fa-clock fa-3x text-primary mb-3"></i>
                        <h5>Scheduled Scraping</h5>
                        <p>Automate data collection with flexible scheduling options</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card feature-card">
                    <div class="card-body text-center">
                        <i class="fas fa-chart-line fa-3x text-success mb-3"></i>
                        <h5>Data Analytics</h5>
                        <p>Comprehensive analytics and reporting for scraped data</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-4">
                <div class="card feature-card">
                    <div class="card-body text-center">
                        <i class="fas fa-shield-alt fa-3x text-info mb-3"></i>
                        <h5>Rate Limiting</h5>
                        <p>Respectful scraping with built-in rate limiting and robots.txt compliance</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        '''
        
        with open(os.path.join(template_dir, 'scraping_dashboard.html'), 'w') as f:
            f.write(dashboard_html)
    
    def run(self, host='localhost', port=5000, debug=True):
        """Run the scraping web interface."""
        self.create_templates()
        
        print("🕷️ Web Scraping Pipeline")
        print("=" * 50)
        print(f"🚀 Starting scraping platform...")
        print(f"🌐 Access the dashboard at: http://{host}:{port}")
        print("\n🔥 Scraping Features:")
        print("   - Multi-site data extraction")
        print("   - Automated scheduling and monitoring")
        print("   - Rate limiting and robots.txt compliance")
        print("   - Data validation and processing")
        print("   - Export in multiple formats")
        print("   - Comprehensive analytics and reporting")
        print("   - Web interface for easy management")
        
        try:
            self.app.run(host=host, port=port, debug=debug)
        finally:
            self.scheduler.stop()
            self.scraper.close()

def main():
    """Main function to run the web scraping pipeline."""
    print("🕷️ Web Scraping Pipeline")
    print("=" * 50)
    
    choice = input("\nChoose interface:\n1. Web Interface\n2. CLI Demo\nEnter choice (1-2): ")
    
    if choice == '2':
        # CLI demo
        print("\n🕷️ Web Scraping Pipeline - CLI Demo")
        print("Creating sample scraping project...")
        
        # Initialize components
        db = ScrapingDatabase()
        scraper = WebScraper()
        data_processor = DataProcessor()
        
        # Demo scraping configuration
        scraping_config = {
            'extraction_rules': {
                'title': {
                    'type': 'css_selector',
                    'selector': 'title',
                    'text_only': True
                },
                'headings': {
                    'type': 'css_selector',
                    'selector': 'h1, h2, h3',
                    'text_only': True,
                    'multiple': True
                }
            },
            'use_selenium': False,
            'timeout': 30
        }
        
        # Test URLs
        test_urls = [
            'https://httpbin.org/html',
            'https://example.com'
        ]
        
        print("🏃 Running demo scraping...")
        for url in test_urls:
            print(f"Scraping: {url}")
            result = scraper.scrape_url(url, scraping_config)
            
            if result['status'] == 'success':
                print(f"  ✅ Success: {len(str(result['data']))} characters extracted")
                print(f"  📊 Data: {result['data']}")
            else:
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
        
        print("\n✅ Demo completed!")
        scraper.close()
    
    else:
        # Run web interface
        app = ScrapingWebInterface()
        app.run()

if __name__ == "__main__":
    main()
