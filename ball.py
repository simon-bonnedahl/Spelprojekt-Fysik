import pygame as pg
import pygame.gfxdraw
from settings import *
import math 
vec = pg.math.Vector2
import random


class Ball(pg.sprite.Sprite):
    def __init__(self, game, x, y, radius):
        self.groups = game.allObjects, game.balls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        #Fysik
        self.density = 5
        self.radius = radius
        self.area = self.radius**2 * math.pi
        self.mass = self.area*self.density
        self.pos = vec(x, y)
        self.vel = vec(5, -5)                   #initital hastighetesvektor
        self.acc = vec(0, 0)
        self.onGround = False

        #Grafik
        self.sprite = pg.image.load("sprite_{}.png".format(random.randrange(1, 5))).convert_alpha()
        self.image = pg.transform.scale(self.sprite, (self.radius*2, self.radius*2))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos




    def update(self):  
        #Updaterar krafterna som påverkar bollen, acceleration, hastighet och läge
        dragForce = vec(0, 0)
        gravityForce = vec(0, 0)
        frictionForce = vec(0, 0)
        if self.onGround != True:                           #Om en boll är i luften, räkna ut gravitationen
            self.acc = vec(0, GRAVITY)
            gravityForce = self.acc * self.mass             #F = m * a
        else:                                               #Om en boll är på marken, räkna ut friktionen
            self.acc = vec(0, 0)
            normalForce = self.mass * GRAVITY               #Normalkraften = Gravitationskraften
            frictionForce = -self.vel.normalize() * normalForce * FRICTION_CONSTANT                    

        
        if self.vel.magnitude() > 0.01:                        #Om bollen är i rörelse, räkna ut luftmotståndet
            dragForce = -self.vel.normalize() * (DRAG_CONSTANT * AIR_DENSITY * self.area * self.vel.magnitude_squared())/2
        else:
            self.vel = vec(0, 0)
        nettoForce = gravityForce + dragForce + frictionForce
        self.acc = (nettoForce)/self.mass   

        self.vel += self.acc * self.game.dt             #Delta tid
        self.pos += self.vel    

        #Kollisoner
        self.rect.centerx = self.pos.x
        self.collideWithEnviroment('x')
        self.rect.centery = self.pos.y
        self.collideWithEnviroment('y')

        self.collideWithBalls(self.game.balls)
        
       

        #Rendering
        
        #pygame.gfxdraw.aacircle renderas bättre än pygame.draw.circle
       # pygame.gfxdraw.aacircle(self.image, self.radius, self.radius, self.radius-1, self.color)
        #pygame.gfxdraw.filled_circle(self.image, self.radius, self.radius, self.radius-1, self.color)

        self.game.screen.blit(self.sprite, (self.pos))

    def collideWithEnviroment(self, dir):

        if dir == 'x':                  #Kollision med väggar
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:                                          #Höger vägg
                    self.pos.x = hits[0].rect.left - self.rect.width /2
                if self.vel.x < 0:                                          #Vänster vägg
                    self.pos.x = hits[0].rect.right + self.rect.width /2

                self.vel.x *= -0.90 # 10% av hastigheten försvinner vid studs

                                        #Kollision med marken
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.grounds, False)
            if hits: 
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height / 2        #Sätt bollens position precis ovanför marken

                    if abs(self.vel.y) < 1.5:                                   #Om bollens hastighet är tillräckligt
                                                                                #liten vid studs, sätt den till 0.
                        self.onGround = True
                        self.vel.y = 0
                    else:                                                       
                        self.onGround = False
                        self.vel.y *= -0.90                                     # 10% av hastigheten försvinner vid studs
                    
            
    def distanceTo(self, pos2, pos1):
        return math.sqrt((pos2.x - pos1.x)**2 + (pos2.y - pos1.y)**2)
    
    def collideWithBalls(self, balls):
        for ball in balls:
            if ball != self:
                distanceNextFrame = self.distanceTo(self.pos + self.vel, ball.pos + ball.vel);	
                if (distanceNextFrame - self.radius - ball.radius < 0):
                    self.onGround = False
                    ball.onGround = False

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
