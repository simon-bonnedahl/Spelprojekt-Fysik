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
            if self.vel.magnitude() > 0.01: 
                frictionForce = -self.vel.normalize() * normalForce * FRICTION_CONSTANT                    

        
        if self.vel.magnitude() > 0.01:                        #Om bollen är i rörelse, räkna ut luftmotståndet
            dragForce = -self.vel.normalize() * (DRAG_CONSTANT * AIR_DENSITY * self.area * self.vel.magnitude_squared())/2
        else:
            self.vel = vec(0, 0)

        nettoForce = gravityForce + dragForce + frictionForce

        self.acc = nettoForce/self.mass   

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

                    dist = self.distanceTo(self.pos, ball.pos);	                #Mass center till mass center(hypotenusa)
                    pg.draw.line(self.game.screen, (0, 0, 0), self.pos, ball.pos, width=2)
                    #print("drawing line")

                    print("My pos", self.pos)
                    print("Other pos", ball.pos)
                    
                    normalX = (ball.pos.x - self.pos.x) / dist                  #Skillnad i x-led delat på hypotenusa
                    normalY = (ball.pos.y - self.pos.y) / dist                  #Skillnad i y-led delat på hypotenusa

                    normal = vec(normalX, normalY)
                    tangent = vec(-normal.y, normal.x)

                    print("Tangent: ", tangent)
                    print("Normal: ", normal)

                    dotProductTan1 = self.vel.x * tangent.x + self.vel.y * tangent.y
                    dotProductTan2 = ball.vel.x * tangent.x + ball.vel.y * tangent.y

                    print("Dot product 1: ", dotProductTan1)
                    print("Dot product 2: ", dotProductTan2)

                    self.velocityMagnitudeInitial = self.vel.x * normal.x + self.vel.y * normal.y
                    ball.velocityMagnitudeInitial = ball.vel.x * normal.x + ball.vel.y * normal.y

                    print("My velocity initial: ", self.velocityMagnitudeInitial)
                    print("Other velocity initial: ", ball.velocityMagnitudeInitial)
                                #Vai                    #ma - mb                #2mb            Vbi                 ma + mb
                    self.velocityMagnitudeFinal = (self.velocityMagnitudeInitial * (self.mass - ball.mass) + 2 * ball.mass * ball.velocityMagnitudeInitial) / (self.mass + ball.mass)
                    ball.velocityMagnitudeFinal = (ball.velocityMagnitudeInitial * (ball.mass - self.mass) + 2 * self.mass * self.velocityMagnitudeInitial) / (self.mass + ball.mass)
                    
                   
                    self.vel.x = tangent.x * dotProductTan1 + normal.x * self.velocityMagnitudeFinal
                    self.vel.y = tangent.y * dotProductTan1 + normal.y * self.velocityMagnitudeFinal

                    ball.vel.x = tangent.x  * dotProductTan2 + normal.x * ball.velocityMagnitudeFinal
                    ball.vel.y = tangent.y * dotProductTan2 + normal.y * ball.velocityMagnitudeFinal
