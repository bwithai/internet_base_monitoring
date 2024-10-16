import os
import pprint


def get_browser_hist_path(user, brows_name):
    local_path = f"C:\\Users\\{user}\\AppData\\Local"
    browser_type, brws_name = brows_name.split('_', maxsplit=1)
    root = local_path + "\\" + browser_type + "\\" + brws_name + "\\" + "User Data"

    # Check if the 'Local' directory exists
    if not os.path.exists(local_path):
        return None
    else:
        user_data_path = os.path.join(root, "Default", "History")
        if os.path.exists(user_data_path):
            return user_data_path


def get_browsers(user):
    browsers_user_have = {}
    # Define the path to the 'Local' folder
    local_path = f"C:\\Users\\{user}\\AppData\\Local"

    # Directory name to search for
    directory_to_find = "User Data"

    # Check if the 'Local' directory exists
    if not os.path.exists(local_path):
        pass
    else:
        # Walk through each folder in 'Local'
        for root, dirs, files in os.walk(local_path):
            # Check if the target directory is present
            if directory_to_find in dirs:
                user_data_path = os.path.join(root, directory_to_find, "Default", "History")

                # Check if the 'History' file exists
                if os.path.isfile(user_data_path):
                    # Extract the browser name based on the folder structure
                    parts = root.split(os.sep)
                    try:
                        local_index = parts.index("Local")
                        # Concatenate the next two parts to form the name
                        name = f"{parts[local_index + 1]}_{parts[local_index + 2]}"
                        browsers_user_have[name] = user_data_path
                    except (ValueError, IndexError):
                        print("Unable to determine the browser name from the path structure.")
        return browsers_user_have

# b = get_browsers('hp')
# pprint.pprint(b)
