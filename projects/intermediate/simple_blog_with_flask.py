"""
Simple Blog with Flask

A Python application that simulates a simple blog using Flask.
Features include:
- Displaying a list of blog posts.
- Adding new blog posts.
- Viewing individual blog posts.
"""

import sys
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

def smoke_test():
    """Exercise every GET route once, without starting a server.

    `app.test_client()` dispatches a real request through the real application
    object -- no socket, no port, no waiting. A web project that cannot be
    driven this way cannot be tested either, so this is worth having whether or
    not anything is capturing the output.
    """
    print("smoke test: dispatching one request per route\n")
    with app.test_client() as client:
        rules = sorted(app.url_map.iter_rules(), key=lambda rule: str(rule))
        checked = 0
        for rule in rules:
            if "GET" not in rule.methods or rule.arguments:
                continue
            response = client.get(str(rule))
            body = response.get_data(as_text=True)
            body = " ".join(body.split())[:60]
            print(f"  GET {str(rule):26} {response.status_code}  {body}")
            checked += 1
    print(f"\n{checked} route(s) answered. Pass --serve to start the real "
          f"server instead.")


if __name__ == "__main__":
    # Serving is opt-in, because a run that never returns cannot be
    # tested or captured. With no arguments the file answers every
    # route once and exits; `--serve` starts the real server.
    if "--serve" in sys.argv:
        app.run(debug=True)
    else:
        smoke_test()
