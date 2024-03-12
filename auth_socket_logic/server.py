# server.py
import ssl

from fastapi import FastAPI, WebSocket

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='server.crt', keyfile='server.key')

    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print(f"Received: {data}")

        response = input("send message to client: ")
        await websocket.send_text(response)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=12345, ssl_keyfile='./server.key', ssl_certfile='./server.crt',
                log_level="info")
