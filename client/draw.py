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
]
fps = 25
clock = pygame.time.Clock()
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
def screen2(play, play2, canvas, done):
    while not done:
        canvas.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            
        for i in range(play.height):
            for j in range(play.width):
                pygame.draw.rect(canvas, GRAY, [play.x + play.zoom * j, play.y + play.zoom * i, play.zoom, play.zoom], 1)
                if play.field[i][j] > 0:
                    pygame.draw.rect(canvas, colors[play.field[i][j]],
                                    [play.x + play.zoom * j + 1, play.y + play.zoom * i + 1, play.zoom - 2, play.zoom - 1])

        for i in range(play2.height):
            for j in range(play2.width):
                pygame.draw.rect(canvas, GRAY, [play2.x + play2.zoom * j + 400, play2.y + play2.zoom * i, play2.zoom, play2.zoom], 1)
                if play2.field[i][j] > 0:
                    pygame.draw.rect(canvas, colors[play2.field[i][j]],
                                    [play2.x + play2.zoom * j + 401, play2.y + play2.zoom * i + 1, play2.zoom - 2, play2.zoom - 1])


        if play.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in play.figure.image():
                        pygame.draw.rect(canvas, colors[play.figure.color],
                                        [play.x + play.zoom * (j + play.figure.x) + 1,
                                        play.y + play.zoom * (i + play.figure.y) + 1,
                                        play.zoom - 2, play.zoom - 2])
                        

        
        if play2.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in play2.figure.image():
                        pygame.draw.rect(canvas, colors[play2.figure.color],
                                        [play2.x + play2.zoom * (j + play2.figure.x) + 401,
                                        play2.y + play2.zoom * (i + play2.figure.y) + 1,
                                        play2.zoom - 2, play2.zoom - 2])
        
        font = pygame.font.SysFont('Calibri', 25, True, False)
        font1 = pygame.font.SysFont('Calibri', 65, True, False)
        text = font.render("Score: " + str(play.score), True, BLACK)
        text_game_over = font1.render("Game Over :( ", True, (255, 0, 0))
        canvas.blit(text, [0, 0])
        text = font.render("Score: " + str(play2.score), True, BLACK)
        canvas.blit(text, [410, 0])
        if play.state == "gameover":
            canvas.blit(text_game_over, [10, 200])
        if play2.state == "gameover":
            canvas.blit(text_game_over, [410, 200])
        pygame.display.flip()
        clock.tick(fps)