"""
Simple Blog with Flask

A Python application that simulates a simple blog using Flask.
Features include:
- Displaying a list of blog posts.
- Adding new blog posts.
- Viewing individual blog posts.
"""

import os
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


# Flask looks for templates on disk, so a self-contained single-file project
# has to put them there before the first request. Keeping them as strings
# means the project stays one file; writing them at startup means Jinja can
# actually find them.
TEMPLATES = {
    "base.html": """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>{% block title %}Blog{% endblock %}</title>
<style>
 body { font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; }
 article { border-bottom: 1px solid #ddd; padding: 1rem 0; }
 a { color: #06c; }
</style></head>
<body>
<h1><a href="{{ url_for('index') }}">Simple Blog</a></h1>
{% block body %}{% endblock %}
</body></html>""",

    "index.html": """{% extends "base.html" %}
{% block body %}
<p><a href="{{ url_for('new_post') }}">Write a new post</a></p>
{% for post in posts %}
<article>
  <h2><a href="{{ url_for('view_post', post_id=post.id) }}">{{ post.title }}</a></h2>
  <p>{{ post.content }}</p>
</article>
{% else %}
<p>No posts yet.</p>
{% endfor %}
{% endblock %}""",

    "post.html": """{% extends "base.html" %}
{% block title %}{{ post.title }}{% endblock %}
{% block body %}
<article><h2>{{ post.title }}</h2><p>{{ post.content }}</p></article>
<p><a href="{{ url_for('index') }}">Back to all posts</a></p>
{% endblock %}""",

    "new_post.html": """{% extends "base.html" %}
{% block title %}New post{% endblock %}
{% block body %}
<form method="post">
  <p><input name="title" placeholder="Title" required></p>
  <p><textarea name="content" rows="8" placeholder="Content" required></textarea></p>
  <p><button type="submit">Publish</button></p>
</form>
{% endblock %}""",
}


def write_templates():
    """Put the templates where Jinja will look for them."""
    os.makedirs("templates", exist_ok=True)
    for name, body in TEMPLATES.items():
        with open(os.path.join("templates", name), "w",
                  encoding="utf-8") as handle:
            handle.write(body)


def smoke_test():
    """Exercise every GET route once, without starting a server.

    `app.test_client()` dispatches a real request through the real application
    object -- no socket, no port, no waiting. A web project that cannot be
    driven this way cannot be tested either.

    It returns the number of routes that did **not** answer 2xx, and the
    caller turns that into an exit code. The earlier version printed the
    status and exited 0 regardless, so this file reported success while every
    content route returned 500.
    """
    print("smoke test: dispatching one request per route\n")
    broken = 0
    with app.test_client() as client:
        rules = sorted(app.url_map.iter_rules(), key=lambda rule: str(rule))
        checked = 0
        for rule in rules:
            if "GET" not in rule.methods or rule.arguments:
                continue
            response = client.get(str(rule))
            body = " ".join(response.get_data(as_text=True).split())[:60]
            if response.status_code >= 400:
                broken += 1
            print(f"  GET {str(rule):26} {response.status_code}  {body}")
            checked += 1
    print(f"\n{checked} route(s) answered, {broken} failing. "
          f"Pass --serve to start the real server instead.")
    return broken


if __name__ == "__main__":
    # Templates first: they are what the routes render, and rendering them
    # before they exist is what made every content route 500.
    write_templates()
    # Serving is opt-in, because a run that never returns cannot be tested or
    # captured. With no arguments the file answers every route once and exits.
    if "--serve" in sys.argv:
        app.run(debug=True)
    else:
        raise SystemExit(1 if smoke_test() else 0)
