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
    try:
        with open(filepath, 'rb') as file:
            data = file.read()
            client_socket.sendall(data)
            client_socket.send(b"<EOF>")
    except FileNotFoundError:
        client_socket.sendall(b'%-> Not found')
        client_socket.send(b"<EOF>")


def receive_file(conn, filename):
    file_bytes = b""
    done = False
    try:
        while not done:
            data = conn.recv(4096)
            if file_bytes[-5:] == b"<EOF>":
                done = True
            else:
                file_bytes += data

        with open(filename, 'wb') as file:
            file.write(file_bytes[:-5])

        print(f"Downloaded {filename} successfully.")
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")
