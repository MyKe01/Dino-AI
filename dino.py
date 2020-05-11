from __future__ import print_function
from dask import visualize
import pygame
import neat
import time
import os
import random
import math


pygame.font.init()

GEN = 0

WIN_WIDTH = 1200
WIN_HEIGHT = 400

DINO_IMGS = [
        pygame.image.load(os.path.join("imgs","dino1.png")), 
        pygame.image.load(os.path.join("imgs","dino2.png")),
        pygame.image.load(os.path.join("imgs","dino3.png")),
        pygame.image.load(os.path.join("imgs","startdino.png")),
        pygame.image.load(os.path.join("imgs","downdino1.png")),
        pygame.image.load(os.path.join("imgs","downdino2.png"))
            ]

OBSTACLES_IMGS = [
              pygame.image.load(os.path.join("imgs","smallcactus1.png")),
              pygame.image.load(os.path.join("imgs","smallcactus2.png")),
              pygame.image.load(os.path.join("imgs","smallcactus3.png")),
              pygame.image.load(os.path.join("imgs","bigcactus1.png")),
              pygame.image.load(os.path.join("imgs","bigcactus2.png")),
              pygame.image.load(os.path.join("imgs","bigcactus3.png")),
              pygame.image.load(os.path.join("imgs","bat1.png")),
              pygame.image.load(os.path.join("imgs","bat2.png"))
              ]

BACKGROUND_IMG = pygame.image.load(os.path.join("imgs","background.png"))

HEIGHT_BATS = [296, 256, 206]

HEIGHT_SMALL_CACTUS = 306

HEIGHT_BIG_CACTUS = 280

STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Dino:
    IMGS = DINO_IMGS
    ANIMATION_TIME = 10

    def __init__ (self, x, y) :
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velY = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[3]
        self.gravity = 0.5
        self.jumping = True

    def jump (self):
        if self.jumping == True and self.y == WIN_HEIGHT-114 :
            self.velY = 15
            self.img = self.IMGS[0]
            self.jumping == False
            
    
    def move(self):
        self.y -= self.velY
        if self.y < WIN_HEIGHT-114 :
            self.velY -= self.gravity
        else:
            self.y = WIN_HEIGHT-114
            self.img = self.IMGS[1]
            self.velY = 0
            self.jumping = True

    def draw(self, win):
        self.img_count +=1
        if self.img!= self.IMGS[0]:
            if self.img_count < self.ANIMATION_TIME : 
                self.img = self.IMGS[1]
            elif self.img_count < self.ANIMATION_TIME*2 : 
                self.img = self.IMGS[2]
            elif self.img_count < self.ANIMATION_TIME*2 +1 : 
                self.img = self.IMGS[1]
                self.img_count = 0
        else:
            self.img_count = 0

        new_rect = self.img.get_rect(center=self.img.get_rect(topleft = (self.x, self.y )).center)
        win.blit(self.img, new_rect.topleft)
    
    def get_mask(self): #serve a trovare i pixel all'interno di un rettangolo/quadrato
        return pygame.mask.from_surface(self.img)

