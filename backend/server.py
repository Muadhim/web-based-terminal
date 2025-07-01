import asyncio
import websockets
import sys
import os
sys.path.append(os.path.dirname(__file__))
from user_session import add_session, remove_session, is_valid_token
import urllib.parse
from datetime import datetime

from shell_manager import ShellSession
from config import PORT, SHELL

async def handle_terminal(websocket, path):
    parsed = urllib.parse.urlparse(path)
    query = urllib.parse.parse_qs(parsed.query)
    token = query.get("token", [None])[0]

    if not is_valid_token(token):
        await websocket.send("Unauthorized")
        await websocket.close()
        return

    if not add_session(token, websocket):
        await websocket.send("Session already active")
        await websocket.close()
        return

    username = "admin"
    logfile = f"logs/{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    os.makedirs("logs", exist_ok=True)

    shell = ShellSession(shell_path=SHELL)

    async def read_from_shell():
        while True:
            await asyncio.sleep(0.01)
            data = shell.read()
            if data:
                await websocket.send(data)
                with open(logfile, "a") as f:
                    f.write(f">> {data}")

    async def write_to_shell():
        async for message in websocket:
            shell.write(message)
            with open(logfile, "a") as f:
                f.write(f"<< {message}")

    try:
        await asyncio.gather(read_from_shell(), write_to_shell())
    except Exception as e:
        print(f"Connection closed: {e}")
        pass
    finally:
        shell.close()
        remove_session(token)

async def main():
    print(f"Starting WebSocket server on ws://localhost:{PORT}")
    async with websockets.serve(handle_terminal, "0.0.0.0", PORT):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
