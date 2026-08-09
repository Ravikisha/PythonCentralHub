"""RSS feed reader -- fetch a feed, clean the summaries, print the headlines.

The original version had two problems worth naming:

* It called `webbrowser.open(...)` at import time, so merely running the
  script opened a browser window at whatever link happened to be last. A
  reader who ran it to see some headlines got a tab instead.
* It used `entry` after the loop had finished, which is the *last* entry
  rather than any chosen one. That works, silently, and means something
  different from what it looks like.

Both are fixed here. Opening a link is now an explicit choice, and every
entry is addressed by index.

    python rssfeedreader.py                  # fetch and print
    python rssfeedreader.py --open 3         # also open entry 3 in a browser
    python rssfeedreader.py --test           # HTML stripping, no network
"""

import html
import re
import sys

FEED_URL = "https://www.reddit.com/r/Python/.rss"

TAG = re.compile(r"<[^>]+>")
WHITESPACE = re.compile(r"\s+")


def strip_html(text: str) -> str:
    """Turn a feed summary into plain text.

    Feed summaries are HTML fragments, so printing them raw gives a wall of
    `<div class="md">`. This removes the tags, unescapes the entities and
    collapses the whitespace -- in that order, because unescaping first would
    turn `&lt;b&gt;` into a tag that the regex then eats.

    A regex is the wrong tool for parsing HTML in general and the right one
    here: the goal is to *discard* markup, not to understand it, so the
    failure mode is a stray angle bracket rather than a wrong answer.
    """
    without_tags = TAG.sub(" ", text or "")
    unescaped = html.unescape(without_tags)
    return WHITESPACE.sub(" ", unescaped).strip()


def fetch(url: str = FEED_URL):
    """Parse the feed, returning None if it cannot be reached."""
    import feedparser

    feed = feedparser.parse(url)
    if feed.get("bozo") and not feed.get("entries"):
        print(f"could not read the feed: {feed.get('bozo_exception')}")
        return None
    return feed


def show(feed, limit: int = 10) -> None:
    title = feed["feed"].get("title", "(untitled feed)")
    print(f"{title} -- {len(feed['entries'])} entries\n")
    for index, entry in enumerate(feed["entries"][:limit]):
        summary = strip_html(entry.get("summary", ""))
        print(f"{index:>3}. {entry.get('title', '(no title)')}")
        print(f"     {entry.get('published', 'no date')}  "
              f"by {entry.get('author', 'unknown')}")
        if summary:
            print(f"     {summary[:110]}{'...' if len(summary) > 110 else ''}")
        print()


def open_entry(feed, index: int) -> None:
    """Open one entry in a browser -- only when explicitly asked.

    The original did this unconditionally at the end of the script. Opening a
    window is a side effect nobody asked for, and it makes the file unusable
    in anything automated.
    """
    import webbrowser

    entries = feed["entries"]
    if not 0 <= index < len(entries):
        print(f"no entry {index}; the feed has {len(entries)}")
        return
    link = entries[index].get("link")
    print(f"opening entry {index}: {link}")
    webbrowser.open(link)


def main() -> int:
    feed = fetch()
    if feed is None:
        return 1
    show(feed)
    if "--open" in sys.argv:
        position = sys.argv.index("--open") + 1
        index = int(sys.argv[position]) if position < len(sys.argv) else 0
        open_entry(feed, index)
    else:
        print("Pass --open N to open entry N in a browser.")
    return 0


if __name__ == "__main__":
    if "--test" in sys.argv:
        import unittest

        class TestStrip(unittest.TestCase):
            def test_tags_removed(self):
                self.assertEqual(
                    strip_html('<div class="md"><p>Hello</p></div>'), "Hello")

            def test_entities_unescaped(self):
                self.assertEqual(strip_html("a &amp; b"), "a & b")

            def test_escaped_tags_survive_as_text(self):
                # &lt;b&gt; is the *text* "<b>", not markup. Unescaping before
                # stripping would delete it; this order keeps it.
                self.assertEqual(strip_html("&lt;b&gt;"), "<b>")

            def test_whitespace_collapsed(self):
                self.assertEqual(strip_html("a\n\n   b\t c"), "a b c")

            def test_empty_input(self):
                self.assertEqual(strip_html(""), "")
                self.assertEqual(strip_html(None), "")

        unittest.main(argv=sys.argv[:1], exit=False)
    else:
        raise SystemExit(main())
