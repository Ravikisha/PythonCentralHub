import requests
import json
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime, timedelta
import sqlite3
import schedule
import time
import threading
from flask import Flask, render_template, jsonify, request
import plotly.graph_objs as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import tweepy
import facebook
import instaloader
from textblob import TextBlob
import re
from collections import Counter
import numpy as np
from wordcloud import WordCloud
import base64
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

class SocialMediaAnalyticsAPI:
    def __init__(self):
        """Initialize API connections and configurations."""
        self.db_path = "social_analytics.db"
        self.init_database()
        
        # API configurations (replace with your actual API keys)
        self.twitter_config = {
            'api_key': 'YOUR_TWITTER_API_KEY',
            'api_secret': 'YOUR_TWITTER_API_SECRET',
            'access_token': 'YOUR_TWITTER_ACCESS_TOKEN',
            'access_token_secret': 'YOUR_TWITTER_ACCESS_TOKEN_SECRET'
        }
        
        self.facebook_config = {
            'access_token': 'YOUR_FACEBOOK_ACCESS_TOKEN',
            'page_id': 'YOUR_FACEBOOK_PAGE_ID'
        }
        
        self.instagram_config = {
            'username': 'YOUR_INSTAGRAM_USERNAME',
            'password': 'YOUR_INSTAGRAM_PASSWORD'
        }
        
        # Initialize API clients
        self.setup_apis()
        
    def init_database(self):
        """Create database tables for social media analytics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                post_id TEXT UNIQUE NOT NULL,
                content TEXT,
                author TEXT,
                timestamp DATETIME,
                likes INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                reach INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0,
                sentiment_score REAL DEFAULT 0,
                sentiment_label TEXT,
                hashtags TEXT,
                mentions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                date DATE NOT NULL,
                time_period TEXT DEFAULT 'daily',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Hashtags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hashtags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hashtag TEXT NOT NULL,
                platform TEXT NOT NULL,
                usage_count INTEGER DEFAULT 1,
                engagement_score REAL DEFAULT 0,
                last_used DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Competitors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platform TEXT NOT NULL,
                username TEXT NOT NULL,
                followers INTEGER DEFAULT 0,
                following INTEGER DEFAULT 0,
                posts_count INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0,
                last_updated DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platform TEXT NOT NULL,
                start_date DATE,
                end_date DATE,
                budget REAL DEFAULT 0,
                reach INTEGER DEFAULT 0,
                impressions INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                cost_per_click REAL DEFAULT 0,
                roi REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def setup_apis(self):
        """Initialize social media API clients."""
        try:
            # Twitter API
            if all(self.twitter_config.values()):
                auth = tweepy.OAuthHandler(
                    self.twitter_config['api_key'],
                    self.twitter_config['api_secret']
                )
                auth.set_access_token(
                    self.twitter_config['access_token'],
                    self.twitter_config['access_token_secret']
                )
                self.twitter_api = tweepy.API(auth, wait_on_rate_limit=True)
            else:
                self.twitter_api = None
                
            # Facebook API
            if self.facebook_config['access_token']:
                self.facebook_api = facebook.GraphAPI(
                    access_token=self.facebook_config['access_token']
                )
            else:
                self.facebook_api = None
                
            # Instagram API
            if self.instagram_config['username']:
                self.instagram_api = instaloader.Instaloader()
            else:
                self.instagram_api = None
                
        except Exception as e:
            print(f"API setup error: {e}")
    
    def fetch_twitter_data(self, username, count=100):
        """Fetch Twitter data for analysis."""
        if not self.twitter_api:
            return self.generate_mock_twitter_data(username, count)
            
        try:
            tweets = tweepy.Cursor(
                self.twitter_api.user_timeline,
                screen_name=username,
                include_rts=False,
                tweet_mode='extended'
            ).items(count)
            
            posts_data = []
            for tweet in tweets:
                # Sentiment analysis
                sentiment = TextBlob(tweet.full_text).sentiment
                sentiment_label = 'positive' if sentiment.polarity > 0.1 else 'negative' if sentiment.polarity < -0.1 else 'neutral'
                
                # Extract hashtags and mentions
                hashtags = [tag['text'] for tag in tweet.entities['hashtags']]
                mentions = [mention['screen_name'] for mention in tweet.entities['user_mentions']]
                
                post_data = {
                    'platform': 'twitter',
                    'post_id': str(tweet.id),
                    'content': tweet.full_text,
                    'author': tweet.user.screen_name,
                    'timestamp': tweet.created_at,
                    'likes': tweet.favorite_count,
                    'shares': tweet.retweet_count,
                    'comments': 0,  # Twitter API doesn't provide reply count directly
                    'reach': tweet.user.followers_count,
                    'sentiment_score': sentiment.polarity,
                    'sentiment_label': sentiment_label,
                    'hashtags': json.dumps(hashtags),
                    'mentions': json.dumps(mentions)
                }
                
                posts_data.append(post_data)
                
            return posts_data
            
        except Exception as e:
            print(f"Twitter API error: {e}")
            return self.generate_mock_twitter_data(username, count)
    
    def fetch_facebook_data(self, page_id, count=100):
        """Fetch Facebook data for analysis."""
        if not self.facebook_api:
            return self.generate_mock_facebook_data(page_id, count)
            
        try:
            posts = self.facebook_api.get_connections(
                page_id,
                'posts',
                fields='id,message,created_time,likes.summary(true),shares,comments.summary(true)'
            )
            
            posts_data = []
            for post in posts['data'][:count]:
                message = post.get('message', '')
                if message:
                    # Sentiment analysis
                    sentiment = TextBlob(message).sentiment
                    sentiment_label = 'positive' if sentiment.polarity > 0.1 else 'negative' if sentiment.polarity < -0.1 else 'neutral'
                    
                    # Extract hashtags
                    hashtags = re.findall(r'#\w+', message)
                    
                    post_data = {
                        'platform': 'facebook',
                        'post_id': post['id'],
                        'content': message,
                        'author': page_id,
                        'timestamp': datetime.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S%z'),
                        'likes': post.get('likes', {}).get('summary', {}).get('total_count', 0),
                        'shares': post.get('shares', {}).get('count', 0),
                        'comments': post.get('comments', {}).get('summary', {}).get('total_count', 0),
                        'sentiment_score': sentiment.polarity,
                        'sentiment_label': sentiment_label,
                        'hashtags': json.dumps(hashtags)
                    }
                    
                    posts_data.append(post_data)
                    
            return posts_data
            
        except Exception as e:
            print(f"Facebook API error: {e}")
            return self.generate_mock_facebook_data(page_id, count)
    
    def fetch_instagram_data(self, username, count=100):
        """Fetch Instagram data for analysis."""
        if not self.instagram_api:
            return self.generate_mock_instagram_data(username, count)
            
        try:
            profile = instaloader.Profile.from_username(self.instagram_api.context, username)
            posts_data = []
            
            for post in profile.get_posts():
                if len(posts_data) >= count:
                    break
                    
                # Sentiment analysis
                caption = post.caption or ""
                sentiment = TextBlob(caption).sentiment
                sentiment_label = 'positive' if sentiment.polarity > 0.1 else 'negative' if sentiment.polarity < -0.1 else 'neutral'
                
                # Extract hashtags
                hashtags = re.findall(r'#\w+', caption)
                
                post_data = {
                    'platform': 'instagram',
                    'post_id': str(post.mediaid),
                    'content': caption,
                    'author': username,
                    'timestamp': post.date_utc,
                    'likes': post.likes,
                    'shares': 0,  # Instagram doesn't have shares
                    'comments': post.comments,
                    'sentiment_score': sentiment.polarity,
                    'sentiment_label': sentiment_label,
                    'hashtags': json.dumps(hashtags)
                }
                
                posts_data.append(post_data)
                
            return posts_data
            
        except Exception as e:
            print(f"Instagram API error: {e}")
            return self.generate_mock_instagram_data(username, count)
    
    def generate_mock_twitter_data(self, username, count):
        """Generate mock Twitter data for demonstration."""
        mock_posts = []
        base_date = datetime.now() - timedelta(days=30)
        
        sample_tweets = [
            "Just launched our new product! Excited to share it with everyone! #innovation #startup",
            "Great meeting with the team today. Productivity through the roof! #teamwork",
            "Beautiful sunset today. Nature never fails to amaze me #photography #nature",
            "Reading an amazing book about AI and machine learning #AI #books #learning",
            "Coffee and code. Perfect combination for a Monday morning #programming #coffee",
            "Thanks to everyone who attended our webinar! #grateful #community",
            "Working on some exciting new features. Stay tuned! #development #excited",
            "Market analysis shows promising trends for Q4 #business #analytics",
            "Celebrating our team's achievements this quarter! #success #team",
            "New blog post is live! Check out our insights on digital transformation #blog"
        ]
        
        for i in range(count):
            content = sample_tweets[i % len(sample_tweets)]
            sentiment = TextBlob(content).sentiment
            hashtags = re.findall(r'#\w+', content)
            
            post = {
                'platform': 'twitter',
                'post_id': f"twitter_{i}_{username}",
                'content': content,
                'author': username,
                'timestamp': base_date + timedelta(hours=i*2),
                'likes': np.random.randint(10, 500),
                'shares': np.random.randint(5, 100),
                'comments': np.random.randint(2, 50),
                'reach': np.random.randint(1000, 10000),
                'impressions': np.random.randint(2000, 20000),
                'sentiment_score': sentiment.polarity,
                'sentiment_label': 'positive' if sentiment.polarity > 0.1 else 'negative' if sentiment.polarity < -0.1 else 'neutral',
                'hashtags': json.dumps(hashtags)
            }
            mock_posts.append(post)
            
        return mock_posts
    
    def generate_mock_facebook_data(self, page_id, count):
        """Generate mock Facebook data for demonstration."""
        mock_posts = []
        base_date = datetime.now() - timedelta(days=30)
        
        sample_posts = [
            "We're thrilled to announce our partnership with amazing companies!",
            "Behind the scenes: How we create our products with passion and dedication",
            "Customer success story: How we helped transform their business",
            "Team spotlight: Meet our incredible developers and designers",
            "Industry insights: The future of technology and innovation",
            "Thank you for 10,000 followers! Your support means everything to us",
            "New office tour: Take a look at our creative workspace",
            "Product update: Enhanced features based on your feedback",
            "Community event: Join us for our upcoming tech meetup",
            "Milestone celebration: Reflecting on our journey and growth"
        ]
        
        for i in range(count):
            content = sample_posts[i % len(sample_posts)]
            sentiment = TextBlob(content).sentiment
            
            post = {
                'platform': 'facebook',
                'post_id': f"facebook_{i}_{page_id}",
                'content': content,
                'author': page_id,
                'timestamp': base_date + timedelta(hours=i*3),
                'likes': np.random.randint(20, 800),
                'shares': np.random.randint(5, 200),
                'comments': np.random.randint(5, 100),
                'reach': np.random.randint(2000, 15000),
                'impressions': np.random.randint(3000, 25000),
                'sentiment_score': sentiment.polarity,
                'sentiment_label': 'positive' if sentiment.polarity > 0.1 else 'negative' if sentiment.polarity < -0.1 else 'neutral',
                'hashtags': json.dumps([])
            }
            mock_posts.append(post)
            
        return mock_posts
    
    def generate_mock_instagram_data(self, username, count):
        """Generate mock Instagram data for demonstration."""
        mock_posts = []
        base_date = datetime.now() - timedelta(days=30)
        
        sample_posts = [
            "Monday motivation! Starting the week with positive energy ✨ #motivation #mondayvibes",
            "Behind the scenes of our creative process 🎨 #creativity #process #design",
            "Coffee break essentials ☕ What's your favorite brew? #coffee #lifestyle",
            "Team building adventure! 🏔️ #team #adventure #outdoors #fun",
            "New product reveal coming soon! Stay tuned 👀 #comingsoon #excited #newproduct",
            "Grateful for our amazing community! 🙏 #grateful #community #love",
            "Weekend vibes: Relaxing and recharging 🌿 #weekend #selfcare #nature",
            "Innovation in action! Working on game-changing solutions 💡 #innovation #tech",
            "Celebrating small wins and big dreams! 🎉 #success #dreams #celebration",
            "Sunset reflections and future planning 🌅 #sunset #planning #goals"
        ]
        
        for i in range(count):
            content = sample_posts[i % len(sample_posts)]
            sentiment = TextBlob(content).sentiment
            hashtags = re.findall(r'#\w+', content)
            
            post = {
                'platform': 'instagram',
                'post_id': f"instagram_{i}_{username}",
                'content': content,
                'author': username,
                'timestamp': base_date + timedelta(hours=i*4),
                'likes': np.random.randint(50, 1200),
                'shares': 0,
                'comments': np.random.randint(10, 150),
                'reach': np.random.randint(1500, 12000),
                'impressions': np.random.randint(2500, 20000),
                'sentiment_score': sentiment.polarity,
                'sentiment_label': 'positive' if sentiment.polarity > 0.1 else 'negative' if sentiment.polarity < -0.1 else 'neutral',
                'hashtags': json.dumps(hashtags)
            }
            mock_posts.append(post)
            
        return mock_posts
    
    def save_posts_to_db(self, posts_data):
        """Save posts data to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for post in posts_data:
            # Calculate engagement rate
            total_engagement = post['likes'] + post['shares'] + post['comments']
            reach = post.get('reach', 1000)
            engagement_rate = (total_engagement / reach) * 100 if reach > 0 else 0
            post['engagement_rate'] = engagement_rate
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO posts 
                    (platform, post_id, content, author, timestamp, likes, shares, 
                     comments, reach, impressions, engagement_rate, sentiment_score, 
                     sentiment_label, hashtags, mentions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post['platform'], post['post_id'], post['content'], post['author'],
                    post['timestamp'], post['likes'], post['shares'], post['comments'],
                    post.get('reach', 0), post.get('impressions', 0), engagement_rate,
                    post['sentiment_score'], post['sentiment_label'],
                    post.get('hashtags', '[]'), post.get('mentions', '[]')
                ))
            except Exception as e:
                print(f"Error saving post {post['post_id']}: {e}")
                
        conn.commit()
        conn.close()
    
    def analyze_engagement_patterns(self, platform=None, days=30):
        """Analyze engagement patterns across platforms."""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                platform,
                DATE(timestamp) as date,
                AVG(engagement_rate) as avg_engagement,
                SUM(likes) as total_likes,
                SUM(shares) as total_shares,
                SUM(comments) as total_comments,
                COUNT(*) as post_count
            FROM posts 
            WHERE timestamp >= date('now', '-{} days')
        '''.format(days)
        
        if platform:
            query += f" AND platform = '{platform}'"
            
        query += " GROUP BY platform, DATE(timestamp) ORDER BY date"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def analyze_sentiment_trends(self, platform=None, days=30):
        """Analyze sentiment trends over time."""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                platform,
                DATE(timestamp) as date,
                sentiment_label,
                COUNT(*) as count,
                AVG(sentiment_score) as avg_sentiment
            FROM posts 
            WHERE timestamp >= date('now', '-{} days')
        '''.format(days)
        
        if platform:
            query += f" AND platform = '{platform}'"
            
        query += " GROUP BY platform, DATE(timestamp), sentiment_label ORDER BY date"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def analyze_hashtag_performance(self, platform=None, limit=20):
        """Analyze hashtag performance and popularity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT hashtags, engagement_rate, likes, shares, comments
            FROM posts 
            WHERE hashtags != '[]' AND hashtags IS NOT NULL
        '''
        
        if platform:
            query += f" AND platform = '{platform}'"
            
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        hashtag_stats = {}
        
        for hashtags_json, engagement, likes, shares, comments in results:
            try:
                hashtags = json.loads(hashtags_json)
                for hashtag in hashtags:
                    hashtag = hashtag.lower().replace('#', '')
                    if hashtag not in hashtag_stats:
                        hashtag_stats[hashtag] = {
                            'usage_count': 0,
                            'total_engagement': 0,
                            'total_likes': 0,
                            'total_shares': 0,
                            'total_comments': 0
                        }
                    
                    hashtag_stats[hashtag]['usage_count'] += 1
                    hashtag_stats[hashtag]['total_engagement'] += engagement
                    hashtag_stats[hashtag]['total_likes'] += likes
                    hashtag_stats[hashtag]['total_shares'] += shares
                    hashtag_stats[hashtag]['total_comments'] += comments
            except:
                continue
        
        # Calculate average engagement per hashtag
        for hashtag, stats in hashtag_stats.items():
            if stats['usage_count'] > 0:
                stats['avg_engagement'] = stats['total_engagement'] / stats['usage_count']
            else:
                stats['avg_engagement'] = 0
        
        # Sort by average engagement and usage
        sorted_hashtags = sorted(
            hashtag_stats.items(),
            key=lambda x: (x[1]['avg_engagement'], x[1]['usage_count']),
            reverse=True
        )
        
        return sorted_hashtags[:limit]
    
    def generate_content_insights(self, platform=None, days=30):
        """Generate insights about content performance."""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                content,
                engagement_rate,
                likes,
                shares,
                comments,
                sentiment_label,
                LENGTH(content) as content_length
            FROM posts 
            WHERE timestamp >= date('now', '-{} days')
        '''.format(days)
        
        if platform:
            query += f" AND platform = '{platform}'"
            
        query += " ORDER BY engagement_rate DESC"
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return {}
        
        insights = {
            'best_performing_posts': df.head(5).to_dict('records'),
            'worst_performing_posts': df.tail(5).to_dict('records'),
            'avg_engagement_by_sentiment': df.groupby('sentiment_label')['engagement_rate'].mean().to_dict(),
            'content_length_analysis': {
                'avg_length': df['content_length'].mean(),
                'length_engagement_correlation': df['content_length'].corr(df['engagement_rate'])
            },
            'engagement_stats': {
                'avg_engagement': df['engagement_rate'].mean(),
                'max_engagement': df['engagement_rate'].max(),
                'min_engagement': df['engagement_rate'].min()
            }
        }
        
        return insights
    
    def create_competitor_analysis(self, competitors_data):
        """Analyze competitor performance."""
        analysis = {
            'follower_comparison': {},
            'engagement_comparison': {},
            'posting_frequency': {},
            'content_analysis': {}
        }
        
        for competitor in competitors_data:
            name = competitor['name']
            analysis['follower_comparison'][name] = competitor.get('followers', 0)
            analysis['engagement_comparison'][name] = competitor.get('engagement_rate', 0)
            analysis['posting_frequency'][name] = competitor.get('posts_count', 0)
        
        return analysis
    
    def generate_recommendations(self):
        """Generate AI-powered recommendations for social media strategy."""
        insights = self.generate_content_insights(days=30)
        hashtag_performance = self.analyze_hashtag_performance()
        engagement_patterns = self.analyze_engagement_patterns()
        
        recommendations = {
            'content_strategy': [],
            'posting_schedule': [],
            'hashtag_strategy': [],
            'engagement_tactics': []
        }
        
        # Content strategy recommendations
        if insights.get('avg_engagement_by_sentiment'):
            best_sentiment = max(insights['avg_engagement_by_sentiment'].items(), key=lambda x: x[1])
            recommendations['content_strategy'].append(
                f"Focus on {best_sentiment[0]} content - it has {best_sentiment[1]:.1f}% higher engagement"
            )
        
        # Hashtag recommendations
        if hashtag_performance:
            top_hashtags = [f"#{tag[0]}" for tag in hashtag_performance[:5]]
            recommendations['hashtag_strategy'].append(
                f"Use high-performing hashtags: {', '.join(top_hashtags)}"
            )
        
        # Posting schedule recommendations
        if not engagement_patterns.empty:
            best_platform = engagement_patterns.groupby('platform')['avg_engagement'].mean().idxmax()
            recommendations['posting_schedule'].append(
                f"Focus more content on {best_platform} - highest average engagement"
            )
        
        return recommendations

class SocialMediaDashboard:
    def __init__(self):
        """Initialize the Flask web dashboard."""
        self.app = Flask(__name__)
        self.analytics_api = SocialMediaAnalyticsAPI()
        self.setup_routes()
        
    def setup_routes(self):
        """Setup Flask routes for the dashboard."""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page."""
            return render_template('dashboard.html')
        
        @self.app.route('/api/overview')
        def api_overview():
            """API endpoint for overview statistics."""
            conn = sqlite3.connect(self.analytics_api.db_path)
            
            # Get overview stats
            query = '''
                SELECT 
                    platform,
                    COUNT(*) as total_posts,
                    AVG(engagement_rate) as avg_engagement,
                    SUM(likes) as total_likes,
                    SUM(shares) as total_shares,
                    SUM(comments) as total_comments
                FROM posts 
                GROUP BY platform
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            return jsonify(df.to_dict('records'))
        
        @self.app.route('/api/engagement-chart')
        def api_engagement_chart():
            """API endpoint for engagement chart data."""
            df = self.analytics_api.analyze_engagement_patterns(days=30)
            
            fig = px.line(df, x='date', y='avg_engagement', color='platform',
                         title='Engagement Rate Over Time')
            
            graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
            return graphJSON
        
        @self.app.route('/api/sentiment-chart')
        def api_sentiment_chart():
            """API endpoint for sentiment analysis chart."""
            df = self.analytics_api.analyze_sentiment_trends(days=30)
            
            sentiment_summary = df.groupby(['platform', 'sentiment_label'])['count'].sum().reset_index()
            
            fig = px.sunburst(sentiment_summary, path=['platform', 'sentiment_label'], 
                            values='count', title='Sentiment Distribution by Platform')
            
            graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
            return graphJSON
        
        @self.app.route('/api/hashtag-performance')
        def api_hashtag_performance():
            """API endpoint for hashtag performance data."""
            hashtags = self.analytics_api.analyze_hashtag_performance(limit=15)
            
            hashtag_data = [
                {
                    'hashtag': f"#{tag[0]}",
                    'usage_count': tag[1]['usage_count'],
                    'avg_engagement': tag[1]['avg_engagement'],
                    'total_likes': tag[1]['total_likes']
                }
                for tag in hashtags
            ]
            
            return jsonify(hashtag_data)
        
        @self.app.route('/api/content-insights')
        def api_content_insights():
            """API endpoint for content insights."""
            insights = self.analytics_api.generate_content_insights(days=30)
            return jsonify(insights)
        
        @self.app.route('/api/recommendations')
        def api_recommendations():
            """API endpoint for AI recommendations."""
            recommendations = self.analytics_api.generate_recommendations()
            return jsonify(recommendations)
        
        @self.app.route('/api/fetch-data', methods=['POST'])
        def api_fetch_data():
            """API endpoint to fetch new social media data."""
            data = request.json
            platform = data.get('platform')
            username = data.get('username')
            
            try:
                if platform == 'twitter':
                    posts = self.analytics_api.fetch_twitter_data(username, 50)
                elif platform == 'facebook':
                    posts = self.analytics_api.fetch_facebook_data(username, 50)
                elif platform == 'instagram':
                    posts = self.analytics_api.fetch_instagram_data(username, 50)
                else:
                    return jsonify({'error': 'Invalid platform'}), 400
                
                self.analytics_api.save_posts_to_db(posts)
                
                return jsonify({
                    'success': True,
                    'message': f'Fetched {len(posts)} posts from {platform}',
                    'posts_count': len(posts)
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/generate-report')
        def api_generate_report():
            """API endpoint to generate comprehensive report."""
            # Generate comprehensive analytics report
            overview = self.analytics_api.analyze_engagement_patterns(days=30)
            sentiment = self.analytics_api.analyze_sentiment_trends(days=30)
            hashtags = self.analytics_api.analyze_hashtag_performance()
            insights = self.analytics_api.generate_content_insights(days=30)
            recommendations = self.analytics_api.generate_recommendations()
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'period': '30 days',
                'overview': overview.to_dict('records') if not overview.empty else [],
                'sentiment_analysis': sentiment.to_dict('records') if not sentiment.empty else [],
                'top_hashtags': hashtags[:10],
                'content_insights': insights,
                'recommendations': recommendations
            }
            
            return jsonify(report)
    
    def create_dashboard_template(self):
        """Create the HTML template for the dashboard."""
        template_dir = 'templates'
        import os
        os.makedirs(template_dir, exist_ok=True)
        
        html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Media Analytics Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .card { box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075); border: none; }
        .stat-card { text-align: center; padding: 20px; }
        .stat-number { font-size: 2rem; font-weight: bold; margin: 10px 0; }
        .chart-container { height: 400px; }
        .recommendations-list { max-height: 300px; overflow-y: auto; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-chart-line"></i> Social Media Analytics Dashboard
            </span>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- Overview Cards -->
        <div class="row mb-4" id="overview-cards">
            <!-- Cards will be populated by JavaScript -->
        </div>

        <!-- Data Fetching Section -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-download"></i> Fetch Social Media Data</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <select class="form-select" id="platform-select">
                                    <option value="twitter">Twitter</option>
                                    <option value="facebook">Facebook</option>
                                    <option value="instagram">Instagram</option>
                                </select>
                            </div>
                            <div class="col-md-6">
                                <input type="text" class="form-control" id="username-input" 
                                       placeholder="Enter username or page ID">
                            </div>
                            <div class="col-md-3">
                                <button class="btn btn-primary w-100" onclick="fetchSocialData()">
                                    <i class="fas fa-sync"></i> Fetch Data
                                </button>
                            </div>
                        </div>
                        <div id="fetch-status" class="mt-2"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Charts Section -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-line"></i> Engagement Trends</h5>
                    </div>
                    <div class="card-body">
                        <div id="engagement-chart" class="chart-container"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-smile"></i> Sentiment Analysis</h5>
                    </div>
                    <div class="card-body">
                        <div id="sentiment-chart" class="chart-container"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Hashtags and Insights -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-hashtag"></i> Top Performing Hashtags</h5>
                    </div>
                    <div class="card-body">
                        <div id="hashtag-list"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-lightbulb"></i> AI Recommendations</h5>
                    </div>
                    <div class="card-body">
                        <div id="recommendations" class="recommendations-list"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Generate Report Button -->
        <div class="row mb-4">
            <div class="col-12 text-center">
                <button class="btn btn-success btn-lg" onclick="generateReport()">
                    <i class="fas fa-file-alt"></i> Generate Comprehensive Report
                </button>
            </div>
        </div>
    </div>

    <script>
        // Load dashboard data
        function loadDashboard() {
            loadOverview();
            loadEngagementChart();
            loadSentimentChart();
            loadHashtagPerformance();
            loadRecommendations();
        }

        function loadOverview() {
            $.get('/api/overview', function(data) {
                let cardsHtml = '';
                data.forEach(platform => {
                    cardsHtml += `
                        <div class="col-md-3">
                            <div class="card stat-card">
                                <h6 class="text-muted">${platform.platform.toUpperCase()}</h6>
                                <div class="stat-number text-primary">${platform.total_posts}</div>
                                <p class="mb-1">Total Posts</p>
                                <small class="text-muted">${platform.avg_engagement.toFixed(1)}% Avg Engagement</small>
                            </div>
                        </div>
                    `;
                });
                $('#overview-cards').html(cardsHtml);
            });
        }

        function loadEngagementChart() {
            $.get('/api/engagement-chart', function(graphJSON) {
                Plotly.newPlot('engagement-chart', JSON.parse(graphJSON));
            });
        }

        function loadSentimentChart() {
            $.get('/api/sentiment-chart', function(graphJSON) {
                Plotly.newPlot('sentiment-chart', JSON.parse(graphJSON));
            });
        }

        function loadHashtagPerformance() {
            $.get('/api/hashtag-performance', function(data) {
                let hashtagHtml = '<div class="list-group">';
                data.slice(0, 10).forEach(hashtag => {
                    hashtagHtml += `
                        <div class="list-group-item d-flex justify-content-between align-items-center">
                            <span><strong>${hashtag.hashtag}</strong></span>
                            <span>
                                <span class="badge bg-primary rounded-pill">${hashtag.usage_count} uses</span>
                                <span class="badge bg-success rounded-pill">${hashtag.avg_engagement.toFixed(1)}% engagement</span>
                            </span>
                        </div>
                    `;
                });
                hashtagHtml += '</div>';
                $('#hashtag-list').html(hashtagHtml);
            });
        }

        function loadRecommendations() {
            $.get('/api/recommendations', function(data) {
                let recHtml = '';
                Object.keys(data).forEach(category => {
                    if (data[category].length > 0) {
                        recHtml += `<h6 class="text-primary">${category.replace('_', ' ').toUpperCase()}</h6>`;
                        recHtml += '<ul class="list-group list-group-flush mb-3">';
                        data[category].forEach(rec => {
                            recHtml += `<li class="list-group-item">${rec}</li>`;
                        });
                        recHtml += '</ul>';
                    }
                });
                $('#recommendations').html(recHtml);
            });
        }

        function fetchSocialData() {
            const platform = $('#platform-select').val();
            const username = $('#username-input').val();
            
            if (!username) {
                alert('Please enter a username or page ID');
                return;
            }

            $('#fetch-status').html('<div class="alert alert-info">Fetching data...</div>');

            $.ajax({
                url: '/api/fetch-data',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({platform: platform, username: username}),
                success: function(response) {
                    $('#fetch-status').html(`
                        <div class="alert alert-success">
                            ${response.message} - ${response.posts_count} posts processed
                        </div>
                    `);
                    // Reload dashboard after fetching new data
                    setTimeout(loadDashboard, 1000);
                },
                error: function(xhr) {
                    const error = xhr.responseJSON ? xhr.responseJSON.error : 'Unknown error';
                    $('#fetch-status').html(`<div class="alert alert-danger">Error: ${error}</div>`);
                }
            });
        }

        function generateReport() {
            $.get('/api/generate-report', function(data) {
                // Create and download report
                const reportContent = JSON.stringify(data, null, 2);
                const blob = new Blob([reportContent], {type: 'application/json'});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `social_media_report_${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                window.URL.revokeObjectURL(url);
            });
        }

        // Load dashboard on page load
        $(document).ready(function() {
            loadDashboard();
        });
    </script>
</body>
</html>
        '''
        
        with open(os.path.join(template_dir, 'dashboard.html'), 'w') as f:
            f.write(html_template)
    
    def run(self, host='localhost', port=5000, debug=True):
        """Run the Flask dashboard."""
        self.create_dashboard_template()
        print(f"🚀 Social Media Analytics Dashboard starting...")
        print(f"📊 Access the dashboard at: http://{host}:{port}")
        print("🔗 Features available:")
        print("   - Real-time social media data fetching")
        print("   - Engagement and sentiment analytics")
        print("   - Hashtag performance analysis")
        print("   - AI-powered recommendations")
        print("   - Comprehensive reporting")
        
        self.app.run(host=host, port=port, debug=debug)

