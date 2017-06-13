
#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import re
import urllib
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def get_page_contents(url):
  proc = subprocess.Popen(["curl", "-s", str(url).rstrip()], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  page = out.encode('utf8')
  if len(page) > 0:
    return page
  else:
    urlerrors[url] = "No content received"
    return False

def strip_html_tags(data):
  out = re.compile(r'<.*?>')
  out = out.sub('', data)
  out = out.replace('&amp;' , '&')
  return out

urlerrors = {}
charcode = 64

for url in sys.stdin:
  page = get_page_contents(url)
  if page == False:
    continue
  charcode += 1
  soup = BeautifulSoup(page)
  title = soup.title.string
  paragraphs = soup.findAll('p')
  opening_paragraph = 0
  blurb = strip_html_tags(str(paragraphs[0]))
  blurb = blurb.strip()
  while len(blurb) < 100 or 'cookies' in blurb:
    opening_paragraph += 1
    blurb = strip_html_tags(str(paragraphs[opening_paragraph]))
  print( '\033[92m' + url).strip()
  print( '\033[93m' + chr(charcode) + ':|' + '\033[0m' + title).strip()
  print( '\033[93m' + chr(charcode) + ':' + '\033[0m' + blurb).strip()
  print("  ")
for url, error in urlerrors.iteritems():
  print("%s: %s" % (error, url))
