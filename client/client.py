from threading import Thread
import time
import websocket
import pygame
import random
import json 

colors = [
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
    (255, 255, 255)
]


class Figure:
    x = 0
    y = 0
    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
        [[5, 6, 10, 11], [7, 10, 11 , 14], [9, 10, 14, 15], [6, 9, 10, 13]], 
        [[6, 7, 9, 10], [6, 10, 11, 15], [10, 11, 13, 14], [5, 9, 10, 14]]
    ]

    def __init__(self, x, y, times, space_status):
        self.x = x
        self.y = y
        self.times = times
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 2)
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])

    def __str__(self):
        return json.dumps({
            'times' : self.times,
            'x' : self.x,
            'y' : self.y,
            'type' : self.type,
            'color' : self.color,
            'rotation' : self.rotation
        })

    def __repr__(self):
        return self.__str__()

class Tetris:
    level = 2
    score = 0
    state = "start"
    height = 0
    width = 0
    zoom = 20
    t = 1
    figure = None

    def __init__(self, x, y, height, width):
        self.x = x
        self.y = y
        self.sound = False
        self.height = height
        self.width = width
        self.field = []
        self.old_socore = 0

        for i in range(height): 
            self.new_line = []
            for j in range(width):
                self.new_line.append(7)
            self.field.append(self.new_line.copy())
        
        self.temp_field = self.field.copy()

    def new_figure(self):
        self.figure = Figure(3, 0, self.t, 0)
        self.t += 1

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] != 7:
                        intersection = True
        return intersection
    
    def stone(self, a):
        add = a
        for i in range(self.height - 1, 0):
            empty = random.randint(0, self.width)
            for j in range(self.width - 1, 0):
                if add > 0:
                    if j != empty:
                        self.temp_field[i][j] = 0
                    else:
                        self.temp_field[i][j] = 7
                else:
                    self.temp_field[i][j] = 0
            add -= 1

        for i in range(self.height):
            for j in range(self.width):
                self.field[i][j] = self.temp_field[i][j]


    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 7:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score += lines ** 2

    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        if self.state != 'gameover':
            self.send_figure(ws)
        self.freeze()
    
    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        if self.sound:
            pygame.mixer.Sound('./music/freeze.wav').play()

        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"
        
    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x
    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        pygame.mixer.Sound('./music/rotate.mp3').play()

        if self.intersects():
            self.figure.rotation = old_rotation
    
    def send_figure(self, ws):
        ws.send(str(self.figure))


class Player:
    status = str()
    def __str__(self):
        return self.status


def on_message(ws, message):
    global player, play2
    if message == 'start':
        player.status = message
        play2.new_figure()
    elif player.status == 'start' and message != 'over':
        msg = json.loads(message)
        if msg['times'] == 1 or msg['times'] == play2.figure.times:
            play2.figure.times = msg['times']
            play2.figure.x = msg['x']
            play2.figure.y = msg['y']
            play2.figure.type = msg['type']
            play2.figure.color = msg['color']
            play2.figure.rotation = msg['rotation']
        else:
            play2.freeze()
            play2.figure.times = msg['times']
    elif message == 'over' and player.status == 'start':
        play2.state = 'gameover'
        player.status = 'over'
    else:
        print(message)

def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")

