import json
import sqlite3
import shutil
import tempfile
from datetime import datetime, timedelta


def check_schema(history_path):
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        copied_history_path = shutil.copy2(history_path, tmpfile.name)

        try:
            connection = sqlite3.connect(
                f"file:{copied_history_path}?mode=ro&immutable=1", uri=True
            )
            cursor = connection.cursor()

            # Query to get the schema of the urls table
            cursor.execute("PRAGMA table_info(urls);")
            schema = cursor.fetchall()

            for column in schema:
                print(column)

        finally:
            cursor.close()
            connection.close()


def fetch_history_from_db(history_path, limit=10, offset=0):
    """Fetch history from the provided database path."""
    history_data = []

    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        copied_history_path = shutil.copy2(history_path, tmpfile.name)

        try:
            connection = sqlite3.connect(
                f"file:{copied_history_path}?mode=ro&immutable=1", uri=True
            )
            cursor = connection.cursor()

            # Updated query to remove favicon and fetch duration if available
            query = f"""
            SELECT urls.url, urls.title, urls.visit_count, urls.typed_count, visits.visit_time 
            FROM urls
            JOIN visits ON urls.id = visits.url 
            ORDER BY visits.visit_time DESC
            LIMIT {limit} OFFSET {offset};
            """
            cursor.execute(query)
            results = cursor.fetchall()

            for url, title, visit_count, typed_count, visit_time in results:
                readable_time = datetime(1601, 1, 1) + timedelta(microseconds=visit_time)
                history_data.append({
                    "url": url,
                    "title": title if title else '',
                    "datetime": readable_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "visit_count": visit_count,
                    "typed_count": typed_count
                })

        finally:
            cursor.close()
            connection.close()

    return history_data


def paginate_history(history_path, offset=0, limit=10):
    """Paginate through the browser history and return as JSON."""
    all_history = []  # Store all history entries for JSON response

    if history_path:
        history = fetch_history_from_db(history_path, limit, offset)
    else:
        print("Unsupported browser")
        return json.dumps({"error": f"Unsupported browser or hist_path: {history_path}"})

    if history:
        print(f"\nShowing {len(history)} results from offset {offset}:\n")
        for entry in history:
            data = {'DateTime': entry['datetime'],
                    'URL': entry['url'],
                    'Title': entry['title'],
                    'Visit Count': entry['visit_count'],
                    'Typed Count': entry.get('typed_count', 0)}
            all_history.append(data)

    # Return all history entries as a JSON string
    return json.dumps(all_history, indent=4)


if __name__ == "__main__":
    # b = get_default_browser(os.getlogin())
    # print(b)
    data = paginate_history('chrome', offset=0, limit=2)
    print(data)

"""
    Visit Count: The number of times the URL was visited.
    Last Visit Date: The timestamp of the last visit (already included).
    Favicon URL: The URL of the website's favicon (if available).
    Typed Count: The number of times the URL was typed directly into the address bar (in Firefox).
    Duration: The duration of the visit (how long the site was visited, if available).
"""
# default_browser = get_default_browser()
# if default_browser:
#     print(f"Detected default browser: {default_browser}")
#     paginate_history(default_browser)
# else:
#     print("Please specify your browser manually (chrome/firefox/edge).")
#     browser = input("Enter your browser: ").strip().lower()
#     paginate_history(browser)
