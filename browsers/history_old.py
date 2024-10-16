import json
import sqlite3
import os
import platform
import shutil
import tempfile
from datetime import datetime, timedelta
import subprocess
from typing import Optional
import ctypes


def get_user_sid(username: str) -> Optional[str]:
    """Retrieve the SID for a given username and convert it to a string."""
    try:
        # Set up buffers
        sid = ctypes.create_string_buffer(256)
        sid_size = ctypes.c_ulong(len(sid))
        domain = ctypes.create_string_buffer(256)
        domain_size = ctypes.c_ulong(len(domain))
        sid_name_use = ctypes.c_ulong()

        # LookupAccountName retrieves the SID for the given username
        result = ctypes.windll.advapi32.LookupAccountNameA(
            None, username.encode('utf-8'), sid, ctypes.byref(sid_size),
            domain, ctypes.byref(domain_size), ctypes.byref(sid_name_use))

        if result == 0:
            raise ctypes.WinError()

        # Convert SID to a string
        string_sid = ctypes.c_void_p()
        if ctypes.windll.advapi32.ConvertSidToStringSidA(sid, ctypes.byref(string_sid)) == 0:
            raise ctypes.WinError()

        sid_str = ctypes.string_at(string_sid).decode('utf-8')
        ctypes.windll.kernel32.LocalFree(string_sid)  # Free memory allocated by ConvertSidToStringSidA

        return sid_str
    except Exception as e:
        print(f"Failed to get SID for {username}: {e}")
        return None


def get_default_browser(username):
    """Detect the default web browser on the user's system."""
    if platform.system() == "Windows":
        try:
            import winreg
            # Get the SID of the user
            user_sid = get_user_sid(username)
            print(user_sid)
            if not user_sid:
                print(f"Could not retrieve SID for user: {username}")
                return None

            # Access the registry key for the specific user based on their SID
            reg_path = f'{user_sid}\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice'
            with winreg.OpenKey(winreg.HKEY_USERS, reg_path) as key:
                browser = winreg.QueryValueEx(key, 'ProgId')[0]
                print(browser)
                if 'Chrome' in browser:
                    return 'chrome'
                elif 'Firefox' in browser:
                    return 'firefox'
                elif 'Edge' in browser:
                    return 'edge'
                elif '360SecBHTM' in browser:
                    return '360SecureBrowser'
        except Exception:
            print("Could not determine the default browser. Please specify manually.")
            return None

    elif platform.system() == "Linux":
        try:
            output = subprocess.check_output(['xdg-settings', 'get', 'default-web-browser']).decode().strip()
            if 'firefox' in output:
                return 'firefox'
            elif 'chrome' in output or 'chromium' in output:
                return 'chrome'
        except Exception:
            print("Could not determine the default browser. Please specify manually.")
            return None

    elif platform.system() == "Darwin":  # macOS
        try:
            output = subprocess.check_output(['open', '-a', 'Safari', '--args', '--new', 'http://www.google.com'],
                                             stderr=subprocess.STDOUT)
            return 'safari'  # You can add logic for Safari if needed
        except Exception:
            print("Could not determine the default browser. Please specify manually.")
            return None

    return None


def fetch_chrome_history(limit=10, offset=0):
    """Fetch Chrome history."""
    # history_path = os.path.expanduser('~/AppData/Local/Google/Chrome/User Data/Default/History')
    history_path = r"C:\Users\hp\AppData\Local\Google\Chrome\User Data\Default\History"

    if not os.path.exists(history_path):
        print(f"Chrome history file not found at {history_path}")
        return []

    return fetch_history_from_db(history_path, limit, offset)


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


def fetch_360SB_history(limit=10, offset=0):
    history_path = os.path.expanduser('~/AppData/Local/360SecureBrowser/Chrome/User Data/Default/History')

    if not os.path.exists(history_path):
        print(f"Edge history file not found at {history_path}")
        return []

    return fetch_history_from_db(history_path, limit, offset)


def fetch_edge_history(limit=10, offset=0):
    """Fetch Edge history."""
    history_path = os.path.expanduser('~/AppData/Local/Microsoft/Edge/User Data/Default/History')

    if not os.path.exists(history_path):
        print(f"Edge history file not found at {history_path}")
        return []

    # Call this function with the path to your Edge history database
    # check_schema(history_path)

    return fetch_history_from_db(history_path, limit, offset)


def fetch_firefox_history(limit=10, offset=0):
    """Fetch Firefox history."""
    profile_path = None
    for folder in os.listdir(os.path.expanduser('~/.mozilla/firefox')):
        if folder.endswith('.default-release'):
            profile_path = os.path.join(os.path.expanduser('~/.mozilla/firefox'), folder, 'places.sqlite')
            break

    if profile_path is None or not os.path.exists(profile_path):
        print(f"Firefox history file not found at {profile_path}")
        return []

    return fetch_firefox_history_from_db(profile_path, limit, offset)


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


def fetch_firefox_history_from_db(history_path, limit=10, offset=0):
    """Fetch Firefox history from the provided database path."""
    history_data = []

    connection = sqlite3.connect(history_path)
    cursor = connection.cursor()

    # Updated query to fetch the duration if available
    query = f"""
    SELECT url, title, last_visit_date, visit_count 
    FROM moz_places 
    ORDER BY last_visit_date DESC
    LIMIT {limit} OFFSET {offset};
    """
    cursor.execute(query)
    results = cursor.fetchall()

    for url, title, last_visit_date, visit_count in results:
        readable_time = datetime(1970, 1, 1) + timedelta(microseconds=last_visit_date)
        history_data.append({
            "url": url,
            "title": title if title else '',
            "datetime": readable_time.strftime('%Y-%m-%d %H:%M:%S'),
            "visit_count": visit_count,
        })

    cursor.close()
    connection.close()

    return history_data


def write_history_to_file(history_data, filename="browser_history.txt"):
    """Write history to a specified file."""
    with open(filename, "a", encoding="utf-8") as file:
        for entry in history_data:
            file.write(
                f"DateTime: {entry['datetime']}, URL: {entry['url']}, Title: {entry['title']}, Visit Count: {entry.get('visit_count', 0)}, Typed Count: {entry.get('typed_count', 0)}\n")


def paginate_history(browser, user, brows_path, offset=0, limit=10):
    """Paginate through the browser history and return as JSON."""
    all_history = []  # Store all history entries for JSON response

    if browser == 'chrome':
        history = fetch_chrome_history(limit=limit, offset=offset)
    elif browser == 'edge':
        history = fetch_edge_history(limit=limit, offset=offset)
    elif browser == '360SecureBrowser':
        history = fetch_360SB_history(limit=limit, offset=offset)
    elif browser == 'firefox':
        history = fetch_firefox_history(limit=limit, offset=offset)
    else:
        print("Unsupported browser")
        return json.dumps({"error": "Unsupported browser"})

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

    # Example usage:
    # result = paginate_history('chrome')
    # print(result)  # This will print the JSON formatted history data.


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
