# from typing import List
# import platform
# import os
#
#
# def get_installed_browsers(user) -> List[str]:
#     """Detect installed browsers on a Windows or Linux system."""
#     browsers = []
#
#     if platform.system() == "Windows":
#         import winreg
#         # Check for Chrome
#         chrome_paths = [
#             os.path.expanduser(f'C:\\Users\\{user}\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'),
#             os.path.expanduser(f'C:\\Users\\{user}\\AppData\\Local\\Chromium\\Application\\chrome.exe')
#         ]
#         if any(os.path.exists(path) for path in chrome_paths):
#             browsers.append('chrome')
#
#         # Check for Firefox
#         firefox_paths = [
#             os.path.expanduser(f'C:\\Users\\{user}\\AppData\\Local\\Mozilla Firefox\\firefox.exe'),
#             os.path.expanduser(f'C:\\Users\\{user}\\AppData\\Local\\Mozilla\\Firefox\\firefox.exe')
#         ]
#         if any(os.path.exists(path) for path in firefox_paths):
#             browsers.append('firefox')
#
#         # Check for Microsoft Edge
#         edge_path = os.path.expanduser(f'C:\\Users\\{user}\\AppData\\Local\\Microsoft\\Edge\\Application\\msedge.exe')
#         if os.path.exists(edge_path):
#             browsers.append('edge')
#
#         # Check for Opera
#         opera_paths = [
#             os.path.expanduser(f'C:\\Users\\{user}\\AppData\\Local\\Programs\\Opera\\launcher.exe'),
#             os.path.expanduser(f'C:\\Users\\{user}\\AppData\\Local\\Programs\\Opera GX\\launcher.exe')
#         ]
#         if any(os.path.exists(path) for path in opera_paths):
#             browsers.append('opera')
#
#         # Check for 360 Secure Browser
#         secure_browser_paths = [
#             os.path.expanduser(f'C:\\Users\\{user}\\AppData\\Local\\360Chrome\\Chrome\\Application\\360chrome.exe'),
#             os.path.expanduser(f'C:\\Users\\{user}\\AppData\\Local\\360Browser\\Browser\\Application\\360chrome.exe'),
#             os.path.expanduser(
#                 f'C:\\Users\\{user}\\AppData\\Local\\360SecureBrowser\\Chrome\\Application\\360SecureBrowser.exe')
#         ]
#         if any(os.path.exists(path) for path in secure_browser_paths):
#             browsers.append('360SecureBrowser')
#
#     elif platform.system() == "Linux":
#         # Define typical paths for browser executables on Linux
#         linux_browser_commands = {
#             "Chrome": "google-chrome",
#             "Chromium": "chromium-browser",
#             "Firefox": "firefox",
#             "Opera": "opera",
#             "Brave": "brave-browser",
#             "Vivaldi": "vivaldi"
#         }
#
#         for browser_name, command in linux_browser_commands.items():
#             if os.system(f"command -v {command} > /dev/null 2>&1") == 0:
#                 browsers.append(browser_name)
#
#     # Return a unique list of browser names
#     return list(set(browsers))
#
#
# print(get_installed_browsers("hp"))
import os
import winreg as reg


def get_installed_browsers_with_paths():
    browsers = {}
    try:
        # Open the registry key for installed browsers (machine-wide installations)
        key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Clients\StartMenuInternet")
        for i in range(0, reg.QueryInfoKey(key)[0]):
            try:
                # Get the browser name
                browser = reg.EnumKey(key, i)
                install_path = get_browser_install_path(browser)
                browsers[browser] = install_path
            except OSError:
                break
        reg.CloseKey(key)
    except FileNotFoundError:
        pass

    try:
        # Check also in HKEY_CURRENT_USER in case of user-specific installations
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"SOFTWARE\Clients\StartMenuInternet")
        for i in range(0, reg.QueryInfoKey(key)[0]):
            try:
                browser = reg.EnumKey(key, i)
                install_path = get_browser_install_path(browser)
                if browser not in browsers:
                    browsers[browser] = install_path
            except OSError:
                break
        reg.CloseKey(key)
    except FileNotFoundError:
        pass

    return browsers


def get_browser_install_path(browser_name):
    try:
        # Try to open the Uninstall key for the specific browser
        key_path = fr"SOFTWARE\Clients\StartMenuInternet\{browser_name}\shell\open\command"
        try:
            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, key_path)
        except FileNotFoundError:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path)

        # Get the path to the executable (usually the first value)
        install_path = reg.QueryValue(key, None)
        reg.CloseKey(key)

        # Clean up the path (remove surrounding quotes)
        return install_path.strip('"')
    except FileNotFoundError:
        return "Installation path not found."


if __name__ == "__main__":
    browsers = get_installed_browsers_with_paths()
    if browsers:
        print("Installed browsers and their installation paths:")
        for browser, path in browsers.items():
            print(f"- {browser}: {path}")
    else:
        print("No browsers detected.")
    input("try: ")

