#!/usr/bin/env python3
"""
Reddit Bot using PRAW
A comprehensive Reddit bot for automated posting, commenting, and interaction.

Features:
- Automated posting to subreddits
- Comment monitoring and responses
- Keyword-based interactions
- Subreddit analytics
- Content moderation assistance
- Scheduled posting

Requirements:
- praw
- schedule
- configparser
- datetime

Author: Python Central Hub
Date: 2025-09-05
"""

import praw
import schedule
import time
import random
import re
import json
import os
from datetime import datetime, timedelta
from configparser import ConfigParser
import logging


class RedditBot:
    """Automated Reddit bot for various interactions and tasks."""
    
    def __init__(self, config_file="reddit_config.ini"):
        self.config = self.load_config(config_file)
        self.reddit = None
        self.subreddit_cache = {}
        self.response_templates = self.load_response_templates()
        self.setup_logging()
        self.authenticate()
    
    def load_config(self, config_file):
        """Load Reddit API configuration."""
        config = ConfigParser()
        
        # Create default config if doesn't exist
        if not os.path.exists(config_file):
            self.create_default_config(config_file)
        
        config.read(config_file)
        return config
    
    def create_default_config(self, config_file):
        """Create a default configuration file template."""
        config = ConfigParser()
        config['reddit'] = {
            'client_id': 'your_client_id_here',
            'client_secret': 'your_client_secret_here',
            'password': 'your_password_here',
            'user_agent': 'PythonBot v1.0 by /u/YourUsername',
            'username': 'your_username_here'
        }
        config['settings'] = {
            'target_subreddits': 'test,pythonlearning',
            'keywords': 'python,programming,help',
            'max_posts_per_hour': '5',
            'max_comments_per_hour': '10',
            'enable_auto_post': 'false',
            'enable_auto_comment': 'false'
        }
        
        with open(config_file, 'w') as f:
            config.write(f)
        
        print(f"⚠️  Default config created at {config_file}")
        print("Please update with your Reddit API credentials!")
    
    def setup_logging(self):
        """Setup logging for bot activities."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('reddit_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def authenticate(self):
        """Authenticate with Reddit API using PRAW."""
        try:
            self.reddit = praw.Reddit(
                client_id=self.config['reddit']['client_id'],
                client_secret=self.config['reddit']['client_secret'],
                password=self.config['reddit']['password'],
                user_agent=self.config['reddit']['user_agent'],
                username=self.config['reddit']['username']
            )
            
            # Test authentication
            self.reddit.user.me()
            self.logger.info(f"✅ Successfully authenticated as {self.reddit.user.me()}")
            
        except Exception as e:
            self.logger.error(f"❌ Authentication failed: {e}")
            self.reddit = None
    
    def load_response_templates(self):
        """Load response templates for automated comments."""
        return {
            'python_help': [
                "Great question! Here are some resources that might help:\n\n"
                "- [Python Documentation](https://docs.python.org/3/)\n"
                "- [Real Python Tutorials](https://realpython.com/)\n"
                "- r/learnpython is also a great community!\n\n"
                "Good luck with your Python journey! 🐍",
                
                "I see you're working with Python! Here are some tips:\n\n"
                "1. Check the official docs first\n"
                "2. Use print() statements to debug\n"
                "3. Break down complex problems into smaller parts\n\n"
                "Feel free to ask if you need more specific help!",
            ],
            'programming_encouragement': [
                "Keep coding! Programming is a journey of continuous learning. 💻",
                "Great progress! Remember, every expert was once a beginner. 🚀",
                "Debugging is like detective work - you'll get better with practice! 🔍",
            ],
            'general_help': [
                "Happy to help! What specific issue are you facing?",
                "Could you provide more details about your problem?",
                "Have you tried checking the documentation for this?",
            ]
        }
    
    def get_target_subreddits(self):
        """Get list of target subreddits from config."""
        subreddits = self.config['settings']['target_subreddits'].split(',')
        return [sub.strip() for sub in subreddits]
    
    def get_keywords(self):
        """Get list of keywords to monitor from config."""
        keywords = self.config['settings']['keywords'].split(',')
        return [keyword.strip().lower() for keyword in keywords]
    
    def search_posts(self, subreddit_name, query, limit=10):
        """Search for posts in a subreddit based on query."""
        if not self.reddit:
            return []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = list(subreddit.search(query, limit=limit, sort='new'))
            return posts
        except Exception as e:
            self.logger.error(f"Error searching posts in r/{subreddit_name}: {e}")
            return []
    
    def monitor_new_posts(self, subreddit_name, limit=25):
        """Monitor new posts in a subreddit for keyword matches."""
        if not self.reddit:
            return []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            new_posts = list(subreddit.new(limit=limit))
            keywords = self.get_keywords()
            
            matching_posts = []
            for post in new_posts:
                title_lower = post.title.lower()
                selftext_lower = post.selftext.lower()
                
                for keyword in keywords:
                    if keyword in title_lower or keyword in selftext_lower:
                        matching_posts.append(post)
                        break
            
            return matching_posts
            
        except Exception as e:
            self.logger.error(f"Error monitoring r/{subreddit_name}: {e}")
            return []
    
    def auto_comment(self, post, response_type='general_help'):
        """Automatically comment on a post with helpful response."""
        if not self.reddit:
            return False
        
        try:
            # Check if we've already commented on this post
            post.comments.replace_more(limit=0)
            for comment in post.comments:
                if comment.author and comment.author.name == self.reddit.user.me().name:
                    self.logger.info(f"Already commented on post: {post.title[:50]}...")
                    return False
            
            # Select random response from template
            templates = self.response_templates.get(response_type, self.response_templates['general_help'])
            response = random.choice(templates)
            
            # Add comment
            post.reply(response)
            self.logger.info(f"✅ Commented on post: {post.title[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Error commenting on post: {e}")
            return False
    
    def create_post(self, subreddit_name, title, content, is_self_post=True):
        """Create a new post in specified subreddit."""
        if not self.reddit:
            return False
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            if is_self_post:
                post = subreddit.submit(title=title, selftext=content)
            else:
                # For link posts
                post = subreddit.submit(title=title, url=content)
            
            self.logger.info(f"✅ Created post in r/{subreddit_name}: {title}")
            return post
            
        except Exception as e:
            self.logger.error(f"Error creating post in r/{subreddit_name}: {e}")
            return False
    
    def get_subreddit_stats(self, subreddit_name):
        """Get statistics about a subreddit."""
        if not self.reddit:
            return None
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            stats = {
                'name': subreddit.display_name,
                'subscribers': subreddit.subscribers,
                'description': subreddit.description[:200] + '...' if len(subreddit.description) > 200 else subreddit.description,
                'created_utc': datetime.fromtimestamp(subreddit.created_utc),
                'over18': subreddit.over18,
                'active_users': subreddit.active_user_count
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting stats for r/{subreddit_name}: {e}")
            return None
    
    def analyze_user(self, username):
        """Analyze a Reddit user's activity."""
        if not self.reddit:
            return None
        
        try:
            user = self.reddit.redditor(username)
            
            # Get recent submissions and comments
            submissions = list(user.submissions.new(limit=10))
            comments = list(user.comments.new(limit=10))
            
            analysis = {
                'username': user.name,
                'comment_karma': user.comment_karma,
                'link_karma': user.link_karma,
                'created_utc': datetime.fromtimestamp(user.created_utc),
                'recent_submissions': len(submissions),
                'recent_comments': len(comments),
                'most_active_subreddits': self.get_user_subreddits(submissions + comments)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing user {username}: {e}")
            return None
    
    def get_user_subreddits(self, user_content):
        """Get list of subreddits where user is most active."""
        subreddit_counts = {}
        
        for item in user_content:
            subreddit_name = item.subreddit.display_name
            subreddit_counts[subreddit_name] = subreddit_counts.get(subreddit_name, 0) + 1
        
        # Sort by count and return top 5
        sorted_subreddits = sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_subreddits[:5]
    
    def schedule_post(self, subreddit_name, title, content, post_time):
        """Schedule a post for future publishing."""
        def post_job():
            self.create_post(subreddit_name, title, content)
        
        schedule.every().day.at(post_time).do(post_job)
        self.logger.info(f"📅 Scheduled post for {post_time}: {title}")
    
    def run_monitoring_cycle(self):
        """Run one cycle of monitoring and interactions."""
        if not self.reddit:
            self.logger.warning("Reddit not authenticated. Skipping monitoring cycle.")
            return
        
        target_subreddits = self.get_target_subreddits()
        
        for subreddit_name in target_subreddits:
            self.logger.info(f"🔍 Monitoring r/{subreddit_name}...")
            
            # Monitor new posts
            matching_posts = self.monitor_new_posts(subreddit_name)
            
            for post in matching_posts[:3]:  # Limit to 3 posts per subreddit
                # Determine response type based on keywords
                title_lower = post.title.lower()
                if 'python' in title_lower or 'help' in title_lower:
                    response_type = 'python_help'
                elif any(word in title_lower for word in ['learning', 'beginner', 'new']):
                    response_type = 'programming_encouragement'
                else:
                    response_type = 'general_help'
                
                # Auto-comment if enabled
                if self.config.getboolean('settings', 'enable_auto_comment', fallback=False):
                    self.auto_comment(post, response_type)
                    time.sleep(2)  # Rate limiting
    
    def start_scheduled_monitoring(self):
        """Start scheduled monitoring with rate limiting."""
        # Schedule monitoring every 30 minutes
        schedule.every(30).minutes.do(self.run_monitoring_cycle)
        
        self.logger.info("🤖 Reddit bot monitoring started...")
        print("Bot is running! Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("🛑 Bot monitoring stopped by user.")


def interactive_mode():
    """Run bot in interactive mode for manual operations."""
    bot = RedditBot()
    
    if not bot.reddit:
        print("❌ Failed to authenticate. Please check your configuration.")
        return
    
    while True:
        print("\n🤖 Reddit Bot - Interactive Mode")
        print("=" * 40)
        print("1. Search posts")
        print("2. Monitor subreddit")
        print("3. Create post")
        print("4. Get subreddit stats")
        print("5. Analyze user")
        print("6. Start automated monitoring")
        print("7. Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == '1':
            subreddit = input("Enter subreddit name: ").strip()
            query = input("Enter search query: ").strip()
            limit = int(input("Number of results (default 10): ") or 10)
            
            posts = bot.search_posts(subreddit, query, limit)
            print(f"\n📊 Found {len(posts)} posts:")
            for i, post in enumerate(posts, 1):
                print(f"{i}. {post.title[:60]}... (Score: {post.score})")
        
        elif choice == '2':
            subreddit = input("Enter subreddit name: ").strip()
            posts = bot.monitor_new_posts(subreddit)
            print(f"\n📊 Found {len(posts)} matching posts:")
            for i, post in enumerate(posts, 1):
                print(f"{i}. {post.title[:60]}...")
        
        elif choice == '3':
            subreddit = input("Enter subreddit name: ").strip()
            title = input("Enter post title: ").strip()
            content = input("Enter post content: ").strip()
            
            result = bot.create_post(subreddit, title, content)
            if result:
                print(f"✅ Post created successfully!")
            else:
                print("❌ Failed to create post.")
        
        elif choice == '4':
            subreddit = input("Enter subreddit name: ").strip()
            stats = bot.get_subreddit_stats(subreddit)
            
            if stats:
                print(f"\n📊 r/{stats['name']} Statistics:")
                print(f"Subscribers: {stats['subscribers']:,}")
                print(f"Active users: {stats['active_users']}")
                print(f"Created: {stats['created_utc'].strftime('%Y-%m-%d')}")
                print(f"NSFW: {stats['over18']}")
                print(f"Description: {stats['description']}")
        
        elif choice == '5':
            username = input("Enter username: ").strip()
            analysis = bot.analyze_user(username)
            
            if analysis:
                print(f"\n👤 u/{analysis['username']} Analysis:")
                print(f"Comment Karma: {analysis['comment_karma']:,}")
                print(f"Link Karma: {analysis['link_karma']:,}")
                print(f"Account Age: {analysis['created_utc'].strftime('%Y-%m-%d')}")
                print(f"Recent Activity: {analysis['recent_submissions']} posts, {analysis['recent_comments']} comments")
                print("Most Active Subreddits:")
                for subreddit, count in analysis['most_active_subreddits']:
                    print(f"  - r/{subreddit}: {count} posts/comments")
        
        elif choice == '6':
            print("🚀 Starting automated monitoring...")
            bot.start_scheduled_monitoring()
        
        elif choice == '7':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice! Please select 1-7.")


def main():
    """Main function to run Reddit bot."""
    print("🤖 Reddit Bot - PRAW Edition")
    print("=" * 40)
    
    mode = input("Run in (i)nteractive or (a)utomated mode? [i/a]: ").strip().lower()
    
    if mode == 'a':
        bot = RedditBot()
        bot.start_scheduled_monitoring()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
