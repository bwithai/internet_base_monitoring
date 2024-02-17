import socket
import os

from utils import is_cd_cmd


def start_server():
    host = '127.0.0.1'
    port = 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"Server listening on {host}:{port}")

        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")
            cwd = conn.recv(4096).decode('utf-8')

            while True:
                command = input(f"{cwd} $ ")
                conn.sendall(command.encode('utf-8'))

                if command.lower() == 'exit':
                    break

                # Receive and print the output from the client
                response = conn.recv(4096).decode('utf-8')

                if is_cd_cmd(command):
                    cwd = response
                    # print(cd_result)
                    continue
                else:
                    print(response)


if __name__ == "__main__":
    start_server()
