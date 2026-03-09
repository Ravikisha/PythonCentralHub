"""
Simple Blog with Flask

A Python application that simulates a simple blog using Flask.
Features include:
- Displaying a list of blog posts.
- Adding new blog posts.
- Viewing individual blog posts.
"""

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Sample data for blog posts
blog_posts = [
    {"id": 1, "title": "First Post", "content": "This is the content of the first post."},
    {"id": 2, "title": "Second Post", "content": "This is the content of the second post."},
]

@app.route('/')
def index():
    """Display the list of blog posts."""
    return render_template('index.html', posts=blog_posts)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    """View an individual blog post."""
    post = next((p for p in blog_posts if p['id'] == post_id), None)
    if post:
        return render_template('post.html', post=post)
    return "Post not found", 404

@app.route('/new', methods=['GET', 'POST'])
def new_post():
    """Add a new blog post."""
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_id = max(p['id'] for p in blog_posts) + 1 if blog_posts else 1
        blog_posts.append({"id": new_id, "title": title, "content": content})
        return redirect(url_for('index'))
    return render_template('new_post.html')

if __name__ == '__main__':
    app.run(debug=True)