def main():
    """Main function to run the Social Media Analytics Dashboard."""
    print("📱 Social Media Analytics Dashboard")
    print("=" * 50)
    
    # Initialize the analytics system
    analytics = SocialMediaAnalyticsAPI()
    
    print("\nChoose interface:")
    print("1. Web Dashboard (Recommended)")
    print("2. Command Line Interface")
    print("3. Generate Sample Data & Run Dashboard")
    
    choice = input("\nEnter choice (1-3): ")
    
    if choice == '3':
        # Generate sample data for demonstration
        print("\n📊 Generating sample data...")
        
        # Generate sample data for multiple platforms
        twitter_data = analytics.generate_mock_twitter_data("tech_company", 30)
        facebook_data = analytics.generate_mock_facebook_data("tech_company_page", 25)
        instagram_data = analytics.generate_mock_instagram_data("tech_company_insta", 20)
        
        # Save to database
        analytics.save_posts_to_db(twitter_data + facebook_data + instagram_data)
        
        print("✅ Sample data generated and saved to database")
        print("🚀 Starting web dashboard...")
        
        # Run dashboard
        dashboard = SocialMediaDashboard()
        dashboard.run()
        
    elif choice == '2':
        # Command line interface
        try:
            while True:
                print("\n📋 Social Media Analytics Menu:")
                print("1. Fetch Twitter Data")
                print("2. Fetch Facebook Data")
                print("3. Fetch Instagram Data")
                print("4. View Engagement Analysis")
                print("5. View Sentiment Analysis")
                print("6. View Hashtag Performance")
                print("7. Generate Insights")
                print("8. Get Recommendations")
                print("9. Generate Report")
                print("10. Exit")
                
                cmd_choice = input("\nEnter choice (1-10): ")
                
                if cmd_choice == '1':
                    username = input("Enter Twitter username: ")
                    count = int(input("Number of tweets to fetch (default 50): ") or 50)
                    print("📊 Fetching Twitter data...")
                    data = analytics.fetch_twitter_data(username, count)
                    analytics.save_posts_to_db(data)
                    print(f"✅ Fetched and saved {len(data)} tweets")
                
                elif cmd_choice == '2':
                    page_id = input("Enter Facebook page ID: ")
                    count = int(input("Number of posts to fetch (default 50): ") or 50)
                    print("📊 Fetching Facebook data...")
                    data = analytics.fetch_facebook_data(page_id, count)
                    analytics.save_posts_to_db(data)
                    print(f"✅ Fetched and saved {len(data)} posts")
                
                elif cmd_choice == '3':
                    username = input("Enter Instagram username: ")
                    count = int(input("Number of posts to fetch (default 50): ") or 50)
                    print("📊 Fetching Instagram data...")
                    data = analytics.fetch_instagram_data(username, count)
                    analytics.save_posts_to_db(data)
                    print(f"✅ Fetched and saved {len(data)} posts")
                
                elif cmd_choice == '4':
                    df = analytics.analyze_engagement_patterns(days=30)
                    if not df.empty:
                        print("\n📈 Engagement Analysis:")
                        print(df.to_string(index=False))
                    else:
                        print("No data available for analysis")
                
                elif cmd_choice == '5':
                    df = analytics.analyze_sentiment_trends(days=30)
                    if not df.empty:
                        print("\n😊 Sentiment Analysis:")
                        print(df.to_string(index=False))
                    else:
                        print("No data available for analysis")
                
                elif cmd_choice == '6':
                    hashtags = analytics.analyze_hashtag_performance(limit=10)
                    print("\n#️⃣ Top Performing Hashtags:")
                    for i, (tag, stats) in enumerate(hashtags, 1):
                        print(f"{i}. #{tag} - {stats['usage_count']} uses, {stats['avg_engagement']:.1f}% avg engagement")
                
                elif cmd_choice == '7':
                    insights = analytics.generate_content_insights(days=30)
                    print("\n💡 Content Insights:")
                    print(json.dumps(insights, indent=2, default=str))
                
                elif cmd_choice == '8':
                    recommendations = analytics.generate_recommendations()
                    print("\n🤖 AI Recommendations:")
                    for category, recs in recommendations.items():
                        if recs:
                            print(f"\n{category.replace('_', ' ').title()}:")
                            for rec in recs:
                                print(f"  • {rec}")
                
                elif cmd_choice == '9':
                    print("\n📄 Generating comprehensive report...")
                    # Generate and save report
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"social_media_report_{timestamp}.json"
                    
                    report_data = {
                        'generated_at': datetime.now().isoformat(),
                        'engagement_analysis': analytics.analyze_engagement_patterns(days=30).to_dict('records'),
                        'sentiment_analysis': analytics.analyze_sentiment_trends(days=30).to_dict('records'),
                        'hashtag_performance': analytics.analyze_hashtag_performance(),
                        'content_insights': analytics.generate_content_insights(days=30),
                        'recommendations': analytics.generate_recommendations()
                    }
                    
                    with open(filename, 'w') as f:
                        json.dump(report_data, f, indent=2, default=str)
                    
                    print(f"✅ Report saved as {filename}")
                
                elif cmd_choice == '10':
                    print("👋 Thank you for using Social Media Analytics!")
                    break
                
                else:
                    print("❌ Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    else:
        # Run web dashboard
        dashboard = SocialMediaDashboard()
        dashboard.run()

if __name__ == "__main__":
    main()
