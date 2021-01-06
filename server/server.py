import asyncio
import websockets
import pymysql
import json


class Room:
    def __init__(self):
        self.players = set()
        self.alive = 0

    async def join(self, ws):
        self.players.add(ws)
        player = f'{ws.remote_address[0]}:{ws.remote_address[1]}'
        await self.broadcast(f'{player} is connect')
        print(f'{player} is connected.')
        
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

async def submit_record(player, score):
    print(player, score)
    db = pymysql.connect(host="127.0.0.1", port=3306, user='test1',
                         passwd='test1', db='tetris', charset='utf8')
    cursor = db.cursor()
    sql = f"select * from record where player='{player}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 0:
        sql = f"INSERT INTO record(player, score) VALUES ('{player}', {score})"
        cursor.execute(sql)
        db.commit()
    else:
        for row in result:
            if score > row[2]:
                sql = f"UPDATE record SET score={score} WHERE player='{player}'"
                cursor.execute(sql)
                db.commit()
                break
    db.close()
    
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
                parse_msg = json.loads(message)
                if parse_msg['type'] == 'submit':
                    await submit_record(
                        parse_msg['data']['player'], parse_msg['data']['score'])
                for r in rooms:
                    if websocket in r.players:
                        await r.send_to_others(websocket, message)
    except:
        for r in rooms:
            if websocket in r.players:
                await r.exit(websocket)


if __name__ == "__main__":
    rooms = []

    start_server = websockets.serve(handler, "192.168.0.107", 8765)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
