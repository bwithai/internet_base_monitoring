import paramiko

# Specify the path where you want to save the private key
key_path = "/home/bwithai/.ssh/01_id"

# Generate an RSA key pair
key = paramiko.RSAKey.generate(2048)

# Save the private key
key.write_private_key_file(key_path)

# Save the public key (optional)
with open(key_path + '.pub', 'w') as f:
    f.write(f'{key.get_name()} {key.get_base64()} your_comment')
