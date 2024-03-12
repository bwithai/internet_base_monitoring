```bash
# Generate server private key and certificate
openssl req -newkey rsa:2048 -nodes -keyout server_key.pem -x509 -days 365 -out server_cert.pem -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost"
```