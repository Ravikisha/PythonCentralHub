# Web Page Content Downloader

import urllib.request, urllib.error, urllib.parse


def ask(prompt="", default=""):
    """Read a line, or fall back to `default` when nobody is there to type.

    Without this the script raises EOFError the moment it runs unattended — in
    a test, a scheduled job, or the build that captures this output for the
    docs. The fallback is printed rather than silent, so a reader can always
    tell which answers were typed and which were assumed.
    """
    try:
        return input(prompt).strip() or default
    except EOFError:
        print(f"{default}   (no input available, using the default)")
        return default

url = ask('Enter the URL: ', 'https://example.com')
fileName = ask('Enter the file name: ', 'demo.txt')

response = urllib.request.urlopen(url)
webContent = response.read().decode('utf-8')


f = open(fileName, 'w')
f.write(webContent)
f.close()