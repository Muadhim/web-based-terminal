import asyncio
import websockets
import sys
import os
sys.path.append(os.path.dirname(__file__))

from shell_manager import ShellSession
from config import PORT, SHELL

async def handle_terminal(websocket):
    shell = ShellSession(shell_path=SHELL)

    async def read_from_shell():
        while True:
            await asyncio.sleep(0.01)
            data = shell.read()
            if data:
                await websocket.send(data)

    async def write_to_shell():
        async for message in websocket:
            shell.write(message)

    try:
        await asyncio.gather(read_from_shell(), write_to_shell())
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        shell.close()

async def main():
    print(f"Starting WebSocket server on ws://localhost:{PORT}")
    async with websockets.serve(handle_terminal, "0.0.0.0", PORT):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
