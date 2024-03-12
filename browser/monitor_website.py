import json
import pprint
from browser_history.utils import default_browser
from datetime import datetime

BrowserClass = default_browser()


def custom_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


def fetch_hist():
    if BrowserClass is None:
        # default browser could not be identified
        return {"message": "could not get default browser!"}
    else:
        b = BrowserClass()
        # his is a list of (datetime.datetime, url, title) tuples
        his = b.fetch_history().histories

        data = his[-10:-1]
        # Convert data to JSON format
        json_data = json.dumps([
            {
                'datetime': dt.isoformat(),
                'url': url,
                'title': title
            }
            for dt, url, title in data
        ])

        return json_data