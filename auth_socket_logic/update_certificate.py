import ssl
import asyncio
import websockets


def fetch_updated_certificate():
    pass


async def update_certificate():
    # Implement logic to retrieve the updated certificate from a secure source.
    # You can use an API endpoint or any other secure method.
    updated_certificate = fetch_updated_certificate()

    # Save the updated certificate to a secure location.
    with open('../updated_server.crt', 'w') as f:
        f.write(updated_certificate)


async def start_client():
    while True:
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

            # Load the trusted CA certificate (updated_server.crt or server.crt).
            ssl_context.load_verify_locations(cafile='../updated_server.crt')

            async with websockets.connect(
                    'wss://127.0.0.1:12345/ws',
                    ssl=ssl_context
            ) as websocket:
                data_to_send = input("Send message to server: ")
                await websocket.send(data_to_send)

                received_message = await websocket.recv()
                print("Received:", received_message)
        except ssl.SSLError as e:
            print(f"SSL error: {e}")
            await update_certificate()


if __name__ == "__main__":
    asyncio.run(start_client())
