news_paske.py eats a list of URLs from stdin and spits out a Chump-IRCbot friendly list with the title and opening paragraph for easy copy-pasting fun into IRC-based news aggregators. Oh, the wonders of modern technology! news_paske will also keep track of already posted urls so you won't embarass yourself by posting the same news article two times in a row. How wonderful!

Usage: news_paske.py <list_of_urls.txt

optional arguments:

  -s [A-Z], --start [A-Z]
                        Define which letter to use as the first one instead of "A".

  -p length, --paragraph length
                        Define minimum length for opening paragraph. Default 100 characters.

