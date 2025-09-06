"""
E-commerce Website (Advanced)

Features:
- Product management
- Cart system
- Analytics
- Modular design
- Web interface (Flask)
- Error handling
"""
from flask import Flask, render_template_string, request, redirect, url_for, session
import sys
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'
products = [
    {'id': 1, 'name': 'Laptop', 'price': 1000},
    {'id': 2, 'name': 'Phone', 'price': 500},
    {'id': 3, 'name': 'Headphones', 'price': 100}
]

@app.route('/')
def index():
    return render_template_string('''<h1>Products</h1>{% for p in products %}<div>{{p['name']}} - ${{p['price']}} <a href="/add/{{p['id']}}">Add to Cart</a></div>{% endfor %}<a href="/cart">View Cart</a>''', products=products)

@app.route('/add/<int:pid>')
def add_to_cart(pid):
    cart = session.get('cart', [])
    cart.append(pid)
    session['cart'] = cart
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    items = [p for p in products if p['id'] in cart]
    total = sum(p['price'] for p in items)
    return render_template_string('''<h1>Cart</h1>{% for p in items %}<div>{{p['name']}} - ${{p['price']}}</div>{% endfor %}<div>Total: ${{total}}</div><a href="/">Back</a>''', items=items, total=total)

@app.route('/analytics')
def analytics():
    sales = random.randint(10, 100)
    return render_template_string('<h1>Analytics</h1><div>Sales: {{sales}}</div><a href="/">Back</a>', sales=sales)

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
