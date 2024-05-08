import os
import subprocess

from datetime import datetime

cert_text = """
-----BEGIN CERTIFICATE-----
MIIFlDCCA3ygAwIBAgIUN6lw+E6vSCa6kF1GyGEYvRr+nlUwDQYJKoZIhvcNAQEL
BQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM
GEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0yNDA1MDIwNTU0MTFaFw0yNDA2
MDEwNTU0MTFaMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw
HwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggIiMA0GCSqGSIb3DQEB
AQUAA4ICDwAwggIKAoICAQDjkZuhS4pnA1p4dH2u8vaZOOM7TmWd6fXLcB9BMaPz
7M7jP8tXq9UXzOItmite4bkr25wKj9XnrMVGkMD3vDZj4ppwPyyUlI3ufT+41VS2
XaXjPYLWPG7f8RQ5W/oWLcRpmwMaCSdbTl+qWBSUO4WbPAOuDordlAeOpyklYyw0
4iHtbD6HGjH3AU5c7D1tN+HcyiDUYYXfZQawH22lFQgocJWAI1hI+tl8XMw4dBl7
PTjvjR1dKH9tH7xhtite9QT5Vg9+0ni1jEt6O/dfY0yCvL+OWVrBDXpvF5CJC7dy
NtBnSM43pgWjNT2Sz5wTViaF2rh8lqXyxsqmJUORYUkoHzqWLRL0SMsJFXXnGCc5
RtMKOwd/emwoINwV+GJ66ypY3QdDdrfomaPgitxpNROxcJe1BpNVx/Y1u9Xp99yH
jLfhv5LWsafBOusuByLCPOpjUrYXPaxpSH2jgTWxdHX50alFqynw+knob6hubNZe
k1PUFjttQxHEa+IgErW1dnQzrBsd5j2+MG+BG2ba+ic5h5jAgBugJvAxy+COCbMR
vYPiTTYQVNEH2G9zM9mjyO+FqLl8kxXzJNfGswKvS/KQY8y0YjjqtV7OuO7qxMe3
owMojcPRTRDzEe6wm8o4G/VCRLFSVPpZ3W/cZTm3csxzfrBNVm2wqBJHPtseXuzY
OQIDAQABo3wwejAJBgNVHRMEAjAAMAsGA1UdDwQEAwIF4DBBBgNVHREEOjA4hwR/
AAABhwTAqAF9hwTAqAFyghEwLnRjcC5hcC5uZ3Jvay5pb4IRMC50Y3AuYXUubmdy
b2suaW8wHQYDVR0OBBYEFCQppvLkqAgOgmrVfK78Ackmt1puMA0GCSqGSIb3DQEB
CwUAA4ICAQDjaavK1WC3yjRJwLExOAeWSLUaM9Ru4qfOCnRHp49HbhKXUW+o5qmg
ZGSCfkgw6L4bZ0cOnA6DIKuF5/ixw/wNrE5jjgQ2gjSpVGv6X72A80R9jvnIamwE
RDePF+qDvY7OrGJsgZKYCHWe0qJh2UfqBO/xlOlCllEWNxtNdXfkOymH7zEgWjzT
wyEZkP0Lon2jQmfN5VEhRhGCFLNn9mlWh55H9WZETuxIfbHt9rzlf+zup0sfkal2
S0eYPZrJm+iDcJ6+ZGHYaJXGjtzH8MnrU0AGfuQBINHVdi/Hbjd6Y3OfZU0KpdrU
YuaQQ42jPJdxMn29NhjeWGMYxvg/zuIDokaG31spaCRFpNREDGvWt0YbdMG9YBNK
YC62ztF5trxYoCaA3fhpCJXB66+6uo9NTmQsO2w09UN+LRfmi0twC0+rFTkcQl3S
2CNBIxPygxzkAc9dlzG/XZMKOPReMX5Q84BvzwjdPUVXsx9flpiEJJySANDJaQtl
jvSEEgdkIX48RFJ+yTIYk2Xjn0WkfufTU5F8y+fhJu9dUBPKrBmAyGyZD4DvEHXH
lNFP1u83Q/SoVXSh66275OqmVs49XbdD9EMwHGpLYDzbqNC0K1mrw465yL6jI9f4
7pOM5UbkZTtGFY5ii8u2JNzzIkkIONSnyXvcmBlw/JFIk6/wSMgUSA==
-----END CERTIFICATE-----
"""


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
