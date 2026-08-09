"""Download a web page to a file -- the naive way, then the way that works.

The three-line version at the bottom of every tutorial reads the whole
response into memory, decodes it as UTF-8 whatever the server said, and
crashes on any HTTP error. Each of those is fine until it is not:

* a 404 raises `HTTPError`, which is not caught, so the script ends in a
  traceback instead of a message;
* `decode("utf-8")` on a page served as ISO-8859-1 either raises or produces
  mojibake;
* reading a 2 GB file into a string does exactly what it says.

`download` fixes the first two. `download_large` fixes the third by streaming.

    python webpagecontentdownloader.py            # downloads example.com
    python webpagecontentdownloader.py --test     # no network
"""

import os
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "Mozilla/5.0 (compatible; python-central-hub-demo/1.0)"


def ask(prompt="", default=""):
    """Read a line, or fall back to `default` when nobody is there to type."""
    try:
        return input(prompt).strip() or default
    except EOFError:
        print(f"{default}   (no input available, using the default)")
        return default


def guess_encoding(response, fallback="utf-8") -> str:
    """Take the encoding from the response, not from hope.

    `Content-Type: text/html; charset=iso-8859-1` is the server telling you
    exactly how to decode the bytes. Ignoring it and assuming UTF-8 is the
    single most common cause of a page full of question marks.
    """
    charset = response.headers.get_content_charset()
    return charset or fallback


def download(url: str, filename: str, timeout: int = 20) -> int | None:
    """Fetch `url` into `filename`. Returns bytes written, or None on failure.

    Everything the naive version leaves out is here: a User-Agent (many sites
    reject the default `Python-urllib`), a timeout (without one the script can
    hang indefinitely), the server's own encoding, and an error path that
    reports rather than raises.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            encoding = guess_encoding(response)
            text = response.read().decode(encoding, errors="replace")
    except urllib.error.HTTPError as exc:
        print(f"{url} returned HTTP {exc.code} ({exc.reason})")
        return None
    except urllib.error.URLError as exc:
        print(f"could not reach {url}: {exc.reason}")
        return None

    with open(filename, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    print(f"{url} -> {filename}  ({len(text):,} characters, "
          f"decoded as {encoding})")
    return len(text)


def download_large(url: str, filename: str, chunk_size: int = 64 * 1024,
                   timeout: int = 20) -> int | None:
    """Stream to disk instead of reading the whole body into memory.

    `shutil.copyfileobj` moves the response to the file `chunk_size` bytes at
    a time, so peak memory is the chunk, not the file. For a page this is
    pointless; for the 700 MB ISO someone eventually points this at, it is the
    difference between working and not.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response, \
                open(filename, "wb") as handle:
            shutil.copyfileobj(response, handle, chunk_size)
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        print(f"could not download {url}: {exc}")
        return None
    size = os.path.getsize(filename)
    print(f"{url} -> {filename}  ({size:,} bytes, streamed in "
          f"{chunk_size // 1024} KB chunks)")
    return size


def safe_name(url: str, default: str = "page.html") -> str:
    """A filename derived from the URL, without the path traversal.

    `os.path.basename` on an attacker-supplied URL is what stops
    `../../etc/passwd` from being a valid destination.
    """
    path = urllib.parse.urlparse(url).path
    name = os.path.basename(path.rstrip("/"))
    return name or default


def main():
    url = ask("Enter the URL: ", "https://example.com")
    filename = ask("Enter the file name: ", safe_name(url, "example.html"))
    if download(url, filename) is None:
        return 1
    download_large(url, "streamed-" + filename)

    # What the error path looks like when the page is not there.
    download("https://example.com/definitely-not-a-real-page", "missing.html")
    return 0


if __name__ == "__main__":
    if "--test" in sys.argv:
        import unittest

        class TestNaming(unittest.TestCase):
            def test_basename_from_url(self):
                self.assertEqual(
                    safe_name("https://example.com/a/b/page.html"),
                    "page.html")

            def test_empty_path_uses_default(self):
                self.assertEqual(safe_name("https://example.com"),
                                 "page.html")

            def test_traversal_stripped(self):
                self.assertEqual(
                    safe_name("https://example.com/../../etc/passwd"),
                    "passwd")

            def test_trailing_slash(self):
                self.assertEqual(safe_name("https://example.com/docs/"),
                                 "docs")

        unittest.main(argv=sys.argv[:1], exit=False)
    else:
        raise SystemExit(main())
