import asyncio
import ctypes
import os
import sys

# Assuming 'client.py' contains the start() function
from parent import start_client


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def run_as_admin():
    if is_admin():
        print("Running with admin rights.")
        asyncio.get_event_loop().run_until_complete(start_client())  # Call your function that requires admin rights
    else:
        print("Relaunching with admin rights...")

        # Get the script filename and arguments
        script = sys.argv[0]
        params = " ".join(sys.argv[1:])

        try:
            # Attempt to relaunch the script with admin rights
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, params, 1)
        except Exception as e:
            print(f"Failed to relaunch as admin: {e}")
            sys.exit(1)

        sys.exit(0)


if __name__ == "__main__":
    run_as_admin()