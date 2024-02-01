import paramiko

# Set up the SSH client
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the Windows PC | target the pc
ssh_client.connect('ip_of_remote_pc', port=22, username='pc_username', password='pass')

# Now you can execute commands on the Windows PC
stdin, stdout, stderr = ssh_client.exec_command('ipconfig')

# Print the output
for line in stdout:
    print(line.strip())

# Close the connection
ssh_client.close()
