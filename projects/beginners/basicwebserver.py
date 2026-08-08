# Basic Web Server (Flask)

import sys
from flask import Flask # pip install flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, World!"

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