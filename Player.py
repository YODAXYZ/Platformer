import os
import random

import pygame

import Settings

PLAYER_RECT_WIDTH = 6
PLAYER_RECT_HEIGHT = 13


class Player:
    def __init__(self, game, x=Settings.SPAWN_X, y=Settings.SPAWN_Y, jump_sound_path="sounds/jump.wav", grass_sound_pathes=["sounds/grass_0.wav", "sounds/grass_1.wav"]):

        self.__rect = pygame.Rect(x, y, PLAYER_RECT_WIDTH, PLAYER_RECT_HEIGHT)

        loaded_sounds = self.__load_sounds(jump_sound_path, grass_sound_pathes)

        self.__jump_sound = loaded_sounds[0]
        self.__grass_sounds = loaded_sounds[1]

        self.__moving_right = False
        self.__moving_left = False

        self.__vertical_momentum = 0

        self.__air_timer = 0

        self.__grass_sound_timer = 0

        self.__animation_frames = {}

        self.__animation_database = {}

        self.__animation_database['run'] = self.__load_animation('player_animations/run', [4, 4, 4, 4])
        self.__animation_database['idle'] = self.__load_animation('player_animations/idle', [7, 7, 40])

        self.__player_action = 'idle'
        self.__player_frame = 0
        self.__player_flip = False

        self.__game = game

    def get_player_rect(self):
        return self.__rect

    def __change_action(self, action_var, frame, new_value):
        if action_var != new_value:
            action_var = new_value
            frame = 0
        return action_var, frame

    def __move(self, rect, movement, tiles, spikes):
        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}

        self.__collide_spikes(rect, spikes)

        self.__collide_flag(rect, end_flag_zone=self.__game.get_end_flag_zone())

        rect.x += movement[0]
        hit_list = self.__collision_test(rect, tiles)

        for tile in hit_list:
            # restriction on movement in right and take value from mirror object edge
            if movement[0] > 0:
                rect.right = tile.left
                collision_types['right'] = True
            elif movement[0] < 0:
                rect.left = tile.right
                collision_types['left'] = True

        rect.y += movement[1]
        hit_list = self.__collision_test(rect, tiles)

        for tile in hit_list:
            if movement[1] > 0:
                rect.bottom = tile.top
                collision_types['bottom'] = True
            elif movement[1] < 0:
                rect.top = tile.bottom
                collision_types['top'] = True
        return rect, collision_types

    def __move_to_spawn(self, rect):
        rect.x = Settings.SPAWN_X
        rect.y = Settings.SPAWN_Y

    def __collision_test(self, rect, tiles):  # use for collect object which colliderect by our person
        hit_list = []
        for tile in tiles:
            if rect.colliderect(tile):  # touch person with object by area 3-4
                hit_list.append(tile)
        return hit_list

    def __collide_flag(self, rect, end_flag_zone):
        for flag_zone_item in end_flag_zone:
            if rect.colliderect(flag_zone_item):
                self.__move_to_spawn(rect)
                self.__game.create_win_menu()

    def __collide_spikes(self, rect, spikes):
        for spike in spikes:
            if rect.colliderect(spike):
                self.__move_to_spawn(rect)

    def __load_animation(self, path, frame_durations):
        animation_name = path.split('/')[-1]
        animation_frame_data = []
        n = 0
        for frame in frame_durations:
            animation_frame_id = animation_name + '_' + str(n)
            img_loc = path + '/' + animation_frame_id + '.png'
            # player_animations/idle/idle_0.png
            animation_image = pygame.image.load(os.path.join(Settings.CURR_PATH, img_loc)).convert()
            animation_image.set_colorkey((255, 255, 255))
            self.__animation_frames[animation_frame_id] = animation_image.copy()
            for i in range(frame):
                animation_frame_data.append(animation_frame_id)
            n += 1
        return animation_frame_data

    def __load_sounds(self, jump_sound_path, grass_sound_pathes):
        jump_sound = pygame.mixer.Sound(os.path.join(Settings.CURR_PATH, jump_sound_path))
        grass_sounds = [
            pygame.mixer.Sound(os.path.join(Settings.CURR_PATH, grass_sound_pathes[0])),
            pygame.mixer.Sound(os.path.join(Settings.CURR_PATH, grass_sound_pathes[1]))
        ]
        grass_sounds[0].set_volume(0.1)
        grass_sounds[1].set_volume(0.1)

        return (jump_sound, grass_sounds)

    def move_right(self):
        self.__moving_right = True

    def move_left(self):
        self.__moving_left = True

    def stop_right(self):
        self.__moving_right = False

    def stop_left(self):
        self.__moving_left = False

    def jump(self):
        if self.__air_timer < 6:
            self.__jump_sound.play()
            self.__vertical_momentum = -5

    def redraw(self):
        #  place with our person
        player_movement = [0, 0]

        player_flip = False

        #  move x
        if self.__moving_right:
            player_movement[0] += 2
        if self.__moving_left:
            player_movement[0] -= 2

        #  move y
        player_movement[1] += self.__vertical_momentum
        self.__vertical_momentum += 0.25
        if self.__vertical_momentum > 3:
            self.__vertical_momentum = 3

        # This need to change animation when person run
        if player_movement[0] == 0:
            self.__player_action, self.__player_frame = self.__change_action(self.__player_action, self.__player_frame, 'idle')
        if player_movement[0] > 0:
            player_flip = False
            self.__player_action, self.__player_frame = self.__change_action(self.__player_action, self.__player_frame, 'run')
        if player_movement[0] < 0:
            player_flip = True
            self.__player_action, self.__player_frame = self.__change_action(self.__player_action, self.__player_frame, 'run')

        self.__rect, collisions = self.__move(self.__rect, player_movement, self.__game.get_tile_rects(), self.__game.get_spikes())

        if collisions['bottom']:
            self.__air_timer = 0
            self.__vertical_momentum = 0
            self.__grass_sound_timer = 0
            if player_movement[0] != 0:  # play_grass_sound when you moved
                if self.__grass_sound_timer == 0:
                    self.__grass_sound_timer = 30
                    random.choice(self.__grass_sounds).play()
        else:
            self.__air_timer += 1  # jump timer

        self.__player_frame += 1
        if self.__player_frame >= len(self.__animation_database[self.__player_action]):  # this need to restart animation of our person
            self.__player_frame = 0

        player_img_id = self.__animation_database[self.__player_action][self.__player_frame]
        player_img = self.__animation_frames[player_img_id]  # animation when person stand on
        scroll = self.__game.get_scroll()
        self.__game.get_display().blit(pygame.transform.flip(player_img, player_flip, False), (self.__rect.x - scroll[0], self.__rect.y - scroll[1]))  # object rendering .flip need for change side of run when render