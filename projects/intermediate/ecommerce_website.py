"""
E-commerce Website (Basic)

A Python application that simulates a basic e-commerce website.
Features include:
- Displaying a list of products.
- Adding products to a shopping cart.
- Calculating the total price.
"""

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
