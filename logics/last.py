import os

from browsers.history import paginate_history, get_default_browser

b = get_default_browser(os.getlogin())
print(b)
d = paginate_history(b)
print(d)