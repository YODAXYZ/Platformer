import pygame, sys

clock = pygame.time.Clock() # timer whhich need for fps

from pygame.locals import *
pygame.init() # initiates pygame

pygame.display.set_caption('Pygame Platformer')  # name of the game

WINDOW_SIZE = (1200, 800) # size of screen

screen = pygame.display.set_mode(WINDOW_SIZE) # initiate the window

display = pygame.Surface((WINDOW_SIZE[0]/4, WINDOW_SIZE[1]/4)) # used as the surface for rendering, which is scaled

moving_right = False  # change when we keydown
moving_left = False  # change when we keydown

vertical_momentum = 0  # y moving increase when we jump
air_timer = 0 # use for

game_map = [['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','1','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','1','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','2','2','2','2','2','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','1','0','0','0','0','0','0','0','0','0','0','0'],
            ['2','2','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','2','2'],
            ['1','1','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1']]  # our map 0 air, 1 ground, 2 grass with ground

# load image in pygame
grass_img = pygame.image.load('grass.png')
dirt_img = pygame.image.load('dirt.png')

player_img = pygame.image.load('player.png')
player_img.set_colorkey((255,255, 255))  # circuit of image

player_rect = pygame.Rect(100,100,5,13) # 1-2 width-height, 3-4 area of object


def collision_test(rect, tiles):  # use for collect object which colliderect by our person
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile): # touch person with object by area 3-4
            hit_list.append(tile)
    return hit_list


def move(rect, movement, tiles):  # rect in our case this is the peson, movement this his move, title it's list of map object
    """This func for oppotunity to move (this significant that when we move we don't have hurdle )"""
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False} # type of touch element

    rect.x += movement[0] # player_movement
    hit_list = collision_test(rect, tiles) # list of our tile(object)

    for tile in hit_list:
        # restriction on movement in right and take value from mirror object edge
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True

    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)

    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types


while True: # game loop
    display.fill((146,244,255))  # clear screen by filling it with blue all environment will be here

    tile_rects = []
    y = 0
    for layer in game_map:
        x = 0
        for tile in layer:
            if tile == '1':
                display.blit(dirt_img, (x*16, y*16))  # 16 this width and height our png
                tile_rects.append(pygame.Rect(x * 16, y * 16, 16, 16))
            if tile == '2':
                display.blit(grass_img, (x*16, y*16))
                tile_rects.append(pygame.Rect(x*16, y*16, 16, 16))
            # if tile != '0':
            #     # tile_rects.append(pygame.Rect(x*16, y*16, 16, 16))
            #     pass
            x += 1
        y += 1
    #  place with our person
    player_movement = [0, 0]

    #  move x
    if moving_right:
        player_movement[0] += 2  #

    if moving_left:
        player_movement[0] -= 2

    #  move y
    player_movement[1] += vertical_momentum
    vertical_momentum += 0.25
    if vertical_momentum > 3:
        vertical_momentum = 3

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom']:
        air_timer = 0
        vertical_momentum = 0
    else:
        air_timer += 1  # jump timer

    display.blit(player_img, (player_rect.x, player_rect.y))  # object rendering

    for event in pygame.event.get():  # event loop
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:
                    vertical_momentum = -5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
        
    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))  # rendering game session
    pygame.display.update()  # update display
    clock.tick(60)  # maintain 60fps
