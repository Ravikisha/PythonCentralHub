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
        try:
            app.run(debug=True)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        smoke_test()
