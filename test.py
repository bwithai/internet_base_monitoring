import socket
import threading
import paramiko

# Replace these variables with your own values
PRIVATE_KEY_PATH = "/home/bwithai/.ssh/01_id"
HOST, PORT = '0.0.0.0', 2222

# Load the private key
try:
    HOST_KEY = paramiko.RSAKey(filename=PRIVATE_KEY_PATH)
except Exception as e:
    print(f"[-] Unable to load private key: {e}")
    raise SystemExit


class SSHServer(paramiko.ServerInterface):
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        # Replace this with your own authentication logic
        return paramiko.AUTH_SUCCESSFUL


# Create the SSH server
try:
    ssh_server = paramiko.Transport((HOST, PORT))
    ssh_server.add_server_key(HOST_KEY)
except Exception as e:
    print(f"[-] Unable to create SSH server: {e}")
    raise SystemExit

# Start the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    print(f"[*] Listening for connections on {HOST}:{PORT}")

    while True:
        client_socket, client_addr = server_socket.accept()
        print(f"[*] Accepted connection from {client_addr[0]}:{client_addr[1]}")

        try:
            ssh_server.start_server(server=SSHServer())
            channel = ssh_server.accept(20)
            if channel is not None:
                print("[*] Authenticated!")
                channel.send("Welcome to my custom SSH server!")
                channel.close()
        except Exception as e:
            print(f"[-] Exception: {e}")
        finally:
            client_socket.close()

except Exception as e:
    print(f"[-] Exception: {e}")
finally:
    server_socket.close()
