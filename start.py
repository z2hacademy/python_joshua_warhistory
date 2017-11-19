import sys, pygame
import os
import game
import time

pygame.init()

gameStage = game.GameStage(855, 480)

role1Image = game.load_image('resource/role1-1.gif')
background = pygame.image.load(os.path.join(os.path.dirname(__file__), 'resource/bg-1.png')).convert()

gameStage.set_background(background)
gameStage.addMovableObj(game.Role(role1Image, [0, 0], (20, 230)))
gameStage.open()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        else: gameStage.raise_event(event)
    gameStage.nextframe()
    time.sleep(0.1)