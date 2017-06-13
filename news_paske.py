#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import re
import urllib
from bs4 import BeautifulSoup
import sys
import argparse
reload(sys)
sys.setdefaultencoding('utf-8')

def get_page_contents(url):
  # Get page contents using curl.
  proc = subprocess.Popen(["curl", "-s", str(url).rstrip()], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  page = out.encode('utf8')
  if len(page) > 0:
    return page
  else:
    urlerrors[url] = "No content received"
    return False

def strip_html_tags(data):
  # Clear HTML tags
  out = re.compile(r'<.*?>')
  out = out.sub('', data)
  out = out.replace('&amp;' , '&')
  return out

try:
  seen_urls = open(".seen_urls", "r")
  seen_urls = seen_urls.readlines()
except IOError:
  seen_urls = []

parser = argparse.ArgumentParser(description='Parse a list of URLs from stdin to a muppet-friendly format.')
parser.add_argument("-s",
                    "--start",
                    metavar='[A-Z]',
                    type=str,
                    help="Define which letter to use as the first one instead of A.")

parser.add_argument("-p",
                    "--paragraph",
                    metavar='length',
                    type=int,
                    help="Define minimum length for opening paragraph. Default 100 characters.")

arg = parser.parse_args()

urlerrors = {}

# Start from a different letter if appending to an existing list of news
if arg.start:
  charcode = int(ord(arg.start[0])) - 1
else:
  charcode = 64

# Set the minimum length for an acceptable first paragraph
if arg.paragraph:
  blurb_min_length = arg.paragraph
else:
  blurb_min_length = 100

# Process standard input for a list of urls.

seen_out = open(".seen_urls", "a")
for url in sys.stdin:
  # Clean URL trackers
  if "utm_source" in url:
    url = url.split("?")
    url = url[0] + "\r\n"
  if url in seen_urls:
    urlerrors[url] = "Already seen"
    continue
  seen_out.write(url)
  if str(url)[0:4].lower() != "http":
    continue
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
  while len(blurb) < blurb_min_length or 'cookies' in blurb:
    opening_paragraph += 1
    blurb = strip_html_tags(str(paragraphs[opening_paragraph]))
  print( '\033[92m' + url).strip()
  print( '\033[93m' + chr(charcode) + ':|' + '\033[0m' + title.strip()).replace('\n', '').replace('\r', '')
  print( '\033[93m' + chr(charcode) + ':' + '\033[0m' + blurb.strip()).replace('\n', '').replace('\r', '')
  print("  ")
for url, error in urlerrors.iteritems():
  print('\033[91m%s:\033[0m %s' % (error, url.strip()))

