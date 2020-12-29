import asyncio
import websockets


class Room:
    def __init__(self):
        self.players = set()

    async def join(self, player):
        self.players.add(player)
        await self.broadcast(f'{player.remote_address[0]}:{player.remote_address[1]} is connect')

    def exit(self, player):
        self.players.remove(player)

    async def broadcast(self, msg):
        await asyncio.wait([player.send(msg) for player in self.players])

    async def send_to_others(self, player, msg):
        await asyncio.wait([p.send(msg) for p in set(self.players.difference(set(player)))])

r = Room()        

async def echo(websocket, path):
    async for message in websocket:
        if message == "join":
            if websocket not in r.players:
                await r.join(websocket)
            else:
                await websocket.send("already join!")
        else:
            await print(message)
        # data = await websocket.recv()
        # print(data)
        # await websocket.send(message)

start_server = websockets.serve(echo, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
