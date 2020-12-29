import asyncio
import websockets

class WebSocket:
    def __init__(self, host, port):
        self.uri = f"ws://{host}:{port}"
        
    
    async def consumer_handler(self, websocket):
        async for message in websocket:
            await self.on_message(websocket, message)
    
    async def producer_handler(self, websocket):
        pass
    
    def on_message(self, websocket, message):
        pass
    
    def send(self, message):
        pass
    
    async def handler(self):
        async with websockets.connect(self.uri) as websocket:
            consumer_task = asyncio.ensure_future(
                self.consumer_handler(websocket))
            producer_task = asyncio.ensure_future(
                self.producer_handler(websocket))
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            
            for task in pending:
                task.cancel()
            
        # message = input("Input: ")
        # await websocket.send(message)
        # while True:
        #     data = await websocket.recv()
        #     print(data)


host = "localhost"
port = "8765"

ws = WebSocket(host, port)

asyncio.get_event_loop().run_until_complete(ws.handler())
