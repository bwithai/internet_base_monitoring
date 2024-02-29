import pprint
from browser_history.utils import default_browser

BrowserClass = default_browser()

if BrowserClass is None:
    # default browser could not be identified
    print("could not get default browser!")
else:
    b = BrowserClass()
    # his is a list of (datetime.datetime, url, title) tuples
    his = b.fetch_history().histories

    pprint.pprint(his[-10:-1])
