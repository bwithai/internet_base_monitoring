import socket
import threading


def handle_client(client_socket, address, client_id):
    while True:
        message = input(f"Enter message from server to {client_id}: ")
        client_socket.send(message.encode())

        user_input = client_socket.recv(1024).decode()
        print(f"Received from client-{client_id} ({address}): {user_input}")

        if user_input.lower() == 'exit':
            break

    client_socket.close()
    print(f"Connection with client-{client_id} ({address}) closed")


# def send_message_to_clients(clients):
#     # for client_socket, _, _ in clients:
#     for i, client in enumerate(clients):
#         print(i, " - ", client)
#
#     client_to_send_message = input("Enter which clinet to send message: ")
#     message = input("Enter message: ")
#     try:
#         client_to_send_message.send(message.encode())
#     except socket.error:
#         # Handle disconnected clients
#         pass


def start_server():
    host = '127.0.0.1'
    port = 12345

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)  # Allow up to 2 clients to connect

    print(f"Server listening on {host}:{port}")

    clients = []
    client_id_counter = 1
    while True:
        client_socket, address = server_socket.accept()

        print(f"Accepted connection from {address}")

        client_handler = threading.Thread(target=handle_client, args=(client_socket, address, client_id_counter))
        client_handler.start()

        clients.append((client_socket, address, client_id_counter))

        # Send a welcome message to the newly connected client
        # send_message_to_clients(clients)

        client_id_counter += 1


if __name__ == "__main__":
    start_server()
