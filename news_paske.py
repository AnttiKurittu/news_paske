#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess
import re
import os
import urllib
from bs4 import BeautifulSoup
import sys
import argparse
reload(sys)
sys.setdefaultencoding('utf-8')

def get_page_contents(url):
  # Get page contents using curl.
  if url[-5:].strip() == ".pdf":
    urlerrors[url] = "Can't parse PDF, handle this manually"
    return False
  proc = subprocess.Popen(["curl", "-s", str(url).rstrip()], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()

  try:
    page = out.encode('utf8')
  except:
    out = out.decode('latin-1')
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

parser.add_argument("-d",
                    "--debug",
                    help="Debug mode - do not store or check seen URLs",
                    action="store_true")

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

seen_out = open(seen_urls_path, "a")

for url in sys.stdin:
  # Clean URL trackers
  add_as_comment = False
  if "utm_source" in url:
    url = url.split("?")
    url = url[0] + "\r\n"
  if url in seen_urls and arg.debug != True:
    urlerrors[url] = "Already seen"
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
    charcode += 1
    soup = BeautifulSoup(page)
    title = soup.title.string
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
    print( '\r\n\033[4m\033[92m' + url.strip() + '\033[0m')
    print( '\033[93m' + chr(charcode) + ':|' + '\033[0m\033[1m' + title.strip() + '\033[0m').replace('\n', '').replace('\r', '')
    if blurb != False:
      print( '\033[93m' + chr(charcode) + ':' + '\033[0m' + blurb.strip().replace('\n', '').replace('\r', ''))
print("")
if urlerrors:
  print "\033[91mEncountered %s error(s) while processing:" % len(urlerrors)
  for url, error in urlerrors.iteritems():
    print('\033[0m * %s: %s' % (error, url.strip()))

