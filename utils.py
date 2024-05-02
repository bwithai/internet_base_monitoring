import os
import subprocess

from datetime import datetime


def get_database_url():
    url = "sqlite:///database.sqlite"
    return url


def today():
    # Get the current date and time
    current_datetime = datetime.now()

    # Format the date and time in ISO 8601 format
    iso_8601_format = current_datetime.isoformat()
    return iso_8601_format


def handle_ls(result):
    response = modify_result(result.stdout)
    return response


def modify_result(ls_response):
    response = ls_response.split('\n')
    directory_list = []
    file_list = []

    for item in response:
        if item:
            if "." in item:
                file_list.append(item)
            else:
                directory_list.append(item)

    result_json = {
        "directories": directory_list,
        "files": file_list
    }

    return result_json


async def is_client_admin(api_key: str):
    API_KEY = "admin"
    if api_key == API_KEY:
        return True  # Replace with your user model or identifier
    else:
        return False


def is_cd_cmd(command):
    # Split the input into command and arguments
    command_args = command.split()

    # Handle 'cd' command separately to change directories
    if command_args[0] == 'cd':
        return True
    else:
        return False


def maintain_client_status(command):
    if command.lower().startswith('status'):
        # Split the input into command and arguments
        command_args = command.split()
        active = int(command_args[1])
        return active


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
            cwd = os.getcwd()

            result = subprocess.run("ls", shell=True, capture_output=True, text=True)
            response = handle_ls(result)
            response['cwd'] = cwd
            return response

        else:
            return None
    except Exception as e:
        return f"%-> {e}"


async def download_file(websocket, filepath):
    file_data = b"<SOF>"
    try:
        with open(filepath, 'rb') as file:
            file_data = file.read()
            await websocket.send(file_data)
    except FileNotFoundError:
        await websocket.send(b'%-> Not found')


# def download_file(client_ws, filepath):
#     try:
#         with open(filepath, 'rb') as file:
#             data = file.read(4096)
#             while data:
#                 client_ws.send(data)
#                 data = file.read(4096)
#             client_ws.send(b"<EOF>")
#     except FileNotFoundError:
#         client_ws.send(b'%-> Not found')
#         client_ws.send(b"<EOF>")


async def receive_file(websocket, filename: str):
    file_path = f"download/{filename}"
    try:
        file_data = await websocket.receive_bytes()

        if file_data.startswith(b'%->'):
            return f"File not found: {filename}"
        else:
            with open(file_path, 'wb') as file:
                file.write(file_data)
            return f"Received and saved {file_path} successfully."
    except Exception as e:
        return f"Error receiving {filename}: {str(e)}"

# def receive_file(conn, filename):
#     file_bytes = b""
#     done = False
#     try:
#         while not done:
#             data = conn.receive_bytes(4096)
#             file_bytes += data
#             if b"<EOF>" in file_bytes:
#                 done = True
#
#         with open(filename, 'wb') as file:
#             file.write(file_bytes[:-5])
#
#         print(f"Downloaded {filename} successfully.")
#     except Exception as e:
#         print(f"Error downloading {filename}: {str(e)}")
