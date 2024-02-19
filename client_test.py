import paramiko
# import logging

# Set the logging level to DEBUG
# logging.basicConfig(level=logging.DEBUG)

# Replace these variables with your own values
PRIVATE_KEY_PATH = "/home/bwithai/.ssh/01_id"
# SERVER_HOST = "192.168.1.122"
SERVER_HOST = "192.168.1.113"

# Load the private key
try:
    private_key = paramiko.RSAKey(filename=PRIVATE_KEY_PATH)
except Exception as e:
    print(f"[-] Unable to load private key: {e}")
    raise SystemExit

# Create an SSH client
ssh_client = paramiko.SSHClient()

# Automatically add the server's host key (this is insecure, better to verify manually)
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect to the server
    ssh_client.connect(SERVER_HOST, port=2222, pkey=private_key)

    # Perform actions on the server (e.g., execute a command)
    stdin, stdout, stderr = ssh_client.exec_command("ls -l")
    print(stdout.read().decode('utf-8'))

except Exception as e:
    print(f"[-] Unable to connect to the server: {e}")

finally:
    # Close the SSH connection
    ssh_client.close()
