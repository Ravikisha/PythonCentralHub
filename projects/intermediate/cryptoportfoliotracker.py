import requests
import pandas as pd
import numpy as np
import sqlite3
import json
import time
from datetime import datetime, timedelta
import threading
import schedule
import logging
from collections import defaultdict, deque
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.utils import PlotlyJSONEncoder

# Web framework for portfolio dashboard
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import hashlib
import secrets

# Email notifications
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Technical analysis
import talib
from scipy import stats

# API clients
import websocket
import ssl
import ccxt

# Encryption for secure storage
from cryptography.fernet import Fernet
import base64
import os

# Configuration management
import configparser

class CryptoAPI:
    def __init__(self):
        """Initialize cryptocurrency API clients."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CryptoPortfolioTracker/1.0'
        })
        
        # Rate limiting for API calls
        self.api_calls = deque()
        self.max_calls_per_minute = 100
        
        # Supported exchanges via CCXT
        self.exchanges = {}
        self.websocket_connections = {}
        
        # Price cache to reduce API calls
        self.price_cache = {}
        self.cache_duration = 60  # seconds
        
    def _rate_limit_check(self):
        """Check and enforce rate limiting."""
        now = time.time()
        
        # Remove calls older than 1 minute
        while self.api_calls and self.api_calls[0] <= now - 60:
            self.api_calls.popleft()
        
        if len(self.api_calls) >= self.max_calls_per_minute:
            sleep_time = 60 - (now - self.api_calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.api_calls.append(now)
    
    def get_crypto_prices(self, symbols):
        """Get current prices for multiple cryptocurrencies."""
        try:
            self._rate_limit_check()
            
            # Check cache first
            cached_prices = {}
            symbols_to_fetch = []
            
            for symbol in symbols:
                if symbol in self.price_cache:
                    cache_time, price = self.price_cache[symbol]
                    if time.time() - cache_time < self.cache_duration:
                        cached_prices[symbol] = price
                    else:
                        symbols_to_fetch.append(symbol)
                else:
                    symbols_to_fetch.append(symbol)
            
            if not symbols_to_fetch:
                return cached_prices
            
            # Fetch from CoinGecko API
            symbols_str = ','.join(symbols_to_fetch).lower()
            url = f'https://api.coingecko.com/api/v3/simple/price'
            params = {
                'ids': symbols_str,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Update cache and combine with cached prices
            current_time = time.time()
            for symbol in symbols_to_fetch:
                if symbol.lower() in data:
                    price_info = data[symbol.lower()]
                    self.price_cache[symbol] = (current_time, price_info)
                    cached_prices[symbol] = price_info
            
            return cached_prices
            
        except Exception as e:
            logging.error(f"Error fetching crypto prices: {e}")
            return {}
    
    def get_historical_data(self, symbol, days=30):
        """Get historical price data for a cryptocurrency."""
        try:
            self._rate_limit_check()
            
            url = f'https://api.coingecko.com/api/v3/coins/{symbol.lower()}/market_chart'
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily' if days > 90 else 'hourly'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            if 'volumes' in data:
                volume_df = pd.DataFrame(data['volumes'], columns=['timestamp', 'volume'])
                volume_df['timestamp'] = pd.to_datetime(volume_df['timestamp'], unit='ms')
                volume_df.set_index('timestamp', inplace=True)
                df['volume'] = volume_df['volume']
            
            return df
            
        except Exception as e:
            logging.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_trending_coins(self):
        """Get trending cryptocurrencies."""
        try:
            self._rate_limit_check()
            
            url = 'https://api.coingecko.com/api/v3/search/trending'
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('coins', [])
            
        except Exception as e:
            logging.error(f"Error fetching trending coins: {e}")
            return []
    
    def get_market_data(self, limit=250):
        """Get market overview data."""
        try:
            self._rate_limit_check()
            
            url = 'https://api.coingecko.com/api/v3/coins/markets'
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '1h,24h,7d,30d'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logging.error(f"Error fetching market data: {e}")
            return []
    
    def setup_websocket_feed(self, symbols, callback):
        """Setup real-time price feed via WebSocket."""
        try:
            # Using Binance WebSocket for real-time data
            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    callback(data)
                except Exception as e:
                    logging.error(f"WebSocket message error: {e}")
            
            def on_error(ws, error):
                logging.error(f"WebSocket error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                logging.info("WebSocket connection closed")
            
            def on_open(ws):
                logging.info("WebSocket connection opened")
            
            # Create WebSocket connection
            symbols_lower = [f"{symbol.lower()}usdt" for symbol in symbols]
            streams = '/'.join([f"{symbol}@ticker" for symbol in symbols_lower])
            
            ws_url = f"wss://stream.binance.com:9443/ws/{streams}"
            
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            # Run WebSocket in background thread
            ws_thread = threading.Thread(target=ws.run_forever, kwargs={'sslopt': {"cert_reqs": ssl.CERT_NONE}})
            ws_thread.daemon = True
            ws_thread.start()
            
            return ws
            
        except Exception as e:
            logging.error(f"Error setting up WebSocket: {e}")
            return None

class CryptoDatabase:
    def __init__(self, db_path="crypto_portfolio.db"):
        """Initialize cryptocurrency portfolio database."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables for cryptocurrency portfolio."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Portfolios table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                total_invested REAL DEFAULT 0,
                current_value REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Holdings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                amount REAL NOT NULL,
                average_cost REAL NOT NULL,
                total_cost REAL NOT NULL,
                current_price REAL,
                current_value REAL,
                profit_loss REAL,
                profit_loss_percentage REAL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                transaction_type TEXT CHECK(transaction_type IN ('buy', 'sell', 'transfer_in', 'transfer_out')) NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                total_value REAL NOT NULL,
                fees REAL DEFAULT 0,
                exchange TEXT,
                notes TEXT,
                transaction_date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume REAL,
                market_cap REAL,
                change_24h REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, timestamp)
            )
        ''')
        
        # Portfolio snapshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                portfolio_id INTEGER NOT NULL,
                total_value REAL NOT NULL,
                total_invested REAL NOT NULL,
                profit_loss REAL NOT NULL,
                profit_loss_percentage REAL NOT NULL,
                holdings_data TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                alert_type TEXT CHECK(alert_type IN ('price_above', 'price_below', 'change_above', 'change_below')) NOT NULL,
                threshold REAL NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                last_triggered TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Watchlist table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, symbol)
            )
        ''')
        
        # Exchange API keys table (encrypted)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exchange_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exchange_name TEXT NOT NULL,
                api_key_encrypted TEXT NOT NULL,
                api_secret_encrypted TEXT NOT NULL,
                passphrase_encrypted TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()

