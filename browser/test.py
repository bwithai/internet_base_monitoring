from browser_history.browsers import Chrome, Firefox

# Create an instance of the Chrome class
chrome_instance = Chrome()

# Fetch the browser history
outputs = chrome_instance.fetch_history()

# Extract the list of (datetime.datetime, url) tuples
history_entries = outputs.histories

# Print the last 10 entries
latest_then = history_entries[-10:-1]

for i in latest_then:
    print(i)
