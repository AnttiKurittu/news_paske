usage: news_paske.py [-h] [-s [A-Z]] [-p length] [-o filename] [-i] [-m] [-q]
                     [-w] [-d]

News_paske.py will parse a list of URLs from stdin to a Chump IRCbot-friendly
format. Add URLs to a file, then pipe it to the script using stdin. Use one
line per source url. News_paske will ignore lines not starting with "http". To
add a comment to the previous URL in the list, start the line with the "+"
symbol. News_paske.py will collect seen URLs to /ncsc-
fi/cases/news_paske_seen/.seen_urls. To prevent checking and collection of
URLs, run the script with the -d option. The script will make a guess on which
paragraph is the opening quote, but will sometimes miss. Review the output
manually before using it!

optional arguments:
  -h, --help            show this help message and exit
  -s [A-Z], --start [A-Z]
                        Define which letter to use as the first one instead of
                        A.
  -p length, --paragraph length
                        Define minimum length for opening paragraph. Default
                        100 characters.
  -o filename, --outfile filename
                        Output to file instead of stdout
  -i, --increment       Increment story index letter for already seen urls -
                        useful if adding to a list that already has added
                        URLs.
  -m, --minify          Shorten URLs using the Google URL shortener service.
  -q, --quiet           Suppress error messages
  -w, --wiki            Use MoinMoin Wiki output format and print the
                        headlines in a bullet-point list with 'links.
  -d, --debug           Debug mode - do not store or check seen URLs

