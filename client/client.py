import asyncio
import websockets


async def hello():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        message = input("Input: ")
        await websocket.send(message)
        while True:
            data = await websocket.recv()
            print(data)


asyncio.get_event_loop().run_until_complete(hello())
# asyncio.get_event_loop().run_forever()
