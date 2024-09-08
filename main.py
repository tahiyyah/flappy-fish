import pygame
from pygame import *
import math
import random

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('flappy fish')
clock = pygame.time.Clock()

#loading images
bg = pygame.image.load('bg.png')
bg = pygame.transform.scale(bg, (600, 600))
fish1 = pygame.image.load('fish1.png')
fish1 = pygame.transform.scale(fish1, (75, 40))
fish2 = pygame.image.load('fish2.png')
fish2 = pygame.transform.scale(fish2, (75, 40))
fish3 = pygame.image.load('fish3.png')
fish3 = pygame.transform.scale(fish3, (75, 40))
fish4 = pygame.image.load('fish4.png')
fish4 = pygame.transform.scale(fish4, (75, 40))

#colours
yellow = (255, 227, 82)
orange = (255, 188, 28)
darkgreen = (101, 206, 80)

alive_animation = [fish1, fish2]
dead_animation = [fish3, fish4]

bgscroll = 0
scroll_speed = 6
bg_width = bg.get_width()
tiles = math.ceil(screen_width / bg_width)
frequency = 1500
last_pillar = pygame.time.get_ticks()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = fish1
        self.rect = self.image.get_rect()
        self.rect.x = 30
        self.rect.y = screen_height / 2
        self.dead = False
        self.index = 0
        self.jumped = False
        self.start = False
        self.end = False
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        self.score = 0
        self.velocity = 0

    def update(self):
        #gravity
        if self.start:
            self.velocity += 1
            if self.velocity > 10:
                self.velocity = 10
            if self.rect.bottom < 530: #makes fish unable to move if it falls to the sand
                self.rect.y += self.velocity
            if self.rect.top < 0: #makes fish not able to go off the screen
                self.rect.y -= self.velocity
        
        #animations
        if not self.end and self.start:
            current_time = pygame.time.get_ticks()
            animation_speed = 150 #setting how fast the animation will be
            self.index = (current_time // animation_speed) % len(alive_animation) #calculating index of current frame
            self.image = alive_animation[self.index] #updating image

            #rotation
            self.image = pygame.transform.rotate(alive_animation[self.index], -self.velocity) #argument1 = animation image, argument2 = negative to ensure rotation is in correct direction

        #collisions
        if self.rect.bottom > 530: #if collides with sand, game over
            self.end = True
            self.start = False

        if self.end:
            self.image = dead_animation[self.index]

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.x = screen_width
        self.width = 85
        self.height = random.randint(100, 350)
        self.colour = darkgreen
        self.bottom = self.height + self.width + 60 #y coordinate for bottom of pillar
        self.rect_top = Rect(self.x, 0, self.width, self.height)
        self.rect_bottom = Rect(self.x, self.bottom, self.width, (screen_height - self.bottom))
        self.passed = False #tracks if the pillar has been passed

    def update(self):
        top = pygame.draw.rect(screen, self.colour, Rect(self.x, 0, self.width, self.height))
        bottom = pygame.draw.rect(screen, self.colour, Rect(self.x, self.bottom, self.width, (screen_height - self.bottom)))

        if player.start:
            self.x -= scroll_speed #pillars scroll

            if self.x < -85:
                pillar_group.remove(self) #once completely off screen, delete

            if top.colliderect(player) or bottom.colliderect(player):
                player.end = True
                player.start = False
            
            #check if the player has passed the pillar
            if not self.passed and self.x < player.rect.x:
                player.score += 1
                self.passed = True

class Button: #creates button class
    def __init__(self, x_pos, y_pos, width, height, base_colour, hover_colour, enabled):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.base_colour = base_colour
        self.hover_colour = hover_colour
        self.enabled = enabled
        self.draw() #draws button to screen automatically

    def draw(self): #draws button to screen
        button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (self.width, self.height)) #creates rectangle that is the button

        if self.enabled: #if enabled = True
            if self.hover():   
                pygame.draw.rect(screen, self.hover_colour, button_rect, 0, 3) #changes colour when clicked
            else:
                pygame.draw.rect(screen, self.base_colour, button_rect, 0, 3)
        else:
            pygame.draw.rect(screen, self.base_colour, button_rect, 0, 3) #if enabled is false, will not change colour when clicked

    def hover(self):
        button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (self.width, self.height))
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos) and self.enabled:
            return True
        else:
            return False

    def clicked(self): #checks if button gets clicked
        mouse_pos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        button_rect = pygame.rect.Rect((self.x_pos, self.y_pos), (self.width, self.height))

        if left_click and button_rect.collidepoint(mouse_pos) and self.enabled:
            return True
        else:
            return False

def dropShadow(message, size, text_colour, shadow_colour, offset, x_pos, y_pos):
    font = pygame.font.SysFont('ArialBold', size)
    text = font.render(message, True, text_colour)
    shadow = font.render(message, True, shadow_colour)
    shadow.set_alpha(127) #lowers shadow opacity
    screen.blit(shadow, (x_pos + offset, y_pos + offset)) #shadow needs to be blit first to be behind text
    screen.blit(text, (x_pos, y_pos))
    
#sprite groups
fish_group = pygame.sprite.Group()
player = Player()
fish_group.add(player)

pillar_group = pygame.sprite.Group()
pillar = Obstacle()
pillar_group.add(pillar)

def main():
    global last_pillar
    global bgscroll
    global tiles

    while True:
        tiles += 1 #if you dont have + 1 then there's a blur in the scroll for a short time
        clock.tick(30)
        
        # draw to screen
        if not player.end: #doesn't scroll if game ends
            for i in range(0, tiles):
                screen.blit(bg, (i * bg_width + bgscroll, 0))

            if player.start: #only scrolls when player starts game
                bgscroll -= scroll_speed
                if abs(bgscroll) > bg_width: #abs gets positive value
                    bgscroll = 0

                current_time = pygame.time.get_ticks()
                if (current_time - last_pillar) > frequency:
                    pillar = Obstacle() #generates new pillar after frequency
                    pillar_group.add(pillar)
                    last_pillar = current_time

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and not player.end: #jump
                player.start = True
                if event.key == pygame.K_SPACE:
                    player.velocity = -10
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    player.velocity = -5

            if event.type == pygame.QUIT:
                pygame.quit()

        pillar_group.update()
        fish_group.update()
        fish_group.draw(screen)

        #displaying score
        dropShadow('score: '+str(player.score), 30, 'white', 'black', 2, 10, 10)

        pygame.display.update()

main()
