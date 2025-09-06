"""
E-commerce Website (Basic)

A Python application that simulates a basic e-commerce website.
Features include:
- Displaying a list of products.
- Adding products to a shopping cart.
- Calculating the total price.
"""

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

if __name__ == '__main__':
    app.run(debug=True)
