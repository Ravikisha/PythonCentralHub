"""
E-commerce Website (Basic)

A Python application that simulates a basic e-commerce website.
Features include:
- Displaying a list of products.
- Adding products to a shopping cart.
- Calculating the total price.
"""

import os
import sys
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Sample product data
products = [
    {"id": 1, "name": "Laptop", "price": 800},
    {"id": 2, "name": "Smartphone", "price": 500},
    {"id": 3, "name": "Headphones", "price": 100},
    {"id": 4, "name": "Keyboard", "price": 50},
]

# Shopping cart
cart = []

@app.route('/')
def index():
    """Display the list of products."""
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    """Add a product to the shopping cart."""
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        cart.append(product)
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    """Display the shopping cart and total price."""
    total_price = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total_price=total_price)


# Flask looks for templates on disk, so a self-contained single-file project
# has to put them there before the first request. Keeping them as strings
# means the project stays one file; writing them at startup means Jinja can
# actually find them.
TEMPLATES = {
    "base.html": """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>{% block title %}Shop{% endblock %}</title>
<style>
 body { font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; }
 table { border-collapse: collapse; width: 100%; }
 td, th { text-align: left; padding: 0.4rem 0.6rem; border-bottom: 1px solid #ddd; }
 a { color: #06c; }
</style></head>
<body>
<h1><a href="{{ url_for('index') }}">Shop</a></h1>
{% block body %}{% endblock %}
</body></html>""",

    "index.html": """{% extends "base.html" %}
{% block body %}
<p><a href="{{ url_for('view_cart') }}">View cart</a></p>
<table>
<tr><th>Product</th><th>Price</th><th></th></tr>
{% for product in products %}
<tr>
  <td>{{ product.name }}</td>
  <td>${{ product.price }}</td>
  <td><a href="{{ url_for('add_to_cart', product_id=product.id) }}">Add to cart</a></td>
</tr>
{% endfor %}
</table>
{% endblock %}""",

    "cart.html": """{% extends "base.html" %}
{% block title %}Cart{% endblock %}
{% block body %}
{% if cart %}
<table>
<tr><th>Product</th><th>Price</th></tr>
{% for item in cart %}
<tr><td>{{ item.name }}</td><td>${{ item.price }}</td></tr>
{% endfor %}
<tr><th>Total</th><th>${{ total_price }}</th></tr>
</table>
{% else %}
<p>The cart is empty.</p>
{% endif %}
<p><a href="{{ url_for('index') }}">Keep shopping</a></p>
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
