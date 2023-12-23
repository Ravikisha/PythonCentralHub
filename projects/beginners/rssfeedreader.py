# RSS Feed Reader

import feedparser # pip install feedparser
import webbrowser

# RSS Feed URL
url = 'https://www.reddit.com/r/Python/.rss'

# Parse RSS Feed
feed = feedparser.parse(url)

# Print Feed Title
print(feed['feed']['title'])

# Print Entry Titles
for entry in feed['entries']:
    print(entry['title'])
    
# Open Entry Link in Browser
webbrowser.open(entry['link'])

# Print Entry Summary
print(entry['summary'])

# Print Entry Date
print(entry['published'])

# Print Entry Author
print(entry['author'])

# Print Entry Tags
for tag in entry['tags']:
    print(tag['term'])

# Print Entry ID
print(entry['id'])

# Print Entry Link
print(entry['link'])
