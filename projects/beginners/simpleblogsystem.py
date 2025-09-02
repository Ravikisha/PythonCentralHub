# Simple Blog System

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class BlogPost:
    def __init__(self, title: str, content: str, author: str = "Anonymous", post_id: str = None):
        self.id = post_id or str(int(datetime.now().timestamp()))
        self.title = title
        self.content = content
        self.author = author
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.tags = []
        self.published = False
    
    def to_dict(self) -> Dict:
        """Convert blog post to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'tags': self.tags,
            'published': self.published
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BlogPost':
        """Create blog post from dictionary"""
        post = cls(data['title'], data['content'], data['author'], data['id'])
        post.created_at = data['created_at']
        post.updated_at = data['updated_at']
        post.tags = data.get('tags', [])
        post.published = data.get('published', False)
        return post
    
    def add_tag(self, tag: str):
        """Add a tag to the post"""
        if tag.lower() not in [t.lower() for t in self.tags]:
            self.tags.append(tag)
            self.updated_at = datetime.now().isoformat()
    
    def remove_tag(self, tag: str):
        """Remove a tag from the post"""
        self.tags = [t for t in self.tags if t.lower() != tag.lower()]
        self.updated_at = datetime.now().isoformat()
    
    def publish(self):
        """Publish the post"""
        self.published = True
        self.updated_at = datetime.now().isoformat()
    
    def unpublish(self):
        """Unpublish the post"""
        self.published = False
        self.updated_at = datetime.now().isoformat()
    
    def update_content(self, title: str = None, content: str = None):
        """Update post content"""
        if title:
            self.title = title
        if content:
            self.content = content
        self.updated_at = datetime.now().isoformat()

class SimpleBlogSystem:
    def __init__(self, data_file: str = "blog_data.json"):
        self.data_file = data_file
        self.posts = []
        self.load_posts()
    
    def load_posts(self):
        """Load posts from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.posts = [BlogPost.from_dict(post_data) for post_data in data]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading posts: {e}")
                self.posts = []
    
    def save_posts(self):
        """Save posts to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([post.to_dict() for post in self.posts], f, indent=2)
        except Exception as e:
            print(f"Error saving posts: {e}")
    
    def create_post(self, title: str, content: str, author: str = "Anonymous") -> BlogPost:
        """Create a new blog post"""
        post = BlogPost(title, content, author)
        self.posts.append(post)
        self.save_posts()
        return post
    
    def get_post_by_id(self, post_id: str) -> Optional[BlogPost]:
        """Get a post by its ID"""
        for post in self.posts:
            if post.id == post_id:
                return post
        return None
    
    def get_all_posts(self, published_only: bool = False) -> List[BlogPost]:
        """Get all posts, optionally filtered by published status"""
        if published_only:
            return [post for post in self.posts if post.published]
        return self.posts.copy()
    
    def get_posts_by_author(self, author: str) -> List[BlogPost]:
        """Get all posts by a specific author"""
        return [post for post in self.posts if post.author.lower() == author.lower()]
    
    def get_posts_by_tag(self, tag: str) -> List[BlogPost]:
        """Get all posts with a specific tag"""
        return [post for post in self.posts if tag.lower() in [t.lower() for t in post.tags]]
    
    def search_posts(self, query: str) -> List[BlogPost]:
        """Search posts by title or content"""
        query = query.lower()
        results = []
        for post in self.posts:
            if (query in post.title.lower() or 
                query in post.content.lower() or 
                query in post.author.lower()):
                results.append(post)
        return results
    
    def delete_post(self, post_id: str) -> bool:
        """Delete a post by ID"""
        post = self.get_post_by_id(post_id)
        if post:
            self.posts.remove(post)
            self.save_posts()
            return True
        return False
    
    def get_post_statistics(self) -> Dict:
        """Get blog statistics"""
        total_posts = len(self.posts)
        published_posts = len([p for p in self.posts if p.published])
        authors = set(post.author for post in self.posts)
        all_tags = []
        for post in self.posts:
            all_tags.extend(post.tags)
        unique_tags = set(all_tags)
        
        return {
            'total_posts': total_posts,
            'published_posts': published_posts,
            'draft_posts': total_posts - published_posts,
            'total_authors': len(authors),
            'total_tags': len(unique_tags),
            'most_common_tags': self._get_most_common_tags(all_tags)
        }
    
    def _get_most_common_tags(self, tags: List[str], limit: int = 5) -> List[tuple]:
        """Get most common tags"""
        tag_count = {}
        for tag in tags:
            tag_count[tag] = tag_count.get(tag, 0) + 1
        
        sorted_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_tags[:limit]
    
    def export_posts(self, filename: str, published_only: bool = True):
        """Export posts to a file"""
        posts = self.get_all_posts(published_only)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for post in posts:
                    f.write(f"Title: {post.title}\n")
                    f.write(f"Author: {post.author}\n")
                    f.write(f"Created: {post.created_at}\n")
                    f.write(f"Tags: {', '.join(post.tags)}\n")
                    f.write(f"Published: {'Yes' if post.published else 'No'}\n")
                    f.write("-" * 50 + "\n")
                    f.write(post.content)
                    f.write("\n" + "=" * 50 + "\n\n")
            
            print(f"Posts exported to {filename}")
        except Exception as e:
            print(f"Error exporting posts: {e}")

def display_post(post: BlogPost):
    """Display a single post"""
    print(f"\n{'='*60}")
    print(f"Title: {post.title}")
    print(f"Author: {post.author}")
    print(f"Created: {post.created_at}")
    print(f"Status: {'Published' if post.published else 'Draft'}")
    if post.tags:
        print(f"Tags: {', '.join(post.tags)}")
    print(f"{'='*60}")
    print(post.content)
    print(f"{'='*60}\n")

def main():
    """Main function to run the blog system"""
    blog = SimpleBlogSystem()
    
    while True:
        print("\n=== Simple Blog System ===")
        print("1. Create new post")
        print("2. View all posts")
        print("3. View published posts")
        print("4. Search posts")
        print("5. View post by ID")
        print("6. Edit post")
        print("7. Delete post")
        print("8. Manage tags")
        print("9. Publish/Unpublish post")
        print("10. View statistics")
        print("11. Export posts")
        print("0. Exit")
        
        try:
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                title = input("Enter post title: ").strip()
                if not title:
                    print("Title cannot be empty!")
                    continue
                
                author = input("Enter author name (or press Enter for Anonymous): ").strip()
                if not author:
                    author = "Anonymous"
                
                print("Enter post content (type 'END' on a new line to finish):")
                content_lines = []
                while True:
                    line = input()
                    if line.strip() == 'END':
                        break
                    content_lines.append(line)
                
                content = '\n'.join(content_lines)
                post = blog.create_post(title, content, author)
                print(f"Post created with ID: {post.id}")
            
            elif choice == '2':
                posts = blog.get_all_posts()
                if not posts:
                    print("No posts found.")
                else:
                    for post in posts:
                        display_post(post)
            
            elif choice == '3':
                posts = blog.get_all_posts(published_only=True)
                if not posts:
                    print("No published posts found.")
                else:
                    for post in posts:
                        display_post(post)
            
            elif choice == '4':
                query = input("Enter search query: ").strip()
                if query:
                    results = blog.search_posts(query)
                    if not results:
                        print("No posts found matching your query.")
                    else:
                        print(f"Found {len(results)} posts:")
                        for post in results:
                            display_post(post)
            
            elif choice == '5':
                post_id = input("Enter post ID: ").strip()
                post = blog.get_post_by_id(post_id)
                if post:
                    display_post(post)
                else:
                    print("Post not found.")
            
            elif choice == '6':
                post_id = input("Enter post ID to edit: ").strip()
                post = blog.get_post_by_id(post_id)
                if post:
                    print(f"Current title: {post.title}")
                    new_title = input("Enter new title (or press Enter to keep current): ").strip()
                    
                    print(f"Current content:\n{post.content}")
                    print("Enter new content (type 'END' on a new line to finish, or just 'END' to keep current):")
                    content_lines = []
                    while True:
                        line = input()
                        if line.strip() == 'END':
                            break
                        content_lines.append(line)
                    
                    new_content = '\n'.join(content_lines) if content_lines else None
                    
                    if new_title or new_content:
                        post.update_content(new_title if new_title else None, new_content)
                        blog.save_posts()
                        print("Post updated successfully!")
                    else:
                        print("No changes made.")
                else:
                    print("Post not found.")
            
            elif choice == '7':
                post_id = input("Enter post ID to delete: ").strip()
                post = blog.get_post_by_id(post_id)
                if post:
                    confirm = input(f"Are you sure you want to delete '{post.title}'? (y/N): ").strip().lower()
                    if confirm == 'y':
                        blog.delete_post(post_id)
                        print("Post deleted successfully!")
                    else:
                        print("Deletion cancelled.")
                else:
                    print("Post not found.")
            
            elif choice == '8':
                post_id = input("Enter post ID to manage tags: ").strip()
                post = blog.get_post_by_id(post_id)
                if post:
                    print(f"Current tags: {', '.join(post.tags) if post.tags else 'None'}")
                    print("1. Add tag")
                    print("2. Remove tag")
                    tag_choice = input("Enter choice: ").strip()
                    
                    if tag_choice == '1':
                        tag = input("Enter tag to add: ").strip()
                        if tag:
                            post.add_tag(tag)
                            blog.save_posts()
                            print("Tag added successfully!")
                    elif tag_choice == '2':
                        if post.tags:
                            tag = input("Enter tag to remove: ").strip()
                            if tag:
                                post.remove_tag(tag)
                                blog.save_posts()
                                print("Tag removed successfully!")
                        else:
                            print("No tags to remove.")
                else:
                    print("Post not found.")
            
            elif choice == '9':
                post_id = input("Enter post ID: ").strip()
                post = blog.get_post_by_id(post_id)
                if post:
                    current_status = "Published" if post.published else "Draft"
                    print(f"Current status: {current_status}")
                    
                    if post.published:
                        confirm = input("Unpublish this post? (y/N): ").strip().lower()
                        if confirm == 'y':
                            post.unpublish()
                            blog.save_posts()
                            print("Post unpublished!")
                    else:
                        confirm = input("Publish this post? (y/N): ").strip().lower()
                        if confirm == 'y':
                            post.publish()
                            blog.save_posts()
                            print("Post published!")
                else:
                    print("Post not found.")
            
            elif choice == '10':
                stats = blog.get_post_statistics()
                print("\n=== Blog Statistics ===")
                print(f"Total posts: {stats['total_posts']}")
                print(f"Published posts: {stats['published_posts']}")
                print(f"Draft posts: {stats['draft_posts']}")
                print(f"Total authors: {stats['total_authors']}")
                print(f"Total unique tags: {stats['total_tags']}")
                
                if stats['most_common_tags']:
                    print("\nMost common tags:")
                    for tag, count in stats['most_common_tags']:
                        print(f"  {tag}: {count}")
            
            elif choice == '11':
                filename = input("Enter filename for export (e.g., blog_export.txt): ").strip()
                if not filename:
                    filename = "blog_export.txt"
                
                published_only = input("Export only published posts? (Y/n): ").strip().lower()
                published_only = published_only != 'n'
                
                blog.export_posts(filename, published_only)
            
            elif choice == '0':
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
