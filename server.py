# Specify the absolute path to save the private key
import paramiko

key_path = "/home/bwithai/.ssh/01_id"

session = paramiko.SSHClient()

session.load_system_host_keys()

key_file = paramiko.RSAKey.from_private_key_file(key_path)

# connect to remote pc
session.connect(
    hostname='192.168.1.135',
    username='deskt',
    pkey=key_file,
    allow_agent=False,
    look_for_keys=False
)
