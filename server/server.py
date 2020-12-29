import asyncio
import websockets


class Room:
    def __init__(self):
        self.players = set()

    async def join(self, player):
        self.players.add(player)
        await self.broadcast(f'{player.remote_address[0]}:{player.remote_address[1]} is connect')
        
        if len(self.players) == 2:
            await self.start()
            
    async def start(self):
        pass

    def exit(self, player):
        self.players.remove(player)

    async def broadcast(self, msg):
        await asyncio.wait([player.send(msg) for player in self.players])

    async def send_to_others(self, player, msg):
        targets = self.players - set([player])
        if targets:
            await asyncio.wait([p.send(msg) for p in targets])


async def handler(websocket, path):
    async for message in websocket:
        if message == "join":
            if websocket not in r.players:
                await r.join(websocket)
            else:
                await websocket.send("already join!")
        else:
            print(message)
            await r.send_to_others(websocket, message)
        # data = await websocket.recv()
        # print(data)
        # await websocket.send(message)

if __name__ == "__main__":
    r = Room()

    start_server = websockets.serve(handler, "localhost", 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
