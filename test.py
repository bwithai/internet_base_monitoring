import subprocess
import os
import getpass

# Assume a list of administrator usernames
admin_users = ["admin"]

current_directory = os.getcwd()

while True:
    # Display the current directory in the prompt
    user_input = input(f"{current_directory} >>> ")

    # Exit the loop if the user types "exit" or "quit"
    if user_input.lower() in ['exit', 'quit']:
        break

    # Handle the "cd" command to change directory
    if user_input.startswith('cd '):
        new_directory = user_input[3:].strip()
        try:
            # Change the current directory
            os.chdir(new_directory)
            current_directory = os.getcwd()
        except FileNotFoundError:
            print(f"Directory not found: {new_directory}")
        continue

    # Check if the user is an administrator before executing certain commands
    if any(user_input.startswith(command) for command in admin_users):
        username = input("Enter your username: ")
        if username.lower() not in admin_users:
            print("Permission denied. Only administrators can run this command.")
            continue

        # Strip 'admin ' from the command and execute with sudo
        admin_command = user_input[len('admin '):]
        try:
            result = subprocess.run(f"sudo {admin_command}", shell=True, capture_output=True, text=True, input=getpass.getpass())
            print(result.stdout)
            if result.stderr:
                print("Error:", result.stderr)
        except Exception as e:
            print("An error occurred:", e)
        continue

    try:
        # Execute the command and capture the output
        result = subprocess.run(user_input, shell=True, capture_output=True, text=True)

        # Print the command output
        print(result.stdout)

        # Print any errors
        if result.stderr:
            print("Error:", result.stderr)

    except Exception as e:
        print("An error occurred:", e)
