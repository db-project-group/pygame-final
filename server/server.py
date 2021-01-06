import asyncio
import websockets
import pymysql

db_settings = {
    "host" : "127.0.0.1",
    "port" : 3306,
    "user" : "root",
    "password" : "",
    "db" : 'login',
    "charset" : "utf-8"
}
table_name = 'user'

class Room:
    def __init__(self):
        self.players = set()
        self.alive = 0

    async def join(self, ws):
        self.players.add(ws)
        player = f'{ws.remote_address[0]}:{ws.remote_address[1]}'
        await self.broadcast(f'{player} is connect')
        
        if len(self.players) == 2:
            await self.start()
            

    async def start(self):
        await self.broadcast('start')
        self.alive = 2

    async def exit(self, ws):
        self.players.remove(ws)
        player = f'{ws.remote_address[0]}:{ws.remote_address[1]}'
        await self.send_to_others(ws, f'{player} is exited')

    async def broadcast(self, msg):
        await asyncio.wait([player.send(msg) for player in self.players])

    async def send_to_others(self, ws, msg):
        targets = self.players - set([ws])
        if targets:
            await asyncio.wait([p.send(msg) for p in targets])

async def handler(websocket, path):
    try:
        async for message in websocket:
            if message == "join":
                if not rooms:
                    r = Room()
                    rooms.append(r)
                    
                for r in rooms:
                    if len(r.players) < 2:
                        await r.join(websocket)
                    
            elif message == 'over':
                print(message)
                for r in rooms:
                    if websocket in r.players:
                        await r.send_to_others(websocket, message)
                        # await r.exit(websocket)
                        r.alive -= 1
                        if r.alive <= 0:
                            r.players = set()
            else:
                for r in rooms:
                    if websocket in r.players:
                        await r.send_to_others(websocket, message)
    except:
        await r.exit(websocket)


if __name__ == "__main__":
    rooms = []

    start_server = websockets.serve(handler, "localhost", 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
