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
        return f"%-> {e}"


def download_file(client_socket, filepath):
    print("start reading")
    try:
        with open(filepath, 'rb') as file:
            data = file.read(4096)
            while data:
                client_socket.sendall(data)
                data = file.read(4096)

    except FileNotFoundError:
        client_socket.sendall(b'%-> Not found')


def receive_file(conn, filename):
    print("start receiving")
    try:
        with open(filename, 'wb') as file:
            data = conn.recv(4096)
            while data:
                file.write(data)
                data = conn.recv(4096)
        print(f"Downloaded {filename} successfully.")
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")
