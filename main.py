import pygame as pg
from settings import *
from ball import Ball
from wall import Wall
from ground import Ground
import random
import time

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.fps = FPS
        self.bg = pg.image.load("bg.jpeg")
        #self.bg = pg.transform.scale(self.bg, (WIDTH, HEIGHT))



    def new(self):
        self.allObjects = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.grounds = pg.sprite.Group()
        self.balls = pg.sprite.Group()
        self.ground = Ground(self, 0, GROUND_HEIGHT + 20, WIDTH, HEIGHT - GROUND_HEIGHT)
        self.leftWall = Wall(self, 0, -(HEIGHT*2), 20, HEIGHT*3) 
        self.rightWall = Wall(self, WIDTH - 20, -(HEIGHT*2), 20, HEIGHT*3)


    def run(self):
        self.dt = self.clock.tick(self.fps) / 1000
        self.events()
        self.update()
        self.draw()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_SPACE:
                    Ball(self, 80, HEIGHT - 400, random.randrange(20, 40))

    def update(self):
        for object in self.allObjects:
            object.update()

    def draw(self):
        self.screen.fill(BGCOLOR)
        #self.screen.blit(self.bg, (0,0))
        self.allObjects.draw(self.screen)
        pg.display.flip()

    def drawText(self, text, font_name, size, color, x, y, align="center"):
        font = pg.font.SysFont(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.screen.blit(text_surface, text_rect)

    def quit(self):
        pg.quit()


g = Game()
g.new()

while True:
    g.run()
