import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json
import datetime
from datetime import timedelta
import random
from flask import Flask, render_template, request, jsonify, session
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class EcommerceAnalytics:
    def __init__(self, db_path="ecommerce_analytics.db"):
        """Initialize the E-commerce Analytics platform."""
        self.db_path = db_path
        self.init_database()
        self.generate_sample_data()
        
    def init_database(self):
        """Create database tables for e-commerce analytics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT,
                country TEXT,
                city TEXT,
                postal_code TEXT,
                registration_date DATE NOT NULL,
                total_spent REAL DEFAULT 0,
                total_orders INTEGER DEFAULT 0,
                customer_lifetime_value REAL DEFAULT 0,
                acquisition_channel TEXT,
                segment TEXT,
                last_purchase_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                brand TEXT,
                price REAL NOT NULL,
                cost REAL NOT NULL,
                stock_quantity INTEGER DEFAULT 0,
                weight REAL,
                dimensions TEXT,
                description TEXT,
                sku TEXT UNIQUE,
                status TEXT CHECK(status IN ('active', 'discontinued', 'out_of_stock')) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                order_date DATETIME NOT NULL,
                status TEXT CHECK(status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'returned')) DEFAULT 'pending',
                total_amount REAL NOT NULL,
                shipping_cost REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                payment_method TEXT,
                shipping_address TEXT,
                tracking_number TEXT,
                delivery_date DATETIME,
                refund_amount REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        
        # Order items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                discount_applied REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Website sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                session_id TEXT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                page_views INTEGER DEFAULT 0,
                duration_minutes REAL DEFAULT 0,
                source TEXT,
                medium TEXT,
                campaign TEXT,
                device_type TEXT,
                browser TEXT,
                country TEXT,
                converted BOOLEAN DEFAULT 0,
                conversion_value REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        
        # Product views table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                view_timestamp DATETIME NOT NULL,
                time_spent_seconds INTEGER DEFAULT 0,
                from_search BOOLEAN DEFAULT 0,
                search_term TEXT,
                added_to_cart BOOLEAN DEFAULT 0,
                purchased BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Marketing campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                budget REAL NOT NULL,
                spent REAL DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0,
                target_audience TEXT,
                channels TEXT,
                status TEXT CHECK(status IN ('active', 'paused', 'completed')) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Inventory movements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                movement_type TEXT CHECK(movement_type IN ('in', 'out', 'adjustment')) NOT NULL,
                quantity INTEGER NOT NULL,
                reason TEXT,
                reference_order_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (reference_order_id) REFERENCES orders (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_sample_data(self):
        """Generate comprehensive sample data for demonstration."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM customers")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        print("🔄 Generating sample e-commerce data...")
        
        # Generate customers
        countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Australia', 'Japan', 'Brazil']
        channels = ['organic', 'paid_search', 'social_media', 'email', 'direct', 'referral']
        
        customers_data = []
        for i in range(1000):
            email = f"customer{i}@email.com"
            first_name = f"Customer{i}"
            last_name = f"Last{i}"
            country = random.choice(countries)
            channel = random.choice(channels)
            registration_date = datetime.date.today() - timedelta(days=random.randint(1, 730))
            
            customers_data.append((
                email, first_name, last_name, f"+1234567{i:04d}", country,
                f"City{i}", f"{random.randint(10000, 99999)}", registration_date,
                0, 0, 0, channel, 'new', None
            ))
        
        cursor.executemany('''
            INSERT INTO customers (email, first_name, last_name, phone, country, city, 
                                 postal_code, registration_date, total_spent, total_orders,
                                 customer_lifetime_value, acquisition_channel, segment, last_purchase_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', customers_data)
        
        # Generate products
        categories = [
            ('Electronics', ['Smartphones', 'Laptops', 'Tablets', 'Accessories']),
            ('Clothing', ['Men', 'Women', 'Kids', 'Shoes']),
            ('Home & Garden', ['Furniture', 'Decor', 'Kitchen', 'Garden']),
            ('Books', ['Fiction', 'Non-fiction', 'Educational', 'Comics']),
            ('Sports', ['Fitness', 'Outdoor', 'Team Sports', 'Water Sports'])
        ]
        
        brands = ['BrandA', 'BrandB', 'BrandC', 'BrandD', 'BrandE']
        
        products_data = []
        for i in range(500):
            category, subcats = random.choice(categories)
            subcategory = random.choice(subcats)
            brand = random.choice(brands)
            price = round(random.uniform(10, 1000), 2)
            cost = round(price * random.uniform(0.3, 0.7), 2)
            stock = random.randint(0, 1000)
            
            products_data.append((
                f"Product {i}", category, subcategory, brand, price, cost, stock,
                round(random.uniform(0.1, 5.0), 2), f"{random.randint(10, 50)}x{random.randint(10, 50)}x{random.randint(5, 20)}cm",
                f"Description for product {i}", f"SKU{i:06d}", 'active'
            ))
        
        cursor.executemany('''
            INSERT INTO products (name, category, subcategory, brand, price, cost, stock_quantity,
                                weight, dimensions, description, sku, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', products_data)
        
        # Generate orders and order items
        statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        payment_methods = ['credit_card', 'paypal', 'bank_transfer', 'cash_on_delivery']
        
        for i in range(2000):
            customer_id = random.randint(1, 1000)
            order_date = datetime.datetime.now() - timedelta(days=random.randint(1, 365))
            status = random.choice(statuses)
            payment_method = random.choice(payment_methods)
            
            # Generate order items
            num_items = random.randint(1, 5)
            total_amount = 0
            order_items = []
            
            for _ in range(num_items):
                product_id = random.randint(1, 500)
                quantity = random.randint(1, 3)
                
                # Get product price
                cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
                unit_price = cursor.fetchone()[0]
                total_price = unit_price * quantity
                total_amount += total_price
                
                order_items.append((product_id, quantity, unit_price, total_price))
            
            shipping_cost = round(random.uniform(5, 25), 2)
            tax_amount = round(total_amount * 0.08, 2)
            discount_amount = round(total_amount * random.uniform(0, 0.2), 2)
            final_total = total_amount + shipping_cost + tax_amount - discount_amount
            
            # Insert order
            cursor.execute('''
                INSERT INTO orders (customer_id, order_date, status, total_amount, shipping_cost,
                                  tax_amount, discount_amount, payment_method, shipping_address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (customer_id, order_date, status, final_total, shipping_cost, tax_amount,
                  discount_amount, payment_method, f"Address for customer {customer_id}"))
            
            order_id = cursor.lastrowid
            
            # Insert order items
            for product_id, quantity, unit_price, total_price in order_items:
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
                    VALUES (?, ?, ?, ?, ?)
                ''', (order_id, product_id, quantity, unit_price, total_price))
        
        # Generate website sessions
        sources = ['google', 'facebook', 'instagram', 'email', 'direct', 'referral']
        devices = ['desktop', 'mobile', 'tablet']
        browsers = ['chrome', 'firefox', 'safari', 'edge']
        
        for i in range(5000):
            customer_id = random.randint(1, 1000) if random.random() > 0.3 else None
            session_id = f"session_{i}"
            start_time = datetime.datetime.now() - timedelta(days=random.randint(1, 90))
            duration = random.uniform(1, 60)
            end_time = start_time + timedelta(minutes=duration)
            page_views = random.randint(1, 20)
            converted = random.random() > 0.85
            conversion_value = random.uniform(50, 500) if converted else 0
            
            cursor.execute('''
                INSERT INTO sessions (customer_id, session_id, start_time, end_time, page_views,
                                    duration_minutes, source, medium, device_type, browser, country,
                                    converted, conversion_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (customer_id, session_id, start_time, end_time, page_views, duration,
                  random.choice(sources), 'organic', random.choice(devices),
                  random.choice(browsers), random.choice(countries), converted, conversion_value))
        
        # Update customer totals
        cursor.execute('''
            UPDATE customers 
            SET total_spent = (
                SELECT COALESCE(SUM(total_amount), 0) 
                FROM orders 
                WHERE customer_id = customers.id AND status = 'delivered'
            ),
            total_orders = (
                SELECT COUNT(*) 
                FROM orders 
                WHERE customer_id = customers.id
            ),
            last_purchase_date = (
                SELECT MAX(order_date) 
                FROM orders 
                WHERE customer_id = customers.id
            )
        ''')
        
        # Calculate CLV
        cursor.execute('''
            UPDATE customers 
            SET customer_lifetime_value = total_spent * 1.5
            WHERE total_spent > 0
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Sample data generation completed")
    
    def get_sales_overview(self, days=30):
        """Get sales overview and key metrics."""
        conn = sqlite3.connect(self.db_path)
        
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=days)
        
        # Current period metrics
        current_query = '''
            SELECT 
                COUNT(*) as total_orders,
                COALESCE(SUM(total_amount), 0) as total_revenue,
                COALESCE(AVG(total_amount), 0) as avg_order_value,
                COUNT(DISTINCT customer_id) as unique_customers
            FROM orders 
            WHERE DATE(order_date) BETWEEN ? AND ?
        '''
        
        current_df = pd.read_sql_query(current_query, conn, params=[start_date, end_date])
        
        # Previous period for comparison
        prev_start = start_date - timedelta(days=days)
        prev_end = start_date - timedelta(days=1)
        
        prev_df = pd.read_sql_query(current_query, conn, params=[prev_start, prev_end])
        
        # Daily sales trend
        daily_query = '''
            SELECT 
                DATE(order_date) as date,
                COUNT(*) as orders,
                SUM(total_amount) as revenue
            FROM orders 
            WHERE DATE(order_date) BETWEEN ? AND ?
            GROUP BY DATE(order_date)
            ORDER BY date
        '''
        
        daily_df = pd.read_sql_query(daily_query, conn, params=[start_date, end_date])
        
        conn.close()
        
        # Calculate growth rates
        current = current_df.iloc[0]
        previous = prev_df.iloc[0]
        
        growth_rates = {}
        for metric in ['total_orders', 'total_revenue', 'avg_order_value', 'unique_customers']:
            if previous[metric] > 0:
                growth_rates[f"{metric}_growth"] = ((current[metric] - previous[metric]) / previous[metric]) * 100
            else:
                growth_rates[f"{metric}_growth"] = 0
        
        return {
            'current_metrics': current.to_dict(),
            'growth_rates': growth_rates,
            'daily_trend': daily_df.to_dict('records')
        }
    
    def analyze_customer_segments(self):
        """Perform customer segmentation analysis using RFM analysis."""
        conn = sqlite3.connect(self.db_path)
        
        # RFM Analysis query
        rfm_query = '''
            SELECT 
                c.id as customer_id,
                c.email,
                c.total_spent,
                c.total_orders,
                julianday('now') - julianday(MAX(o.order_date)) as recency_days,
                COUNT(o.id) as frequency,
                AVG(o.total_amount) as avg_order_value
            FROM customers c
            LEFT JOIN orders o ON c.id = o.customer_id
            WHERE c.total_orders > 0
            GROUP BY c.id, c.email, c.total_spent, c.total_orders
        '''
        
        df = pd.read_sql_query(rfm_query, conn)
        conn.close()
        
        if df.empty:
            return {}
        
        # Calculate RFM scores
        df['recency_score'] = pd.qcut(df['recency_days'], 5, labels=[5,4,3,2,1])
        df['frequency_score'] = pd.qcut(df['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
        df['monetary_score'] = pd.qcut(df['total_spent'], 5, labels=[1,2,3,4,5])
        
        # Convert to numeric
        df['recency_score'] = df['recency_score'].astype(int)
        df['frequency_score'] = df['frequency_score'].astype(int)
        df['monetary_score'] = df['monetary_score'].astype(int)
        
        # Define customer segments
        def segment_customers(row):
            if row['recency_score'] >= 4 and row['frequency_score'] >= 4:
                return 'Champions'
            elif row['recency_score'] >= 3 and row['frequency_score'] >= 3:
                return 'Loyal Customers'
            elif row['recency_score'] >= 4 and row['frequency_score'] <= 2:
                return 'New Customers'
            elif row['recency_score'] <= 2 and row['frequency_score'] >= 4:
                return 'At Risk'
            elif row['recency_score'] <= 2 and row['frequency_score'] <= 2:
                return 'Lost Customers'
            else:
                return 'Regular Customers'
        
        df['segment'] = df.apply(segment_customers, axis=1)
        
        # Segment summary
        segment_summary = df.groupby('segment').agg({
            'customer_id': 'count',
            'total_spent': 'mean',
            'frequency': 'mean',
            'recency_days': 'mean'
        }).round(2)
        
        # Customer Lifetime Value distribution
        clv_stats = {
            'high_value': len(df[df['total_spent'] >= df['total_spent'].quantile(0.8)]),
            'medium_value': len(df[(df['total_spent'] >= df['total_spent'].quantile(0.5)) & 
                                 (df['total_spent'] < df['total_spent'].quantile(0.8))]),
            'low_value': len(df[df['total_spent'] < df['total_spent'].quantile(0.5)])
        }
        
        return {
            'segment_summary': segment_summary.to_dict(),
            'segment_distribution': df['segment'].value_counts().to_dict(),
            'clv_distribution': clv_stats,
            'rfm_data': df[['customer_id', 'email', 'segment', 'recency_score', 
                           'frequency_score', 'monetary_score']].to_dict('records')
        }
    
    def analyze_product_performance(self, days=30):
        """Analyze product performance and inventory metrics."""
        conn = sqlite3.connect(self.db_path)
        
        end_date = datetime.date.today()
        start_date = end_date - timedelta(days=days)
        
        # Product performance query
        performance_query = '''
            SELECT 
                p.id,
                p.name,
                p.category,
                p.brand,
                p.price,
                p.cost,
                p.stock_quantity,
                COALESCE(SUM(oi.quantity), 0) as units_sold,
                COALESCE(SUM(oi.total_price), 0) as revenue,
                COALESCE(SUM(oi.total_price - (p.cost * oi.quantity)), 0) as profit,
                COALESCE(COUNT(DISTINCT o.customer_id), 0) as unique_buyers
            FROM products p
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id
            WHERE o.order_date IS NULL OR DATE(o.order_date) BETWEEN ? AND ?
            GROUP BY p.id, p.name, p.category, p.brand, p.price, p.cost, p.stock_quantity
        '''
        
        df = pd.read_sql_query(performance_query, conn, params=[start_date, end_date])
        
        # Calculate metrics
        df['profit_margin'] = np.where(df['revenue'] > 0, (df['profit'] / df['revenue']) * 100, 0)
        df['inventory_turnover'] = np.where(df['stock_quantity'] > 0, df['units_sold'] / df['stock_quantity'], 0)
        
        # Category performance
        category_performance = df.groupby('category').agg({
            'revenue': 'sum',
            'units_sold': 'sum',
            'profit': 'sum',
            'unique_buyers': 'sum'
        }).round(2)
        
        # Top performing products
        top_products = df.nlargest(10, 'revenue')[['name', 'category', 'revenue', 'units_sold', 'profit_margin']]
        
        # Low stock alerts
        low_stock = df[df['stock_quantity'] <= 10][['name', 'category', 'stock_quantity', 'units_sold']]
        
        # Slow moving inventory
        slow_moving = df[(df['units_sold'] == 0) & (df['stock_quantity'] > 0)][['name', 'category', 'stock_quantity']]
        
        conn.close()
        
        return {
            'category_performance': category_performance.to_dict(),
            'top_products': top_products.to_dict('records'),
            'low_stock_alerts': low_stock.to_dict('records'),
            'slow_moving_inventory': slow_moving.to_dict('records'),
            'performance_metrics': {
                'total_products': len(df),
                'products_sold': len(df[df['units_sold'] > 0]),
                'avg_profit_margin': df[df['revenue'] > 0]['profit_margin'].mean(),
                'total_inventory_value': (df['stock_quantity'] * df['cost']).sum()
            }
        }
    
    def analyze_marketing_effectiveness(self):
        """Analyze marketing campaigns and channel performance."""
        conn = sqlite3.connect(self.db_path)
        
        # Channel performance
        channel_query = '''
            SELECT 
                c.acquisition_channel,
                COUNT(*) as customers,
                SUM(c.total_spent) as total_revenue,
                AVG(c.total_spent) as avg_clv,
                AVG(c.total_orders) as avg_orders
            FROM customers c
            WHERE c.acquisition_channel IS NOT NULL
            GROUP BY c.acquisition_channel
        '''
        
        channel_df = pd.read_sql_query(channel_query, conn)
        
        # Session conversion analysis
        conversion_query = '''
            SELECT 
                source,
                device_type,
                COUNT(*) as total_sessions,
                SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) as conversions,
                AVG(duration_minutes) as avg_session_duration,
                AVG(page_views) as avg_page_views,
                SUM(conversion_value) as total_conversion_value
            FROM sessions
            GROUP BY source, device_type
        '''
        
        conversion_df = pd.read_sql_query(conversion_query, conn)
        conversion_df['conversion_rate'] = (conversion_df['conversions'] / conversion_df['total_sessions']) * 100
        
        # Traffic sources over time
        traffic_query = '''
            SELECT 
                DATE(start_time) as date,
                source,
                COUNT(*) as sessions,
                SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) as conversions
            FROM sessions
            WHERE DATE(start_time) >= date('now', '-30 days')
            GROUP BY DATE(start_time), source
            ORDER BY date
        '''
        
        traffic_df = pd.read_sql_query(traffic_query, conn)
        
        conn.close()
        
        return {
            'channel_performance': channel_df.to_dict('records'),
            'conversion_analysis': conversion_df.to_dict('records'),
            'traffic_trends': traffic_df.to_dict('records'),
            'summary_metrics': {
                'best_channel': channel_df.loc[channel_df['total_revenue'].idxmax(), 'acquisition_channel'] if not channel_df.empty else None,
                'best_converting_source': conversion_df.loc[conversion_df['conversion_rate'].idxmax(), 'source'] if not conversion_df.empty else None,
                'overall_conversion_rate': conversion_df['conversions'].sum() / conversion_df['total_sessions'].sum() * 100 if not conversion_df.empty else 0
            }
        }
    
    def predict_sales_forecast(self, days_ahead=30):
        """Use machine learning to predict future sales."""
        conn = sqlite3.connect(self.db_path)
        
        # Get historical daily sales data
        query = '''
            SELECT 
                DATE(order_date) as date,
                COUNT(*) as orders,
                SUM(total_amount) as revenue,
                COUNT(DISTINCT customer_id) as unique_customers,
                AVG(total_amount) as avg_order_value
            FROM orders
            WHERE DATE(order_date) >= date('now', '-365 days')
            GROUP BY DATE(order_date)
            ORDER BY date
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(df) < 30:
            return {'error': 'Insufficient data for forecasting'}
        
        # Prepare features
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['week_of_year'] = df['date'].dt.week
        
        # Create lag features
        df['revenue_lag_1'] = df['revenue'].shift(1)
        df['revenue_lag_7'] = df['revenue'].shift(7)
        df['orders_lag_1'] = df['orders'].shift(1)
        df['orders_lag_7'] = df['orders'].shift(7)
        
        # Moving averages
        df['revenue_ma_7'] = df['revenue'].rolling(window=7).mean()
        df['orders_ma_7'] = df['orders'].rolling(window=7).mean()
        
        # Drop rows with NaN values
        df = df.dropna()
        
        if len(df) < 20:
            return {'error': 'Insufficient clean data for forecasting'}
        
        # Prepare features and targets
        feature_columns = ['day_of_week', 'day_of_month', 'month', 'week_of_year', 
                          'revenue_lag_1', 'revenue_lag_7', 'orders_lag_1', 'orders_lag_7',
                          'revenue_ma_7', 'orders_ma_7']
        
        X = df[feature_columns]
        y_revenue = df['revenue']
        y_orders = df['orders']
        
        # Train models
        try:
            # Revenue prediction model
            X_train, X_test, y_train, y_test = train_test_split(X, y_revenue, test_size=0.2, random_state=42)
            revenue_model = RandomForestRegressor(n_estimators=100, random_state=42)
            revenue_model.fit(X_train, y_train)
            
            # Orders prediction model
            orders_model = RandomForestRegressor(n_estimators=100, random_state=42)
            orders_model.fit(X_train, y_orders.loc[X_train.index])
            
            # Model performance
            revenue_pred = revenue_model.predict(X_test)
            revenue_mae = mean_absolute_error(y_test, revenue_pred)
            revenue_r2 = r2_score(y_test, revenue_pred)
            
            # Generate future predictions
            last_date = df['date'].max()
            future_dates = [last_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
            
            predictions = []
            
            for future_date in future_dates:
                # Create features for prediction
                future_features = {
                    'day_of_week': future_date.weekday(),
                    'day_of_month': future_date.day,
                    'month': future_date.month,
                    'week_of_year': future_date.isocalendar()[1],
                    'revenue_lag_1': df['revenue'].iloc[-1],
                    'revenue_lag_7': df['revenue'].iloc[-7],
                    'orders_lag_1': df['orders'].iloc[-1],
                    'orders_lag_7': df['orders'].iloc[-7],
                    'revenue_ma_7': df['revenue'].tail(7).mean(),
                    'orders_ma_7': df['orders'].tail(7).mean()
                }
                
                future_X = pd.DataFrame([future_features])
                
                pred_revenue = revenue_model.predict(future_X)[0]
                pred_orders = orders_model.predict(future_X)[0]
                
                predictions.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'predicted_revenue': round(pred_revenue, 2),
                    'predicted_orders': round(pred_orders)
                })
            
            return {
                'predictions': predictions,
                'model_performance': {
                    'revenue_mae': round(revenue_mae, 2),
                    'revenue_r2': round(revenue_r2, 3)
                },
                'summary': {
                    'total_predicted_revenue': sum(p['predicted_revenue'] for p in predictions),
                    'total_predicted_orders': sum(p['predicted_orders'] for p in predictions),
                    'avg_daily_revenue': sum(p['predicted_revenue'] for p in predictions) / len(predictions)
                }
            }
            
        except Exception as e:
            return {'error': f'Forecasting error: {str(e)}'}
    
    def get_cohort_analysis(self):
        """Perform cohort analysis to understand customer retention."""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                c.id as customer_id,
                c.registration_date,
                o.order_date,
                o.total_amount
            FROM customers c
            JOIN orders o ON c.id = o.customer_id
            WHERE o.status = 'delivered'
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return {}
        
        # Convert dates
        df['registration_date'] = pd.to_datetime(df['registration_date'])
        df['order_date'] = pd.to_datetime(df['order_date'])
        
        # Create cohort groups
        df['registration_month'] = df['registration_date'].dt.to_period('M')
        df['order_month'] = df['order_date'].dt.to_period('M')
        
        # Calculate period number
        df['period_number'] = (df['order_month'] - df['registration_month']).apply(attrgetter('n'))
        
        # Create cohort table
        cohort_data = df.groupby(['registration_month', 'period_number'])['customer_id'].nunique().reset_index()
        cohort_table = cohort_data.pivot(index='registration_month', 
                                        columns='period_number', 
                                        values='customer_id')
        
        # Calculate cohort sizes
        cohort_sizes = df.groupby('registration_month')['customer_id'].nunique()
        
        # Calculate retention rates
        cohort_table_pct = cohort_table.divide(cohort_sizes, axis=0)
        
        return {
            'cohort_table': cohort_table.fillna(0).to_dict(),
            'retention_rates': cohort_table_pct.fillna(0).to_dict(),
            'cohort_sizes': cohort_sizes.to_dict()
        }

class EcommerceDashboard:
    def __init__(self):
        """Initialize the Flask dashboard application."""
        self.app = Flask(__name__)
        self.app.secret_key = 'ecommerce_analytics_secret_2024'
        self.analytics = EcommerceAnalytics()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup Flask routes for the dashboard."""
        
        @self.app.route('/')
        def dashboard():
            return render_template('ecommerce_dashboard.html')
        
        @self.app.route('/api/sales-overview')
        def api_sales_overview():
            days = request.args.get('days', 30, type=int)
            data = self.analytics.get_sales_overview(days)
            return jsonify(data)
        
        @self.app.route('/api/customer-segments')
        def api_customer_segments():
            data = self.analytics.analyze_customer_segments()
            return jsonify(data)
        
        @self.app.route('/api/product-performance')
        def api_product_performance():
            days = request.args.get('days', 30, type=int)
            data = self.analytics.analyze_product_performance(days)
            return jsonify(data)
        
        @self.app.route('/api/marketing-effectiveness')
        def api_marketing_effectiveness():
            data = self.analytics.analyze_marketing_effectiveness()
            return jsonify(data)
        
        @self.app.route('/api/sales-forecast')
        def api_sales_forecast():
            days = request.args.get('days', 30, type=int)
            data = self.analytics.predict_sales_forecast(days)
            return jsonify(data)
        
        @self.app.route('/api/cohort-analysis')
        def api_cohort_analysis():
            data = self.analytics.get_cohort_analysis()
            return jsonify(data)
        
        @self.app.route('/api/charts/sales-trend')
        def api_sales_trend_chart():
            overview = self.analytics.get_sales_overview(30)
            
            fig = px.line(x=[d['date'] for d in overview['daily_trend']],
                         y=[d['revenue'] for d in overview['daily_trend']],
                         title='Daily Revenue Trend')
            
            return json.dumps(fig, cls=PlotlyJSONEncoder)
        
        @self.app.route('/api/charts/customer-segments')
        def api_customer_segments_chart():
            segments = self.analytics.analyze_customer_segments()
            
            if 'segment_distribution' in segments:
                fig = px.pie(values=list(segments['segment_distribution'].values()),
                           names=list(segments['segment_distribution'].keys()),
                           title='Customer Segments Distribution')
                
                return json.dumps(fig, cls=PlotlyJSONEncoder)
            
            return jsonify({'error': 'No segment data available'})
    
    def create_dashboard_template(self):
        """Create the HTML template for the dashboard."""
        import os
        template_dir = 'templates'
        os.makedirs(template_dir, exist_ok=True)
        
        html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-commerce Analytics Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .metric-number { font-size: 2rem; font-weight: bold; }
        .chart-container { height: 400px; }
        .growth-positive { color: #28a745; }
        .growth-negative { color: #dc3545; }
        .table-container { max-height: 400px; overflow-y: auto; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-chart-bar"></i> E-commerce Analytics Dashboard
            </span>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- Key Metrics Row -->
        <div class="row mb-4" id="metrics-row">
            <!-- Metrics will be populated by JavaScript -->
        </div>

        <!-- Charts Row -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-line"></i> Sales Trend</h5>
                    </div>
                    <div class="card-body">
                        <div id="sales-trend-chart" class="chart-container"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-users"></i> Customer Segments</h5>
                    </div>
                    <div class="card-body">
                        <div id="customer-segments-chart" class="chart-container"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Analysis Tabs -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <ul class="nav nav-tabs card-header-tabs" id="analysisTab" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="products-tab" data-bs-toggle="tab" 
                                        data-bs-target="#products" type="button" role="tab">
                                    <i class="fas fa-box"></i> Products
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="marketing-tab" data-bs-toggle="tab" 
                                        data-bs-target="#marketing" type="button" role="tab">
                                    <i class="fas fa-bullhorn"></i> Marketing
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="forecast-tab" data-bs-toggle="tab" 
                                        data-bs-target="#forecast" type="button" role="tab">
                                    <i class="fas fa-crystal-ball"></i> Forecast
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="cohort-tab" data-bs-toggle="tab" 
                                        data-bs-target="#cohort" type="button" role="tab">
                                    <i class="fas fa-layer-group"></i> Cohort Analysis
                                </button>
                            </li>
                        </ul>
                    </div>
                    <div class="card-body">
                        <div class="tab-content" id="analysisTabContent">
                            <!-- Products Tab -->
                            <div class="tab-pane fade show active" id="products" role="tabpanel">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Top Performing Products</h6>
                                        <div class="table-container">
                                            <table class="table table-sm" id="top-products-table">
                                                <thead>
                                                    <tr>
                                                        <th>Product</th>
                                                        <th>Revenue</th>
                                                        <th>Units Sold</th>
                                                        <th>Margin %</th>
                                                    </tr>
                                                </thead>
                                                <tbody></tbody>
                                            </table>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Inventory Alerts</h6>
                                        <div id="inventory-alerts"></div>
                                    </div>
                                </div>
                            </div>

                            <!-- Marketing Tab -->
                            <div class="tab-pane fade" id="marketing" role="tabpanel">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Channel Performance</h6>
                                        <div class="table-container">
                                            <table class="table table-sm" id="channel-performance-table">
                                                <thead>
                                                    <tr>
                                                        <th>Channel</th>
                                                        <th>Customers</th>
                                                        <th>Revenue</th>
                                                        <th>Avg CLV</th>
                                                    </tr>
                                                </thead>
                                                <tbody></tbody>
                                            </table>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Conversion Analysis</h6>
                                        <div class="table-container">
                                            <table class="table table-sm" id="conversion-table">
                                                <thead>
                                                    <tr>
                                                        <th>Source</th>
                                                        <th>Sessions</th>
                                                        <th>Conversions</th>
                                                        <th>Rate %</th>
                                                    </tr>
                                                </thead>
                                                <tbody></tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Forecast Tab -->
                            <div class="tab-pane fade" id="forecast" role="tabpanel">
                                <div class="row">
                                    <div class="col-12">
                                        <h6>Sales Forecast (Next 30 Days)</h6>
                                        <div id="forecast-chart" class="chart-container"></div>
                                        <div id="forecast-summary" class="mt-3"></div>
                                    </div>
                                </div>
                            </div>

                            <!-- Cohort Analysis Tab -->
                            <div class="tab-pane fade" id="cohort" role="tabpanel">
                                <div class="row">
                                    <div class="col-12">
                                        <h6>Customer Retention Cohort Analysis</h6>
                                        <div id="cohort-analysis"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Load dashboard data
        $(document).ready(function() {
            loadSalesOverview();
            loadSalesTrendChart();
            loadCustomerSegmentsChart();
            loadProductPerformance();
            loadMarketingEffectiveness();
            
            // Tab change handlers
            $('#forecast-tab').on('shown.bs.tab', loadForecast);
            $('#cohort-tab').on('shown.bs.tab', loadCohortAnalysis);
        });

        function loadSalesOverview() {
            $.get('/api/sales-overview', function(data) {
                displayMetrics(data.current_metrics, data.growth_rates);
            });
        }

        function displayMetrics(metrics, growth) {
            const metricsData = [
                {
                    title: 'Total Revenue',
                    value: `$${metrics.total_revenue.toLocaleString()}`,
                    growth: growth.total_revenue_growth,
                    icon: 'fas fa-dollar-sign'
                },
                {
                    title: 'Total Orders',
                    value: metrics.total_orders.toLocaleString(),
                    growth: growth.total_orders_growth,
                    icon: 'fas fa-shopping-cart'
                },
                {
                    title: 'Avg Order Value',
                    value: `$${metrics.avg_order_value.toFixed(2)}`,
                    growth: growth.avg_order_value_growth,
                    icon: 'fas fa-chart-line'
                },
                {
                    title: 'Unique Customers',
                    value: metrics.unique_customers.toLocaleString(),
                    growth: growth.unique_customers_growth,
                    icon: 'fas fa-users'
                }
            ];

            let html = '';
            metricsData.forEach(metric => {
                const growthClass = metric.growth >= 0 ? 'growth-positive' : 'growth-negative';
                const growthIcon = metric.growth >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
                
                html += `
                    <div class="col-md-3">
                        <div class="card metric-card">
                            <div class="card-body text-center">
                                <i class="${metric.icon} fa-2x mb-2"></i>
                                <h6>${metric.title}</h6>
                                <div class="metric-number">${metric.value}</div>
                                <small class="${growthClass}">
                                    <i class="fas ${growthIcon}"></i> ${Math.abs(metric.growth).toFixed(1)}%
                                </small>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            $('#metrics-row').html(html);
        }

        function loadSalesTrendChart() {
            $.get('/api/charts/sales-trend', function(graphJSON) {
                Plotly.newPlot('sales-trend-chart', JSON.parse(graphJSON));
            });
        }

        function loadCustomerSegmentsChart() {
            $.get('/api/charts/customer-segments', function(graphJSON) {
                Plotly.newPlot('customer-segments-chart', JSON.parse(graphJSON));
            });
        }

        function loadProductPerformance() {
            $.get('/api/product-performance', function(data) {
                // Top products table
                let tableHtml = '';
                data.top_products.forEach(product => {
                    tableHtml += `
                        <tr>
                            <td>${product.name}</td>
                            <td>$${product.revenue.toLocaleString()}</td>
                            <td>${product.units_sold}</td>
                            <td>${product.profit_margin.toFixed(1)}%</td>
                        </tr>
                    `;
                });
                $('#top-products-table tbody').html(tableHtml);

                // Inventory alerts
                let alertsHtml = '';
                if (data.low_stock_alerts.length > 0) {
                    alertsHtml += '<div class="alert alert-warning"><strong>Low Stock:</strong><ul class="mb-0">';
                    data.low_stock_alerts.forEach(item => {
                        alertsHtml += `<li>${item.name} (${item.stock_quantity} left)</li>`;
                    });
                    alertsHtml += '</ul></div>';
                }

                if (data.slow_moving_inventory.length > 0) {
                    alertsHtml += '<div class="alert alert-info"><strong>Slow Moving:</strong><ul class="mb-0">';
                    data.slow_moving_inventory.slice(0, 5).forEach(item => {
                        alertsHtml += `<li>${item.name}</li>`;
                    });
                    alertsHtml += '</ul></div>';
                }

                $('#inventory-alerts').html(alertsHtml || '<p class="text-muted">No alerts</p>');
            });
        }

        function loadMarketingEffectiveness() {
            $.get('/api/marketing-effectiveness', function(data) {
                // Channel performance
                let channelHtml = '';
                data.channel_performance.forEach(channel => {
                    channelHtml += `
                        <tr>
                            <td>${channel.acquisition_channel}</td>
                            <td>${channel.customers}</td>
                            <td>$${channel.total_revenue.toLocaleString()}</td>
                            <td>$${channel.avg_clv.toFixed(2)}</td>
                        </tr>
                    `;
                });
                $('#channel-performance-table tbody').html(channelHtml);

                // Conversion analysis
                let conversionHtml = '';
                data.conversion_analysis.forEach(conversion => {
                    conversionHtml += `
                        <tr>
                            <td>${conversion.source}</td>
                            <td>${conversion.total_sessions}</td>
                            <td>${conversion.conversions}</td>
                            <td>${conversion.conversion_rate.toFixed(2)}%</td>
                        </tr>
                    `;
                });
                $('#conversion-table tbody').html(conversionHtml);
            });
        }

        function loadForecast() {
            $.get('/api/sales-forecast', function(data) {
                if (data.error) {
                    $('#forecast-chart').html(`<div class="alert alert-warning">${data.error}</div>`);
                    return;
                }

                // Create forecast chart
                const trace = {
                    x: data.predictions.map(p => p.date),
                    y: data.predictions.map(p => p.predicted_revenue),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: 'Predicted Revenue'
                };

                Plotly.newPlot('forecast-chart', [trace], {
                    title: 'Revenue Forecast',
                    xaxis: { title: 'Date' },
                    yaxis: { title: 'Revenue ($)' }
                });

                // Display summary
                $('#forecast-summary').html(`
                    <div class="row">
                        <div class="col-md-4">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h6>Total Predicted Revenue</h6>
                                    <h4>$${data.summary.total_predicted_revenue.toLocaleString()}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h6>Total Predicted Orders</h6>
                                    <h4>${data.summary.total_predicted_orders.toLocaleString()}</h4>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="card">
                                <div class="card-body text-center">
                                    <h6>Model Accuracy (R²)</h6>
                                    <h4>${data.model_performance.revenue_r2}</h4>
                                </div>
                            </div>
                        </div>
                    </div>
                `);
            });
        }

        function loadCohortAnalysis() {
            $.get('/api/cohort-analysis', function(data) {
                if (Object.keys(data).length === 0) {
                    $('#cohort-analysis').html('<div class="alert alert-info">Insufficient data for cohort analysis</div>');
                    return;
                }

                $('#cohort-analysis').html('<p>Cohort analysis data loaded. Advanced visualization would be implemented here.</p>');
            });
        }
    </script>
</body>
</html>
        '''
        
        with open(os.path.join(template_dir, 'ecommerce_dashboard.html'), 'w') as f:
            f.write(html_template)
    
    def run(self, host='localhost', port=5000, debug=True):
        """Run the Flask dashboard."""
        self.create_dashboard_template()
        
        print("🛒 E-commerce Analytics Platform")
        print("=" * 50)
        print(f"🚀 Starting dashboard server...")
        print(f"🌐 Access the dashboard at: http://{host}:{port}")
        print("\n📊 Analytics Features:")
        print("   - Sales performance tracking")
        print("   - Customer segmentation analysis")
        print("   - Product performance insights")
        print("   - Marketing effectiveness metrics")
        print("   - AI-powered sales forecasting")
        print("   - Cohort retention analysis")
        
        self.app.run(host=host, port=port, debug=debug)

def main():
    """Main function to run the E-commerce Analytics platform."""
    print("🛒 E-commerce Analytics Platform")
    print("=" * 50)
    
    choice = input("\nChoose interface:\n1. Web Dashboard\n2. CLI Analytics Demo\nEnter choice (1-2): ")
    
    if choice == '2':
        # CLI demo
        analytics = EcommerceAnalytics()
        
        print("\n📊 E-commerce Analytics - CLI Demo")
        print("Running comprehensive analytics...")
        
        # Sales overview
        sales = analytics.get_sales_overview(30)
        print(f"\n💰 Sales Overview (Last 30 Days):")
        print(f"  Total Revenue: ${sales['current_metrics']['total_revenue']:,.2f}")
        print(f"  Total Orders: {sales['current_metrics']['total_orders']:,}")
        print(f"  Average Order Value: ${sales['current_metrics']['avg_order_value']:.2f}")
        print(f"  Unique Customers: {sales['current_metrics']['unique_customers']:,}")
        
        # Customer segments
        segments = analytics.analyze_customer_segments()
        if 'segment_distribution' in segments:
            print(f"\n👥 Customer Segments:")
            for segment, count in segments['segment_distribution'].items():
                print(f"  {segment}: {count} customers")
        
        # Product performance
        products = analytics.analyze_product_performance(30)
        print(f"\n📦 Product Performance:")
        print(f"  Total Products: {products['performance_metrics']['total_products']}")
        print(f"  Products Sold: {products['performance_metrics']['products_sold']}")
        print(f"  Average Profit Margin: {products['performance_metrics']['avg_profit_margin']:.1f}%")
        
        if products['top_products']:
            print(f"\n🏆 Top 3 Products:")
            for i, product in enumerate(products['top_products'][:3], 1):
                print(f"  {i}. {product['name']} - ${product['revenue']:,.2f} revenue")
        
        # Marketing effectiveness
        marketing = analytics.analyze_marketing_effectiveness()
        if marketing['summary_metrics']['best_channel']:
            print(f"\n📢 Marketing Insights:")
            print(f"  Best Channel: {marketing['summary_metrics']['best_channel']}")
            print(f"  Best Converting Source: {marketing['summary_metrics']['best_converting_source']}")
            print(f"  Overall Conversion Rate: {marketing['summary_metrics']['overall_conversion_rate']:.2f}%")
        
        # Sales forecast
        forecast = analytics.predict_sales_forecast(7)
        if 'predictions' in forecast:
            print(f"\n🔮 7-Day Sales Forecast:")
            print(f"  Predicted Revenue: ${forecast['summary']['total_predicted_revenue']:,.2f}")
            print(f"  Predicted Orders: {forecast['summary']['total_predicted_orders']:,}")
            print(f"  Model Accuracy (R²): {forecast['model_performance']['revenue_r2']}")
        
    else:
        # Run web dashboard
        dashboard = EcommerceDashboard()
        dashboard.run()

if __name__ == "__main__":
    main()
