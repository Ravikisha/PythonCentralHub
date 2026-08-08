"""
AI-based News Summarizer

Features:
- News summarization using NLP
- Keyword extraction
- Web interface (Flask)
- Modular design
- Error handling
"""
from flask import Flask, request, render_template_string
import sys
import re
from collections import Counter
try:
    from gensim.summarization import summarize
except ImportError:
    summarize = None

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = ''
    keywords = []
    if request.method == 'POST':
        text = request.form['text']
        if summarize:
            summary = summarize(text)
        else:
            summary = '\n'.join(text.split('.')[:3])
        words = re.findall(r'\w+', text.lower())
        freq = Counter(words)
        keywords = [w for w, c in freq.most_common(10)]
    return render_template_string('''<form method="post"><textarea name="text" rows="10" cols="80"></textarea><br><input type="submit" value="Summarize"></form><h2>Summary</h2><pre>{{summary}}</pre><h2>Keywords</h2><pre>{{keywords}}</pre>''', summary=summary, keywords=', '.join(keywords))

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
