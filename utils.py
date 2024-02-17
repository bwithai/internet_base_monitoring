import os


def is_cd_cmd(command):
    # Split the input into command and arguments
    command_args = command.split()

    # Handle 'cd' command separately to change directories
    if command_args[0] == 'cd':
        return True
    else:
        return False


def handle_cd(command):
    try:
        # Split the input into command and arguments
        command_args = command.split()

        # Handle 'cd' command separately to change directories
        if command_args[0] == 'cd':
            # Join the arguments to form the directory path
            directory_path = ' '.join(command_args[1:])
            # Change the current working directory
            os.chdir(os.path.expanduser(directory_path))
            return os.getcwd()
        else:
            return None
    except Exception as e:
        return f"An error occurred: {e}"