import json
import os
import win32net
import win32netcon

from browsers.browser import get_browsers

users_info = {}
admin = []
helper_ac = []
user_to_block = []

# Words to filter out from the user lists
words_to_remove = ["The", "command", "completed", "with", "successfully", "Administrator"]


# Listing all users of the Windows system
def list_users():
    try:
        users_info = []
        resume_handle = 0

        while True:
            data, total, resume_handle = win32net.NetUserEnum(
                None, 0, win32netcon.FILTER_NORMAL_ACCOUNT, resume_handle
            )
            users_info.extend([user['name'] for user in data])

            if not resume_handle:
                break

        return users_info

    except Exception as e:
        print(f"Error listing users: {e}")
        return None


def is_helper_account(username):
    # Conditions to identify helper accounts
    helper_account_keywords = ['Administrator', 'DefaultAccount', 'WDAGUtilityAccount']
    return any(keyword.lower() in username.lower() for keyword in helper_account_keywords)


def is_user_admin(username):
    try:
        output = os.popen('net localgroup administrators').read()
        return username.lower() in output.lower()
    except Exception as e:
        print(f"Error checking admin membership for {username}: {e}")
        return False


def kill_all_open_processes(username):
    try:
        # Log off the user
        os.system(f"taskkill /F /FI \"USERNAME eq {username}\"")
        print(f"The user {username} has been logged out.")
    except Exception as e:
        print(f"An error occurred while logging out {username}: {e}")


def restart_sys_immediately():
    os.system("shutdown /r /t 0")


def disable_and_logout_user_account(username):
    try:
        # Disable the user account
        os.system(f"net user {username} /active:no")
        print(f"The account {username} has been successfully disabled.")

        # Log off the specific user
        os.system(f"taskkill /F /FI \"USERNAME eq {username}\"")
        print(f"The user {username} has been logged out.")
    except Exception as e:
        print(f"An error occurred while disabling {username}: {e}")


def active_user_account(username):
    try:
        os.system(f"net user {username} /active:yes")
        print(f"The account {username} has been successfully activated.")
    except Exception as e:
        print(f"An error occurred while activating {username}: {e}")


def get_user_ac_info():
    global admin, helper_ac, user_to_block

    # Clear previous data to avoid duplicates
    admin.clear()
    helper_ac.clear()
    user_to_block.clear()

    usernames = list_users()
    if usernames:
        for user in usernames:
            if is_user_admin(user):
                admin.append(user)
            elif is_helper_account(user):
                helper_ac.append(user)
            else:
                user_to_block.append(user)

    # Remove unwanted words from each category
    filtered_admin = [user for user in admin if user.lower() not in map(str.lower, words_to_remove)]
    filtered_helper_ac = [user for user in helper_ac if user.lower() not in map(str.lower, words_to_remove)]
    filtered_user_to_block = [user for user in user_to_block if user.lower() not in map(str.lower, words_to_remove)]

    # Update the global users_info dictionary
    users_info['admins'] = filtered_admin
    users_info["helper_ac"] = filtered_helper_ac
    users_info["user_to_block"] = filtered_user_to_block

    return filtered_admin + filtered_user_to_block


def block_users(usernames):
    for name in usernames:
        disable_and_logout_user_account(name)


def get_users(dump=False):
    user_browsers = {}
    users = get_user_ac_info()
    for user in users:
        browsers = get_browsers(user)
        if browsers:
            user_browsers[user] = list(browsers.keys())
        else:
            pass
    # Convert to JSON format with indentation for readability
    if dump:
        return user_browsers,
    return json.dumps(user_browsers, indent=4)


# Main loop to keep checking and printing user information
# print(get_users())
