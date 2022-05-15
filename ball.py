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
        self.vel = vec(5, -5)
        self.acc = vec(0, 0)
        self.onGround = False

        #Grafik
        self.image = pg.Surface((self.radius*2, self.radius*2), pg.SRCALPHA)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.bg = pg.image.load("bg.jpeg")
        self.bg = pg.transform.scale(self.bg, (self.radius*2, self.radius*2))
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)
        self.color = (r, g, b)
        self.color = WHITE

        self.rotationAngle = 0
        



    def update(self):  

        if self.onGround != True:
            self.acc = vec(0, GRAVITY)
        else:
            self.acc = vec(0, 0)
            #apply friction

        gravityForce = self.acc * self.mass
        if self.vel.magnitude() > 0:
            dragForce = -self.vel.normalize() * (DRAG_CONSTANT * AIR_DENSITY * self.area * self.vel.magnitude_squared())/2
        
        self.acc = (gravityForce + dragForce)/self.mass   
        
        #self.acc += self.vel * -AIR_RESISTANCE         #Förenklad luftmotstånd

        self.vel += self.acc * self.game.dt             #Delta time
        self.pos += self.vel    


        
        self.rect.centerx = self.pos.x
        self.collideWithEnviroment('x')
        self.rect.centery = self.pos.y
        self.collideWithEnviroment('y')

        self.collideWithBalls(self.game.balls)
        
       

        
        #pygame.gfxdraw.aacircle renderas bättre än pygame.draw.circle
        pygame.gfxdraw.aacircle(self.image, self.radius, self.radius, self.radius-1, self.color)
        pygame.gfxdraw.filled_circle(self.image, self.radius, self.radius, self.radius-1, self.color)

        #pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        #self.image.blit(self.bg, (0, 0), None, pg.BLEND_RGBA_MIN)


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
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom + self.rect.height / 2
                if abs(self.vel.y) < 1.5:
                       
                    self.onGround = True
                    self.vel.y = 0
                else:
                    self.onGround = False
                    self.vel.y *= -0.95  #-0.95 om 5% av energin försvinner vid studs
                    
            
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


                """public static void intersect(Ball a, Ball b) {
                //ref http://gamedev.stackexchange.com/questions/20516/ball-collisions-sticking-together
                double xDist, yDist;
                xDist = a.x - b.x;
                yDist = a.y - b.y;
                double distSquared = xDist * xDist + yDist * yDist;
                // Check the squared distances instead of the the distances, same
                // result, but avoids a square root.
                if (distSquared <= (a.radius + b.radius) * (a.radius + b.radius)) {
                    double speedXocity = b.speedX - a.speedX;
                    double speedYocity = b.speedY - a.speedY;
                    double dotProduct = xDist * speedXocity + yDist * speedYocity;
                    // Neat vector maths, used for checking if the objects moves towards
                    // one another.
                    if (dotProduct > 0) {
                        double collisionScale = dotProduct / distSquared;
                        double xCollision = xDist * collisionScale;
                        double yCollision = yDist * collisionScale;
                        // The Collision vector is the speed difference projected on the
                        // Dist vector,
                        // thus it is the component of the speed difference needed for
                        // the collision.
                        double combinedMass = a.getMass() + b.getMass();
                        double collisionWeightA = 2 * b.getMass() / combinedMass;
                        double collisionWeightB = 2 * a.getMass() / combinedMass;
                        a.speedX += (collisionWeightA * xCollision);
                        a.speedY += (collisionWeightA * yCollision);
                        b.speedX -= (collisionWeightB * xCollision);
                        b.speedY -= (collisionWeightB * yCollision);
                    }
                }
    }"""