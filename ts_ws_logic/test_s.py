import asyncio
import ssl
import websockets


async def server_handler(websocket, path):
    await websocket.send("Connection established.")


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile='keys/server_cert.pem', keyfile='keys/server_key.pem')

start_server = websockets.serve(server_handler, "localhost", 8765, ssl=ssl_context)


async def main():
    await start_server


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