if __name__ == "__main__":
    play1 = Tetris(100, 60, 20, 10)
    play2 = Tetris(100, 60, 20, 10)
    play1.sound = True
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8765",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    # ws.on_open = on_open
    ws_thread = Thread(target=ws.run_forever)
    ws_thread.start()
    player = Player()
    msg = input()
    ws.send(msg)
    while player.status != 'start':
        pass
    # print(p.status)
    # 初始化遊戲引擎
    pygame.init()
    # 定義一些顏色  
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    size = (800, 600)  
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Tetris")
    
    # 循環，直到用户點擊關閉按鈕
    done = False
    clock = pygame.time.Clock()
    fps = 25
    counter = 0 
    pressing_down = False    
    # play2_thread = Thread(target=screen2, args=(play1, play2, screen, done))
    # play2_thread.start()
    pygame.mixer.music.load('./music/background.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)
    stop = 0
    add = 0
    while not done:
        if play1.figure is None:
            play1.new_figure()

        counter += 1
        if counter > 100000:
            counter = 0

        if counter % (fps // play1.level // 2) == 0 or pressing_down:
            if play1.state == "start":
                play1.go_down()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if not play1.state == 'gameover':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        play1.rotate()
                        play1.send_figure(ws)
                    if event.key == pygame.K_DOWN:
                        pressing_down = True
                        play1.send_figure(ws)
                    if event.key == pygame.K_LEFT:
                        play1.go_side(-1)
                        play1.send_figure(ws)
                    if event.key == pygame.K_RIGHT:
                        play1.go_side(1)
                        play1.send_figure(ws)
                    if event.key == pygame.K_SPACE:
                        play1.go_space()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        pressing_down = False
        if not play1.state == 'gameover':
            play1.send_figure(ws)
        screen.fill(WHITE)

#         if play1.score - play1.old_socore > 0:
#             add = play1.score - play1.old_socore
#             play2.stone(add)
#             play1.old_socore = play1.score
#         if play2.score - play2.old_socore > 0:
#             add = play2.score - play2.old_socore
#             play1.stone(add)
#             play2.old_socore = play2.score

        for i in range(play1.height):
            for j in range(play1.width):
                pygame.draw.rect(screen, GRAY, [play1.x + play1.zoom * j, play1.y + play1.zoom * i, play1.zoom, play1.zoom], 1)
                if play1.field[i][j] != 7:
                    pygame.draw.rect(screen, colors[play1.field[i][j]],
                                    [play1.x + play1.zoom * j + 1, play1.y + play1.zoom * i + 1, play1.zoom - 2, play1.zoom - 1])

        for i in range(play2.height):
            for j in range(play2.width):
                pygame.draw.rect(screen, GRAY, [play2.x + play2.zoom * j + 400, play2.y + play2.zoom * i, play2.zoom, play2.zoom], 1)
                if play2.field[i][j] != 7:
                    pygame.draw.rect(screen, colors[play2.field[i][j]],
                                    [play2.x + play2.zoom * j + 401, play2.y + play2.zoom * i + 1, play2.zoom - 2, play2.zoom - 1])


        if play1.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in play1.figure.image():
                        pygame.draw.rect(screen, colors[play1.figure.color],
                                        [play1.x + play1.zoom * (j + play1.figure.x) + 1,
                                        play1.y + play1.zoom * (i + play1.figure.y) + 1,
                                        play1.zoom - 2, play1.zoom - 2])
                        

        
        if play2.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in play2.figure.image():
                        pygame.draw.rect(screen, colors[play2.figure.color],
                                        [play2.x + play2.zoom * (j + play2.figure.x) + 401,
                                        play2.y + play2.zoom * (i + play2.figure.y) + 1,
                                        play2.zoom - 2, play2.zoom - 2])
        

        font = pygame.font.SysFont('Calibri', 25, True, False)
        font1 = pygame.font.SysFont('Calibri', 65, True, False)
        text = font.render("Score: " + str(play1.score), True, BLACK)
        text_game_over = font1.render("Game Over :( ", True, (255, 0, 0))
        screen.blit(text, [0, 0])
        text = font.render("Score: " + str(play2.score), True, BLACK)
        screen.blit(text, [410, 0])
        if play1.state == "gameover":
            screen.blit(text_game_over, [10, 200])
            if stop == 0:
                play1.send_figure(ws)
                stop += 1
                ws.send('over')
        if play2.state == "gameover":
            screen.blit(text_game_over, [410, 200])
        if play1.state == 'gameover' and play2.state == 'gameover':
            pygame.mixer.music.stop()
            done = True
            
        pygame.display.flip()
        clock.tick(fps)
    pygame.quit()
    ws.send(f'gameover:{play1.score}')
    
