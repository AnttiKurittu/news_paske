#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import re
import os
from bs4 import BeautifulSoup
import sys
import argparse
import urlparse
import json
import urllib
import urllib2
import requests
reload(sys)
sys.setdefaultencoding('utf-8')

gapi_key = ''

def get_page_contents(url):
  # Get page contents using curl.
  if url[-5:].strip() == ".pdf":
    urlerrors[url] = "Can't parse PDF, handle this manually"
    return False
  proc = subprocess.Popen(["curl", "-s", str(url).rstrip()], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  try:
    page = out.encode('UTF-8')
  except:
    out = out.decode('latin-1')
    page = out.encode('UTF-8')

  if len(page) > 0:
    return page
  else:
    urlerrors[url] = "No content received"
    return False

def shorten_url(url):
    if gapi_key == '':
      return "Unable to shorten URL, no API key present."
    requests.packages.urllib3.disable_warnings()
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=' + gapi_key
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    payload = json.dumps(payload)
    r = requests.post(post_url, data=payload, headers=headers)
    out = json.loads(r.text)
    return out['id']

def strip_html_tags(data):
  # Clear HTML tags
  out = re.compile(r'<.*?>')
  out = out.sub('', data)
  out = out.replace('&amp;' , '&')
  return out

#seen_urls_path = os.path.expanduser("~/.seen_urls")
seen_urls_path = ("/ncsc-fi/cases/news_paske_seen/.seen_urls")

try:
  seen_urls = open(seen_urls_path, "r+")
  seen_urls = seen_urls.readlines()
except IOError:
  seen_urls = open(seen_urls_path, "w+")
  seen_urls.write("Seen URLs stored by news_paske.py" + "\r\n")
  seen_urls.close()
  seen_urls = []

news_paske_descr = 'News_paske.py will parse a list of URLs from stdin to a Chump IRCbot-friendly format. Add URLs to a file, then pipe it to the script using stdin. Use one line per source url. News_paske will ignore lines not starting with \"http\". To add a comment to the previous URL in the list, start the line with the \"+\" symbol. News_paske.py will collect seen URLs to \033[1m%s\033[0m. To prevent checking and collection of URLs, run the script with the -d option. The script will make a guess on which paragraph is the opening quote, but will sometimes miss. Review the output manually before using it!' % seen_urls_path


parser = argparse.ArgumentParser(description=news_paske_descr)
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

parser.add_argument("-o",
                    "--outfile",
                    metavar='filename',
                    type=str,
                    help="Output to file instead of stdout")

parser.add_argument("-i",
                    "--increment",
                    help="Increment story index letter for already seen urls - useful if adding to a list that already has added URLs.",
                    action="store_true")

parser.add_argument("-m",
                    "--minify",
                    help="Shorten URLs using the Google URL shortener service.",
                    action="store_true")

parser.add_argument("-q",
                    "--quiet",
                    help="Suppress error messages",
                    action="store_true")

parser.add_argument("-d",
                    "--debug",
                    help="Debug mode - do not store or check seen URLs",
                    action="store_true")

arg = parser.parse_args()

if arg.outfile:
    class c:

        D = HDR = B = G = Y = R = END = BOLD = UL = ''
else:
    class c:
        HDR = '\033[96m'
        B = '\033[94m'
        Y = '\033[93m'
        G = '\033[92m'
        R = '\033[91m'
        D = '\033[90m'
        END = '\033[0m'
        BOLD = '\033[1m'
        UL = '\033[4m'

urlerrors = {}

if arg.outfile:
  print "Saving to file %s, please wait..." % arg.outfile,
  sys.stdout.flush()
  sys.stdout = open(arg.outfile, 'w')

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

seen_out = open(seen_urls_path, "a")

for url in sys.stdin:
  # Clean URL trackers
  add_as_comment = False
  if "utm_source" in url:
    url = url.split("?")
    url = url[0] + "\r\n"
  if url in seen_urls and arg.debug != True:
    urlerrors[url] = "Already seen"
    if arg.increment:
      charcode += 1
    continue
  if str(url)[0:1] == "+":
    add_as_comment = True
  if str(url)[0:4].lower() != "http" and add_as_comment == False:
    continue
  if arg.debug != True:
    seen_out.write(url)
  if add_as_comment == True:
    print( '\033[93m' + chr(charcode) + ':\033[0m' + url[1:].strip() + '')
  else:
    page = get_page_contents(url)
    if page == False:
      continue
    soup = BeautifulSoup(page)
    try:
      title = soup.title.string
    except AttributeError:
      urlerrors[url] = "No page title found"
      continue
    paragraphs = soup.findAll('p')
    opening_paragraph = 0
    blurb = strip_html_tags(str(paragraphs[0]))
    blurb = blurb.strip()
    while len("".join(blurb.split())) < blurb_min_length or 'cookies' and 'accept' in blurb:
      opening_paragraph += 1
      try:
        blurb = strip_html_tags(str(paragraphs[opening_paragraph]))
        blurb = blurb.strip()
      except IndexError:
        blurb = False
        urlerrors[url] = "No quotable paragraphs found (min %s chars)" % blurb_min_length
        break
    charcode += 1
    if arg.minify:
      short_url = " (" + shorten_url(url.strip()) + ")"
    else:
      short_url = ""
    print( '\r\n' + c.UL + c.G + url.strip() + c.END)
    print( c.Y + chr(charcode) + ':|' + c.END + c.BOLD + title.strip() + c.END).replace('\n', '').replace('\r', '')
    if blurb != False:
      print( c.Y + chr(charcode) + ':' + c.END + blurb.strip().replace('\n', '').replace('\r', '') + short_url)

print("")
if urlerrors and arg.quiet != True:
  print c.R + "Encountered %s error(s) while processing:" % len(urlerrors)
  for url, error in urlerrors.iteritems():
    print(c.END + ' * %s: %s' % (error, url.strip()))

if arg.outfile:
  sys.stdout = sys.__stdout__
  print "Done."
