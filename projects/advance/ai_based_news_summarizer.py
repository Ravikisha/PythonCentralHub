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

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
