# Web Page Content Downloader

import urllib.request, urllib.error, urllib.parse

url = input('Enter the URL: ')
fileName = input('Enter the file name: ')

response = urllib.request.urlopen(url)
webContent = response.read().decode('utf-8')


f = open(fileName, 'w')
f.write(webContent)
f.close()