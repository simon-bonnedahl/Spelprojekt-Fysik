import pygame as pg
from settings import *
vec = pg.math.Vector2

class Ball(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.allObjects
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.radius = 30
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.jumpHeight = JUMPING_HEIGHT
        self.onGround = True

        self.image = pg.Surface((self.radius*2, self.radius*2))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        self.color = LIGHTGREY
        self.skin = True



    def update(self):  
       
        pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        
        self.getInputs()
        self.acc.y = GRAVITY

        self.vel += self.acc
        self.pos += self.vel

        self.rect.centerx = self.pos.x
        self.collideWithEnviroment('x')
        self.rect.centery = self.pos.y
        self.collideWithEnviroment('y')





    def getInputs(self):
        self.keys = pg.key.get_pressed()
        self.acc = vec(0, 0)
        if self.keys[pg.K_LEFT]:
            self.acc.x = -0.2
        if self.keys[pg.K_RIGHT]:
            self.acc.x = 0.2
        if self.keys[pg.K_SPACE]:

            if self.onGround:
                self.jump()


    def jump(self):
        self.vel.y -= self.jumpHeight
        self.onGround = False

    def collideWithEnviroment(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                self.vel.x *= -0.95 #-0.95 om 5% av energin försvinner vid studs
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.grounds, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height / 2
                    self.onGround = True
                if self.vel.y < 0.2:
                    self.pos.y = hits[0].rect.bottom + self.rect.height / 2
                else:
                    self.vel.y *= -0.95  #-0.95 om 5% av energin försvinner vid studs
            

