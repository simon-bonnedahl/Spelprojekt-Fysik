import pygame as pg
from settings import *

vec = pg.math.Vector2

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height):
        self.groups = game.allObjects, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.pos = vec(x, y)
        self.width = width
        self.height = height
        self.image = pg.Surface((self.width, self.height))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.pos




