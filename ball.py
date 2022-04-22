import pygame as pg
from settings import *
import math 
vec = pg.math.Vector2

class Ball(pg.sprite.Sprite):
    def __init__(self, game, x, y, radius):
        self.groups = game.allObjects, game.balls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.radius = radius
        self.mass = self.radius *0.5
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
       
        for i in range(10):
            self.acc = vec(0, 0)
            self.getInputs()
            self.acc.y = GRAVITY
            #   self.acc += self.vel * -self.airResistance
            self.vel += self.acc * self.game.dt             #Delta time
            #applyAirResistance(self.vel, self.radius)
            self.pos += self.vel    

            """fg = -g * m
                vn = normalize(v)
                fd = -vn * 0.5f * p * Cd * A * v^2
                a = (fg + fd)/m
                v += a * dt
                x += v * dt"""
            
            """Force = Direction * Power
            Acceleration = Force / Mass
            Velocity += Acceleration * elapsedTime
            Position += Velocity * elapsedTime"""

            self.rect.centerx = self.pos.x
            self.collideWithEnviroment('x')
            self.rect.centery = self.pos.y
            self.collideWithEnviroment('y')
            self.collideWithBalls(self.game.balls)

        pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)





    def getInputs(self):
        self.keys = pg.key.get_pressed()
        if self.keys[pg.K_LEFT]:
            self.acc.x = -0.2
        if self.keys[pg.K_RIGHT]:
            self.acc.x = 0.2


    def jump(self):
        #self.vel.y -= self.jumpHeight
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
            
    def distanceTo(self, pos2, pos1):
        return math.sqrt((pos2.x - pos1.x)**2 + (pos2.y - pos1.y)**2)
    
    def collideWithBalls(self, balls):
        for ball in balls:
            if ball != self:
                distanceNextFrame = self.distanceTo(self.pos + self.vel, ball.pos + ball.vel);	
                if (distanceNextFrame - self.radius - ball.radius < 0):
                    
                    dist = self.distanceTo(self.pos, ball.pos);	

                    normalX = (ball.pos.x - self.pos.x) / dist
                    normalY = (ball.pos.y - self.pos.y) / dist

                    tangentX = -normalY
                    tangentY = normalX

                    dotProductTan1 = self.vel.x * tangentX + self.vel.y * tangentY
                    dotProductTan2 = ball.vel.x * tangentX + ball.vel.y * tangentY

                    dotProductNorm1 = self.vel.x * normalX + self.vel.y * normalY
                    dotProductNorm2 = ball.vel.x * normalX + ball.vel.y * normalY

                    mass1 = (dotProductNorm1 * (self.mass - ball.mass) + 2 * ball.mass * dotProductNorm2) / (self.mass + ball.mass)
                    mass2 = (dotProductNorm2 * (ball.mass - self.mass) + 2 * self.mass * dotProductNorm1) / (self.mass + ball.mass)

                    self.vel.x = tangentX * dotProductTan1 + normalX * mass1
                    self.vel.y = tangentY * dotProductTan1 + normalY * mass1

                    ball.vel.x = tangentX * dotProductTan2 + normalX * mass2
                    ball.vel.y = tangentY * dotProductTan2 + normalY * mass2