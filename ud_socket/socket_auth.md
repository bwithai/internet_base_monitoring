# workable Approach
## openssl.cnf
```editorconfig
[req]
distinguished_name = req_distinguished_name
req_extensions = req_ext
prompt = no

[req_distinguished_name]
CN = 127.0.0.1

[req_ext]
subjectAltName = @alt_names

[alt_names]
IP.1 = 127.0.0.1
IP.2 = 192.168.88.77
DNS.1 = 0.tcp.ap.ngrok.io

```
### After this run
```bash
openssl genpkey -algorithm RSA -out server.key
openssl req -new -key server.key -out server.csr -config openssl.cnf
openssl x509 -req -in server.csr -signkey server.key -out server.crt -extfile openssl.cnf -extensions req_ext -days 365

```