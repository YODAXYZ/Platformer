import pygame, sys, random
from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 2, 512)  # this for predict before sound some action
pygame.init() # initiates pygame

clock = pygame.time.Clock()  # timer which need for fps

pygame.display.set_caption('Pygame Platformer')  # name of the game

WINDOW_SIZE = (1200, 800) # size of screen

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32) # initiate the window

width_for_person_center, height_for_person_center = 152, 106  # value for center camera from our window_size

display = pygame.Surface((300, 200)) # used as the surface for rendering, which is scaled

moving_right = False  # change when we keydown
moving_left = False  # change when we keydown

vertical_momentum = 0  # y moving increase when we jump
air_timer = 0 # use for

grass_sound_timer = 0

true_scroll = [0, 0]  # scroll for camera


def load_map(path):
    """This func for load map from txt to matrix"""
    with open(path + ".txt", 'r') as f:
        data = f.read()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))

    return game_map


global animation_frames
animation_frames = {}

def load_animation(path,frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        # player_animations/idle/idle_0.png
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((255,255,255))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data


def change_action(action_var, frame, new_value):
    """Changing animation"""
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


animation_database = {}

animation_database['run'] = load_animation('player_animations/run', [7, 7])
animation_database['idle'] = load_animation('player_animations/idle', [7, 7, 40])

player_action = 'idle'
player_frame = 0
player_flip = False


game_map = load_map("map")  # our map 0 air, 1 ground, 2 grass with ground

# load image in pygame
grass_img = pygame.image.load('grass.png')
dirt_img = pygame.image.load('dirt.png')


jump_sound = pygame.mixer.Sound('jump.wav')  # sound to jump
grass_sounds = [pygame.mixer.Sound('grass_0.wav'), pygame.mixer.Sound('grass_1.wav')]
grass_sounds[0].set_volume(0.1)
grass_sounds[1].set_volume(0.1)
# player_img = pygame.image.load('player.png')
# player_img.set_colorkey((255, 255, 255))  # circuit of image

pygame.mixer.music.load('music.wav')  # load music to game
pygame.mixer.music.play(-1)  # count music play -1 repeat

player_rect = pygame.Rect(100, 100, 5, 13) # 1-2 width-height, 3-4 area of object

background_objects = [[0.25, [120,10,70,400]], [0.25, [280,30,40,400]], [0.5, [30,40,40,400]], [0.5, [130,90,100,400]], [0.5, [300,80,120,400]]]  # object in background

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

    if grass_sound_timer > 0:
        grass_sound_timer -= 10

    true_scroll[0] += (player_rect.x - true_scroll[0] - width_for_person_center) / 20  # / 20 this effect of camera move
    true_scroll[1] += (player_rect.y - true_scroll[1] - height_for_person_center) / 20

    scroll = [int(x) for x in true_scroll]

    pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 80))  # background
    for background_object in background_objects:  # some background object
        obj_rect = pygame.Rect(background_object[1][0] - scroll[0] * background_object[0],
                               background_object[1][1] - scroll[1] * background_object[0], background_object[1][2],
                               background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display, (14, 222, 150), obj_rect)
        else:
            pygame.draw.rect(display, (9, 91, 85), obj_rect)

    tile_rects = []
    y = 0
    for layer in game_map:
        x = 0
        for tile in layer:
            if tile == '1':
                display.blit(dirt_img, (x*16 - scroll[0], y*16 - scroll[1]))  # 16 this width and height our png
                tile_rects.append(pygame.Rect(x * 16, y * 16, 16, 16))
            if tile == '2':
                display.blit(grass_img, (x*16 - scroll[0], y*16 - scroll[1]))
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

    # This need to change animation when person run
    if player_movement[0] == 0:
        player_action, player_frame = change_action(player_action, player_frame, 'idle')
    if player_movement[0] > 0:
        player_flip = False
        player_action, player_frame = change_action(player_action, player_frame, 'run')
    if player_movement[0] < 0:
        player_flip = True
        player_action, player_frame = change_action(player_action, player_frame, 'run')

    player_rect, collisions = move(player_rect, player_movement, tile_rects)

    if collisions['bottom']:
        air_timer = 0
        vertical_momentum = 0
        if player_movement[0] != 0:  # play_grass_sound when you moved
            if grass_sound_timer == 0:
                grass_sound_timer = 30
                random.choice(grass_sounds).play()
    else:
        air_timer += 1  # jump timer

    player_frame += 1
    if player_frame >= len(animation_database[player_action]):  # this need to restart animation of our person
        player_frame = 0

    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]  # animation when person stand on
    display.blit(pygame.transform.flip(player_img, player_flip, False), (player_rect.x - scroll[0], player_rect.y - scroll[1]))  # object rendering .flip need for change side of run when render

    for event in pygame.event.get():  # event loop
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_1:  # off music
                pygame.mixer.music.fadeout(1000)
            if event.key == K_2:  # on music 
                pygame.mixer.music.play(-1)
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:
                    jump_sound.play()
                    vertical_momentum = -5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
        
    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))  # rendering game session
    pygame.display.update()  # update display
    clock.tick(60)  # maintain 60fps
