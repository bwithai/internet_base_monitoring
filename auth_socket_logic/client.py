# client.py
import ssl
import asyncio
import websockets


async def start_client():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(cafile='./server.crt')

    async with websockets.connect(
            'wss://127.0.0.1:12345/ws',  # Change to your server IP address and port
            ssl=ssl_context
    ) as websocket:
        while True:
            data_to_send = input("Send message to server: ")
            await websocket.send(data_to_send)

            received_message = await websocket.recv()
            print("Received:", received_message)


if __name__ == "__main__":
    asyncio.run(start_client())