class PortfolioAnalyzer:
    def __init__(self, db, crypto_api):
        """Initialize portfolio analyzer."""
        self.db = db
        self.crypto_api = crypto_api
    
    def calculate_portfolio_metrics(self, portfolio_id):
        """Calculate comprehensive portfolio metrics."""
        conn = sqlite3.connect(self.db.db_path)
        
        # Get current holdings
        holdings_df = pd.read_sql_query('''
            SELECT * FROM holdings WHERE portfolio_id = ?
        ''', conn, params=[portfolio_id])
        
        if holdings_df.empty:
            conn.close()
            return {}
        
        # Update current prices
        symbols = holdings_df['symbol'].unique().tolist()
        current_prices = self.crypto_api.get_crypto_prices(symbols)
        
        # Update holdings with current prices
        total_value = 0
        total_invested = 0
        total_profit_loss = 0
        
        for idx, holding in holdings_df.iterrows():
            symbol = holding['symbol']
            amount = holding['amount']
            avg_cost = holding['average_cost']
            
            if symbol in current_prices:
                current_price = current_prices[symbol]['usd']
                current_value = amount * current_price
                profit_loss = current_value - (amount * avg_cost)
                profit_loss_pct = (profit_loss / (amount * avg_cost)) * 100 if avg_cost > 0 else 0
                
                # Update database
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE holdings 
                    SET current_price = ?, current_value = ?, profit_loss = ?, 
                        profit_loss_percentage = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (current_price, current_value, profit_loss, profit_loss_pct, holding['id']))
                
                total_value += current_value
                total_invested += amount * avg_cost
                total_profit_loss += profit_loss
        
        # Calculate portfolio-level metrics
        total_profit_loss_pct = (total_profit_loss / total_invested) * 100 if total_invested > 0 else 0
        
        # Update portfolio totals
        cursor.execute('''
            UPDATE portfolios 
            SET current_value = ?, total_invested = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (total_value, total_invested, portfolio_id))
        
        conn.commit()
        
        # Get updated holdings for allocation calculation
        updated_holdings = pd.read_sql_query('''
            SELECT symbol, amount, current_value, profit_loss, profit_loss_percentage
            FROM holdings WHERE portfolio_id = ? AND current_value > 0
            ORDER BY current_value DESC
        ''', conn, params=[portfolio_id])
        
        conn.close()
        
        # Calculate allocation percentages
        if not updated_holdings.empty:
            updated_holdings['allocation_percentage'] = (updated_holdings['current_value'] / total_value) * 100
        
        return {
            'total_value': total_value,
            'total_invested': total_invested,
            'total_profit_loss': total_profit_loss,
            'total_profit_loss_percentage': total_profit_loss_pct,
            'holdings': updated_holdings.to_dict('records'),
            'top_performers': self._get_top_performers(updated_holdings),
            'diversification_score': self._calculate_diversification_score(updated_holdings)
        }
    
    def _get_top_performers(self, holdings_df):
        """Get top performing and worst performing assets."""
        if holdings_df.empty:
            return {'top_gainers': [], 'top_losers': []}
        
        sorted_by_pct = holdings_df.sort_values('profit_loss_percentage', ascending=False)
        
        return {
            'top_gainers': sorted_by_pct.head(5).to_dict('records'),
            'top_losers': sorted_by_pct.tail(5).to_dict('records')
        }
    
    def _calculate_diversification_score(self, holdings_df):
        """Calculate portfolio diversification score (0-100)."""
        if holdings_df.empty:
            return 0
        
        # Calculate Herfindahl-Hirschman Index (HHI) for concentration
        allocations = holdings_df['allocation_percentage'].values / 100
        hhi = np.sum(allocations ** 2)
        
        # Convert to diversification score (inverse of concentration)
        diversification_score = (1 - hhi) * 100
        
        return min(100, max(0, diversification_score))
    
    def generate_performance_report(self, portfolio_id, days_back=30):
        """Generate comprehensive performance report."""
        conn = sqlite3.connect(self.db.db_path)
        
        # Get portfolio snapshots for trend analysis
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        snapshots_df = pd.read_sql_query('''
            SELECT * FROM portfolio_snapshots 
            WHERE portfolio_id = ? AND timestamp >= ?
            ORDER BY timestamp
        ''', conn, params=[portfolio_id, start_date])
        
        # Get transaction history
        transactions_df = pd.read_sql_query('''
            SELECT * FROM transactions 
            WHERE portfolio_id = ? AND transaction_date >= ?
            ORDER BY transaction_date DESC
        ''', conn, params=[portfolio_id, start_date])
        
        # Get current metrics
        current_metrics = self.calculate_portfolio_metrics(portfolio_id)
        
        # Calculate additional metrics
        if not snapshots_df.empty:
            # Performance trend
            snapshots_df['timestamp'] = pd.to_datetime(snapshots_df['timestamp'])
            initial_value = snapshots_df.iloc[0]['total_value']
            final_value = snapshots_df.iloc[-1]['total_value']
            period_return = ((final_value - initial_value) / initial_value) * 100 if initial_value > 0 else 0
            
            # Volatility calculation
            snapshots_df['daily_return'] = snapshots_df['total_value'].pct_change()
            volatility = snapshots_df['daily_return'].std() * np.sqrt(365) * 100  # Annualized
            
            # Sharpe ratio (simplified, assuming 0% risk-free rate)
            avg_return = snapshots_df['daily_return'].mean() * 365
            sharpe_ratio = avg_return / (volatility / 100) if volatility > 0 else 0
            
            # Maximum drawdown
            running_max = snapshots_df['total_value'].expanding().max()
            drawdown = (snapshots_df['total_value'] - running_max) / running_max
            max_drawdown = drawdown.min() * 100
        else:
            period_return = 0
            volatility = 0
            sharpe_ratio = 0
            max_drawdown = 0
        
        conn.close()
        
        return {
            'current_metrics': current_metrics,
            'period_return': period_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'transaction_count': len(transactions_df),
            'recent_transactions': transactions_df.head(10).to_dict('records'),
            'performance_history': snapshots_df.to_dict('records')
        }
    
    def create_portfolio_snapshot(self, portfolio_id):
        """Create a snapshot of current portfolio state."""
        metrics = self.calculate_portfolio_metrics(portfolio_id)
        
        if not metrics:
            return
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO portfolio_snapshots 
            (portfolio_id, total_value, total_invested, profit_loss, profit_loss_percentage, holdings_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            portfolio_id,
            metrics['total_value'],
            metrics['total_invested'],
            metrics['total_profit_loss'],
            metrics['total_profit_loss_percentage'],
            json.dumps(metrics['holdings'])
        ))
        
        conn.commit()
        conn.close()

class TechnicalAnalyzer:
    def __init__(self, crypto_api):
        """Initialize technical analysis engine."""
        self.crypto_api = crypto_api
    
    def analyze_asset(self, symbol, days=90):
        """Perform comprehensive technical analysis on an asset."""
        # Get historical data
        df = self.crypto_api.get_historical_data(symbol, days)
        
        if df.empty:
            return {}
        
        # Calculate technical indicators
        analysis = {}
        
        try:
            # Ensure we have enough data
            if len(df) < 50:
                return {'error': 'Insufficient data for analysis'}
            
            # Price-based indicators
            analysis['sma_20'] = self._calculate_sma(df['price'], 20)
            analysis['sma_50'] = self._calculate_sma(df['price'], 50)
            analysis['ema_12'] = self._calculate_ema(df['price'], 12)
            analysis['ema_26'] = self._calculate_ema(df['price'], 26)
            
            # Momentum indicators
            analysis['rsi'] = self._calculate_rsi(df['price'])
            analysis['macd'] = self._calculate_macd(df['price'])
            analysis['bollinger_bands'] = self._calculate_bollinger_bands(df['price'])
            
            # Volume indicators (if available)
            if 'volume' in df.columns:
                analysis['volume_sma'] = self._calculate_sma(df['volume'], 20)
                analysis['vwap'] = self._calculate_vwap(df)
            
            # Support and resistance levels
            analysis['support_resistance'] = self._find_support_resistance(df['price'])
            
            # Price targets
            analysis['price_targets'] = self._calculate_price_targets(df['price'])
            
            # Overall signal
            analysis['signal'] = self._generate_signal(analysis)
            
            # Current price info
            analysis['current_price'] = df['price'].iloc[-1]
            analysis['price_change_24h'] = ((df['price'].iloc[-1] - df['price'].iloc[-2]) / df['price'].iloc[-2]) * 100
            
        except Exception as e:
            logging.error(f"Error in technical analysis for {symbol}: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _calculate_sma(self, prices, period):
        """Calculate Simple Moving Average."""
        return prices.rolling(window=period).mean().iloc[-1]
    
    def _calculate_ema(self, prices, period):
        """Calculate Exponential Moving Average."""
        return prices.ewm(span=period).mean().iloc[-1]
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def _calculate_macd(self, prices):
        """Calculate MACD indicator."""
        ema_12 = prices.ewm(span=12).mean()
        ema_26 = prices.ewm(span=26).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line.iloc[-1],
            'signal': signal_line.iloc[-1],
            'histogram': histogram.iloc[-1]
        }
    
    def _calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Calculate Bollinger Bands."""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band.iloc[-1],
            'middle': sma.iloc[-1],
            'lower': lower_band.iloc[-1],
            'current_position': (prices.iloc[-1] - lower_band.iloc[-1]) / (upper_band.iloc[-1] - lower_band.iloc[-1])
        }
    
    def _calculate_vwap(self, df):
        """Calculate Volume Weighted Average Price."""
        if 'volume' not in df.columns:
            return None
        
        typical_price = df['price']
        volume = df['volume']
        
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap.iloc[-1]
    
    def _find_support_resistance(self, prices, window=20):
        """Identify support and resistance levels."""
        recent_prices = prices.tail(100)  # Last 100 data points
        
        # Find local maxima and minima
        from scipy.signal import argrelextrema
        
        # Local maxima (resistance)
        resistance_indices = argrelextrema(recent_prices.values, np.greater, order=window//2)[0]
        resistance_levels = [recent_prices.iloc[i] for i in resistance_indices]
        
        # Local minima (support)
        support_indices = argrelextrema(recent_prices.values, np.less, order=window//2)[0]
        support_levels = [recent_prices.iloc[i] for i in support_indices]
        
        # Filter and sort levels
        resistance_levels = sorted(list(set([round(level, 2) for level in resistance_levels])), reverse=True)[:3]
        support_levels = sorted(list(set([round(level, 2) for level in support_levels])), reverse=True)[:3]
        
        return {
            'resistance': resistance_levels,
            'support': support_levels
        }
    
    def _calculate_price_targets(self, prices):
        """Calculate price targets based on recent price action."""
        current_price = prices.iloc[-1]
        
        # Calculate percentage-based targets
        upside_targets = [
            current_price * 1.05,  # 5% upside
            current_price * 1.10,  # 10% upside
            current_price * 1.20   # 20% upside
        ]
        
        downside_targets = [
            current_price * 0.95,  # 5% downside
            current_price * 0.90,  # 10% downside
            current_price * 0.80   # 20% downside
        ]
        
        return {
            'upside': [round(target, 2) for target in upside_targets],
            'downside': [round(target, 2) for target in downside_targets]
        }
    
    def _generate_signal(self, analysis):
        """Generate buy/sell/hold signal based on technical indicators."""
        signals = []
        
        try:
            # RSI signal
            rsi = analysis.get('rsi', 50)
            if rsi < 30:
                signals.append('buy')  # Oversold
            elif rsi > 70:
                signals.append('sell')  # Overbought
            else:
                signals.append('neutral')
            
            # MACD signal
            macd_data = analysis.get('macd', {})
            if macd_data.get('macd', 0) > macd_data.get('signal', 0):
                signals.append('buy')  # MACD above signal
            else:
                signals.append('sell')  # MACD below signal
            
            # Moving average signal
            sma_20 = analysis.get('sma_20', 0)
            sma_50 = analysis.get('sma_50', 0)
            current_price = analysis.get('current_price', 0)
            
            if current_price > sma_20 > sma_50:
                signals.append('buy')  # Uptrend
            elif current_price < sma_20 < sma_50:
                signals.append('sell')  # Downtrend
            else:
                signals.append('neutral')
            
            # Determine overall signal
            buy_signals = signals.count('buy')
            sell_signals = signals.count('sell')
            
            if buy_signals > sell_signals:
                return 'buy'
            elif sell_signals > buy_signals:
                return 'sell'
            else:
                return 'hold'
                
        except Exception as e:
            logging.error(f"Error generating signal: {e}")
            return 'hold'

class AlertManager:
    def __init__(self, db, crypto_api):
        """Initialize alert management system."""
        self.db = db
        self.crypto_api = crypto_api
        self.running = False
    
    def start_monitoring(self):
        """Start alert monitoring."""
        self.running = True
        
        # Schedule alert checks
        schedule.every(1).minutes.do(self._check_alerts)
        
        # Start scheduler thread
        monitor_thread = threading.Thread(target=self._run_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        logging.info("Alert monitoring started")
    
    def stop_monitoring(self):
        """Stop alert monitoring."""
        self.running = False
        schedule.clear()
        logging.info("Alert monitoring stopped")
    
    def _run_monitor(self):
        """Run the monitoring loop."""
        while self.running:
            schedule.run_pending()
            time.sleep(60)
    
    def _check_alerts(self):
        """Check all active alerts."""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Get all active alerts
            cursor.execute('''
                SELECT a.*, u.email FROM alerts a
                JOIN users u ON a.user_id = u.id
                WHERE a.is_active = 1
            ''')
            
            alerts = cursor.fetchall()
            
            if not alerts:
                conn.close()
                return
            
            # Get unique symbols
            symbols = list(set([alert[2] for alert in alerts]))
            current_prices = self.crypto_api.get_crypto_prices(symbols)
            
            for alert in alerts:
                alert_id, user_id, symbol, alert_type, threshold, is_active, last_triggered, created_at, email = alert
                
                if symbol not in current_prices:
                    continue
                
                price_data = current_prices[symbol]
                current_price = price_data['usd']
                change_24h = price_data.get('usd_24h_change', 0)
                
                triggered = False
                
                # Check alert conditions
                if alert_type == 'price_above' and current_price >= threshold:
                    triggered = True
                elif alert_type == 'price_below' and current_price <= threshold:
                    triggered = True
                elif alert_type == 'change_above' and change_24h >= threshold:
                    triggered = True
                elif alert_type == 'change_below' and change_24h <= threshold:
                    triggered = True
                
                if triggered:
                    # Check if already triggered recently (avoid spam)
                    if last_triggered:
                        last_trigger_time = datetime.strptime(last_triggered, '%Y-%m-%d %H:%M:%S')
                        if datetime.now() - last_trigger_time < timedelta(hours=1):
                            continue
                    
                    # Send notification
                    self._send_alert_notification(email, symbol, alert_type, threshold, current_price, change_24h)
                    
                    # Update last triggered time
                    cursor.execute('''
                        UPDATE alerts SET last_triggered = CURRENT_TIMESTAMP WHERE id = ?
                    ''', (alert_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Error checking alerts: {e}")
    
    def _send_alert_notification(self, email, symbol, alert_type, threshold, current_price, change_24h):
        """Send alert notification via email."""
        try:
            # Format alert message
            if alert_type == 'price_above':
                message = f"{symbol.upper()} price (${current_price:.2f}) has risen above your alert threshold of ${threshold:.2f}"
            elif alert_type == 'price_below':
                message = f"{symbol.upper()} price (${current_price:.2f}) has fallen below your alert threshold of ${threshold:.2f}"
            elif alert_type == 'change_above':
                message = f"{symbol.upper()} 24h change ({change_24h:.2f}%) has exceeded your alert threshold of {threshold:.2f}%"
            elif alert_type == 'change_below':
                message = f"{symbol.upper()} 24h change ({change_24h:.2f}%) has fallen below your alert threshold of {threshold:.2f}%"
            
            subject = f"Crypto Alert: {symbol.upper()}"
            
            # In a real implementation, you would use actual SMTP settings
            logging.info(f"Alert notification: {email} - {message}")
            
            # Here you would implement actual email sending
            # self._send_email(email, subject, message)
            
        except Exception as e:
            logging.error(f"Error sending notification: {e}")

class CryptoPortfolioApp:
    def __init__(self):
        """Initialize Flask application for cryptocurrency portfolio."""
        self.app = Flask(__name__)
        self.app.secret_key = 'crypto_portfolio_secret_2024'
        
        self.db = CryptoDatabase()
        self.crypto_api = CryptoAPI()
        self.analyzer = PortfolioAnalyzer(self.db, self.crypto_api)
        self.technical_analyzer = TechnicalAnalyzer(self.crypto_api)
        self.alert_manager = AlertManager(self.db, self.crypto_api)
        
        self.setup_routes()
        
        # Start background services
        self.alert_manager.start_monitoring()
        self._start_portfolio_snapshot_scheduler()
    
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def dashboard():
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user_id = session['user_id']
            
            # Get user portfolios
            conn = sqlite3.connect(self.db.db_path)
            portfolios = pd.read_sql_query('''
                SELECT * FROM portfolios WHERE user_id = ? ORDER BY updated_at DESC
            ''', conn, params=[user_id])
            
            # Get market overview
            market_data = self.crypto_api.get_market_data(limit=10)
            trending_coins = self.crypto_api.get_trending_coins()
            
            conn.close()
            
            return render_template('crypto_dashboard.html', 
                                 portfolios=portfolios.to_dict('records'),
                                 market_data=market_data[:10],
                                 trending_coins=trending_coins[:5])
        
        @self.app.route('/portfolio/<int:portfolio_id>')
        def portfolio_detail(portfolio_id):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            # Get portfolio metrics and performance
            metrics = self.analyzer.calculate_portfolio_metrics(portfolio_id)
            performance = self.analyzer.generate_performance_report(portfolio_id)
            
            return render_template('portfolio_detail.html',
                                 portfolio_id=portfolio_id,
                                 metrics=metrics,
                                 performance=performance)
        
        @self.app.route('/add_transaction', methods=['GET', 'POST'])
        def add_transaction():
            if request.method == 'POST':
                data = request.form
                
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                
                # Add transaction
                cursor.execute('''
                    INSERT INTO transactions 
                    (portfolio_id, symbol, transaction_type, amount, price, total_value, fees, exchange, notes, transaction_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['portfolio_id'], data['symbol'].upper(), data['transaction_type'],
                    float(data['amount']), float(data['price']), 
                    float(data['amount']) * float(data['price']),
                    float(data.get('fees', 0)), data.get('exchange', ''),
                    data.get('notes', ''), data['transaction_date']
                ))
                
                # Update holdings
                self._update_holdings_after_transaction(cursor, data)
                
                conn.commit()
                conn.close()
                
                flash('Transaction added successfully!')
                return redirect(url_for('portfolio_detail', portfolio_id=data['portfolio_id']))
            
            return render_template('add_transaction.html')
        
        @self.app.route('/technical_analysis/<symbol>')
        def technical_analysis(symbol):
            analysis = self.technical_analyzer.analyze_asset(symbol)
            return jsonify(analysis)
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                
                # Simple authentication (in production, use proper password hashing)
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT id FROM users WHERE username = ? AND password_hash = ?',
                             (username, hashlib.sha256(password.encode()).hexdigest()))
                user = cursor.fetchone()
                
                if user:
                    session['user_id'] = user[0]
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid credentials')
                
                conn.close()
            
            return render_template('login.html')
        
        @self.app.route('/logout')
        def logout():
            session.pop('user_id', None)
            return redirect(url_for('login'))
        
        @self.app.route('/api/portfolio_chart/<int:portfolio_id>')
        def portfolio_chart(portfolio_id):
            performance = self.analyzer.generate_performance_report(portfolio_id, days_back=90)
            return jsonify(performance['performance_history'])
    
    def _update_holdings_after_transaction(self, cursor, transaction_data):
        """Update holdings table after a transaction."""
        portfolio_id = transaction_data['portfolio_id']
        symbol = transaction_data['symbol'].upper()
        transaction_type = transaction_data['transaction_type']
        amount = float(transaction_data['amount'])
        price = float(transaction_data['price'])
        
        # Get current holding
        cursor.execute('SELECT * FROM holdings WHERE portfolio_id = ? AND symbol = ?',
                      (portfolio_id, symbol))
        holding = cursor.fetchone()
        
        if transaction_type in ['buy', 'transfer_in']:
            if holding:
                # Update existing holding
                old_amount = holding[3]
                old_avg_cost = holding[4]
                old_total_cost = holding[5]
                
                new_amount = old_amount + amount
                new_total_cost = old_total_cost + (amount * price)
                new_avg_cost = new_total_cost / new_amount
                
                cursor.execute('''
                    UPDATE holdings 
                    SET amount = ?, average_cost = ?, total_cost = ?
                    WHERE portfolio_id = ? AND symbol = ?
                ''', (new_amount, new_avg_cost, new_total_cost, portfolio_id, symbol))
            else:
                # Create new holding
                cursor.execute('''
                    INSERT INTO holdings (portfolio_id, symbol, amount, average_cost, total_cost)
                    VALUES (?, ?, ?, ?, ?)
                ''', (portfolio_id, symbol, amount, price, amount * price))
        
        elif transaction_type in ['sell', 'transfer_out']:
            if holding:
                old_amount = holding[3]
                old_total_cost = holding[5]
                
                if old_amount >= amount:
                    new_amount = old_amount - amount
                    new_total_cost = old_total_cost - (amount * holding[4])  # Use average cost
                    
                    if new_amount > 0:
                        cursor.execute('''
                            UPDATE holdings 
                            SET amount = ?, total_cost = ?
                            WHERE portfolio_id = ? AND symbol = ?
                        ''', (new_amount, new_total_cost, portfolio_id, symbol))
                    else:
                        # Remove holding if amount is zero
                        cursor.execute('DELETE FROM holdings WHERE portfolio_id = ? AND symbol = ?',
                                      (portfolio_id, symbol))
    
    def _start_portfolio_snapshot_scheduler(self):
        """Start scheduler for portfolio snapshots."""
        def take_snapshots():
            try:
                conn = sqlite3.connect(self.db.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT id FROM portfolios WHERE is_active = 1')
                portfolios = cursor.fetchall()
                
                for portfolio_id, in portfolios:
                    self.analyzer.create_portfolio_snapshot(portfolio_id)
                
                conn.close()
                logging.info("Portfolio snapshots created")
                
            except Exception as e:
                logging.error(f"Error creating snapshots: {e}")
        
        # Take snapshots every hour
        schedule.every().hour.do(take_snapshots)
    
    def create_sample_data(self):
        """Create sample data for demonstration."""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Create sample user
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', ('demo', 'demo@crypto.com', hashlib.sha256('demo'.encode()).hexdigest()))
        
        # Get user ID
        cursor.execute('SELECT id FROM users WHERE username = ?', ('demo',))
        user_id = cursor.fetchone()[0]
        
        # Create sample portfolio
        cursor.execute('''
            INSERT OR IGNORE INTO portfolios (user_id, name, description)
            VALUES (?, ?, ?)
        ''', (user_id, 'My Crypto Portfolio', 'Main cryptocurrency portfolio'))
        
        # Get portfolio ID
        cursor.execute('SELECT id FROM portfolios WHERE user_id = ? AND name = ?',
                      (user_id, 'My Crypto Portfolio'))
        portfolio_id = cursor.fetchone()[0]
        
        # Add sample transactions
        sample_transactions = [
            ('bitcoin', 'buy', 0.5, 45000, '2024-01-01'),
            ('ethereum', 'buy', 2.0, 3000, '2024-01-02'),
            ('cardano', 'buy', 1000, 0.5, '2024-01-03'),
        ]
        
        for symbol, tx_type, amount, price, date in sample_transactions:
            cursor.execute('''
                INSERT OR IGNORE INTO transactions 
                (portfolio_id, symbol, transaction_type, amount, price, total_value, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (portfolio_id, symbol, tx_type, amount, price, amount * price, date))
            
            # Update holdings
            cursor.execute('''
                INSERT OR REPLACE INTO holdings 
                (portfolio_id, symbol, amount, average_cost, total_cost)
                VALUES (?, ?, ?, ?, ?)
            ''', (portfolio_id, symbol, amount, price, amount * price))
        
        conn.commit()
        conn.close()
    
    def run(self, host='localhost', port=5000, debug=True):
        """Run the cryptocurrency portfolio application."""
        
        print("💰 Cryptocurrency Portfolio Tracker")
        print("=" * 50)
        print(f"🚀 Starting crypto portfolio platform...")
        print(f"🌐 Access the dashboard at: http://{host}:{port}")
        print("\n🔥 Portfolio Features:")
        print("   - Real-time portfolio tracking and analytics")
        print("   - Advanced technical analysis with indicators")
        print("   - Automated alerts and notifications")
        print("   - Comprehensive performance reports")
        print("   - Multi-exchange transaction support")
        print("   - Professional charting and visualization")
        print("   - Risk analysis and diversification metrics")
        print("\n📊 Demo Login: username='demo', password='demo'")
        
        # Create sample data
        self.create_sample_data()
        
        try:
            self.app.run(host=host, port=port, debug=debug)
        finally:
            self.alert_manager.stop_monitoring()

def main():
    """Main function to run the cryptocurrency portfolio tracker."""
    print("💰 Cryptocurrency Portfolio Tracker")
    print("=" * 50)
    
    choice = input("\nChoose interface:\n1. Web Interface\n2. CLI Demo\nEnter choice (1-2): ")
    
    if choice == '2':
        # CLI demo
        print("\n💰 Crypto Portfolio Tracker - CLI Demo")
        print("Initializing demo portfolio...")
        
        # Initialize components
        api = CryptoAPI()
        
        # Demo: Get current prices
        symbols = ['bitcoin', 'ethereum', 'cardano']
        print(f"\n📊 Current Prices for {symbols}:")
        prices = api.get_crypto_prices(symbols)
        
        for symbol, data in prices.items():
            if data:
                print(f"  {symbol.upper()}: ${data['usd']:,.2f} ({data.get('usd_24h_change', 0):+.2f}%)")
        
        # Demo: Technical analysis
        print(f"\n🔍 Technical Analysis for Bitcoin:")
        analysis = TechnicalAnalyzer(api).analyze_asset('bitcoin', 30)
        
        if 'error' not in analysis:
            print(f"  Current Price: ${analysis.get('current_price', 0):,.2f}")
            print(f"  RSI: {analysis.get('rsi', 0):.2f}")
            print(f"  Signal: {analysis.get('signal', 'hold').upper()}")
            
            if 'support_resistance' in analysis:
                sr = analysis['support_resistance']
                print(f"  Support Levels: {sr.get('support', [])}")
                print(f"  Resistance Levels: {sr.get('resistance', [])}")
        
        print("\n✅ Demo completed!")
    
    else:
        # Run web interface
        app = CryptoPortfolioApp()
        app.run()

if __name__ == "__main__":
    main()
