# workable Approach
## openssl.cnf
```editorconfig
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name
prompt = no

[req_distinguished_name]
C = AU
ST = Some-State
O = Internet Widgits Pty Ltd

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
IP.1 = 127.0.0.1
IP.2 = 192.168.1.133
DNS.1 = 0.tcp.ap.ngrok.io

```
### After this run
```bash
openssl genpkey -algorithm RSA -out server.key
openssl req -new -key server.key -out server.csr -config server.cnf
openssl x509 -req -in server.csr -signkey server.key -out server.crt -extensions v3_req -extfile server.cnf
```


# 2nd Workable Approach For Remote Access
```bash
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes
openssl req -new -key server.key -out server.csr -config server.cnf
openssl x509 -req -in server.csr -signkey server.key -out server.crt -extensions v3_req -extfile server.cnf
```

Create a PKCS#12 file: Combine the server certificate and private key into a PKCS#12 file (.pfx or .p12). You can do this using OpenSSL:
```bash
openssl pkcs12 -export -out server.pfx -inkey server.key -in server.crt
```