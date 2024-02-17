import os
import subprocess

while True:
    # Get user input for the command
    user_input = input(f"{os.getcwd()} $ ")

    # Check if the user wants to exit the terminal
    if user_input.lower() == 'exit':
        break

    try:
        # Split the input into command and arguments
        command_args = user_input.split()

        # Handle 'cd' command separately to change directories
        if command_args[0] == 'cd':
            # Join the arguments to form the directory path
            directory_path = ' '.join(command_args[1:])
            # Change the current working directory
            os.chdir(os.path.expanduser(directory_path))
        else:
            # Run the command and capture the output
            result = subprocess.run(user_input, shell=True, capture_output=True, text=True)

            # Print the output
            print(result.stdout, end='')

            # Print any errors
            if result.stderr:
                print(result.stderr, end='')

    except Exception as e:
        print(f"An error occurred: {e}")