class Obstacle:
    GAP = 100*random.uniform(1, 2)
    VEL = 5
    OBS_ANIMATION_TIME = 10
    OBS_IMGS = OBSTACLES_IMGS
    
    def __init__(self, x):
        self.x = x
        self.height = 0
        self.img_index = random.randint(0,6)
        self.top = 0
        self.OB_TOP = OBSTACLES_IMGS[self.img_index]
        self.img_count = 0
        
        self.passed = False
        self.set_height()

    def set_height(self):
        if (self.img_index == 0 or self.img_index == 1 or self.img_index == 2):
            self.top = HEIGHT_SMALL_CACTUS
        elif (self.img_index == 3 or self.img_index == 4 or self.img_index == 5):
            self.top = HEIGHT_BIG_CACTUS
        elif (self.img_index == 6 or self.img_index == 7):
            height_index = random.randint(0,2)
            self.top = HEIGHT_BATS[height_index]

    def move(self):
        self.x -= self.VEL
    
    def drawobs(self, win):   
        if self.img_index == 6 :
            self.img_count+=1
            if self.img_count < self.OBS_ANIMATION_TIME : 
                self.img = self.OBS_IMGS[6]
                self.OB_TOP = self.OBS_IMGS[6]
                win.blit(self.OB_TOP, (self.x, self.top))
            elif self.img_count < self.OBS_ANIMATION_TIME*2 : 
                self.img = self.OBS_IMGS[7]
                self.OB_TOP = self.OBS_IMGS[7]
                win.blit(self.OB_TOP, (self.x, self.top))
            elif self.img_count < self.OBS_ANIMATION_TIME*2 +1 :
                self.OB_TOP = self.OBS_IMGS[7]
                self.img = self.OBS_IMGS[6]
                win.blit(self.OB_TOP, (self.x, self.top))
                self.img_count = 0
        else:
            win.blit(self.OB_TOP, (self.x, self.top))

    def collide(self, Dino):
        dino_mask = Dino.get_mask()
        top_mask = pygame.mask.from_surface(self.OB_TOP)

        top_offset = (self.x - Dino.x, self.top - round(Dino.y))

        t_point = dino_mask.overlap(top_mask, top_offset)

        if t_point: #se sono True
            return True
        
        return False

class Base:
    VEL = 5
    WIDTH = 2400
    IMG = BACKGROUND_IMG
    
    def __init__ (self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0 :
            self.x1 = self.x2 + self.WIDTH
        if self.x2 +  self.WIDTH < 0 :
            self.x2 = self.x1+ self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
        

def draw_window(win, dinos, obstacles, base, score, gen):
    for obstacle in obstacles:
        obstacle.drawobs(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(text, (WIN_WIDTH-10 - text.get_width(), 10))
    text = STAT_FONT.render("Gen: " + str(gen), 1, (0, 0, 0))
    win.blit(text, (10, 10))

    base.draw(win)
    for dino in dinos:
        dino.draw(win)
    pygame.display.update()

def main(genomes, config): #fitness function
    global GEN
    GEN +=1
    nets = []
    ge=[]
    dinos = []
    
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        dinos.append(Dino(89, WIN_HEIGHT-114))
        g.fitness = 0 
        ge.append(g)


    dino = Dino(89, WIN_HEIGHT-114)
    base = Base(352)
    obstacles = [Obstacle(1300)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    win.fill([255, 255, 255])
    clock = pygame.time.Clock()
    score = 0
    tick = 60

    run = True
    while run:
        clock.tick(tick)
        score+= 0.2
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        
        obstacle_ind = 0
        if len(dinos) > 0:
            if len(obstacles) > 1 and dinos[0].x > obstacles[0].x + obstacles[0].OB_TOP.get_width():
                obstacle_ind = 1
        else:
            run = False
            break

        for x, dino in enumerate(dinos):
            dino.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((dino.y, abs(dino.x - obstacles[obstacle_ind].x), abs(dino.y - obstacles[obstacle_ind].height)))

            if output[0] > 0.5:
                dino.jump()

        win.fill([255, 255, 255])

        add_obstacle = False
        rem = []
        for obstacle in obstacles:
            for x, dino in enumerate(dinos) :
                if obstacle.collide(dino):
                    ge[x].fitness -= 1
                    dinos.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not obstacle.passed and obstacle.x < dino.x:
                    obstacle.passed = True
                    add_obstacle = True

            if obstacle.x + obstacle.OB_TOP.get_width() < 0:
                rem.append(obstacle)

            obstacle.move()

        if add_obstacle :
            score +=100
            for g in ge:
                g.fitness += 5
            obstacles.append(Obstacle(1300))
        
            
           

        for r in rem:
            obstacles.remove(r)
        
        base.move()
        draw_window(win, dinos, obstacles, base, math.floor(score), GEN)



def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    
    p = neat.Population(config) #population

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50) #quante volte viene eseguita la funzione
    print('\nBest genome:\n{!s}'.format(winner))
    visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)