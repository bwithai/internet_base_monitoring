import ssl
import websockets


async def client_handler():
    uri = "wss://localhost:8765"

    # Load client private key and certificate
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # ssl_context.load_cert_chain(certfile='keys/client_cert.pem', keyfile='keys/client_key.pem')

    # Load server certificate for verification
    ssl_context.load_verify_locations(cafile='keys/server_cert.pem')

    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        response = await websocket.recv()
        print(response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(client_handler())
