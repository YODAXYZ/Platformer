import os
import sys

import pygame
import pygame_menu

import Settings
from Player import Player
from pygame.locals import *


class Game:

    def __init__(self, map_path="maps/map", music_path="sounds/music.wav"):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()

        self.__display = pygame.Surface(Settings.DISPLAY_SIZE)

        self.__game_map = self.__load_map(map_path)

        self.__tile_rects = []
        self.__tiles_imgs = self.__load_tiles_imgs()
        self.__spikes = []

        self.__music_path = music_path

        self.__grass_sound_timer = 0

        self.__true_scroll = [0, 0]
        self.__scroll = []

        self.__clock = pygame.time.Clock()

        self.__screen = pygame.display.set_mode(Settings.WINDOW_SIZE, 0, 32)

        self.__player = Player(self)

        flag_x, flag_y = Settings.END_FLAG_POINT
        self.__end_flag_zone = [
            pygame.Rect(flag_x * Settings.TILE_SIZE, (flag_y + 1) * Settings.TILE_SIZE, Settings.TILE_SIZE, Settings.TILE_SIZE),
            pygame.Rect(flag_x * Settings.TILE_SIZE, (flag_y - 1) * Settings.TILE_SIZE, Settings.TILE_SIZE, Settings.TILE_SIZE),
            pygame.Rect((flag_x - 1) * Settings.TILE_SIZE, flag_y * Settings.TILE_SIZE, Settings.TILE_SIZE, Settings.TILE_SIZE),
            pygame.Rect((flag_x + 1) * Settings.TILE_SIZE, flag_y * Settings.TILE_SIZE, Settings.TILE_SIZE, Settings.TILE_SIZE),
        ]

    def get_tile_rects(self):
        return self.__tile_rects

    def get_spikes(self):
        return self.__spikes

    def get_end_flag_zone(self):
        return self.__end_flag_zone

    def get_display(self):
        return self.__display

    def get_scroll(self):
        return self.__scroll

    def create_win_menu(self):
        menu = pygame_menu.Menu(Settings.WINDOW_SIZE[1], Settings.WINDOW_SIZE[0], 'You won', theme=pygame_menu.themes.THEME_DARK)

        menu.add_button('Play again', self.__start_game)
        menu.add_button('Quit', pygame_menu.events.EXIT)
        menu.mainloop(self.__screen)

    def __create_start_menu(self):
        menu = pygame_menu.Menu(Settings.WINDOW_SIZE[1], Settings.WINDOW_SIZE[0], 'Welcome',theme=pygame_menu.themes.THEME_DARK)

        menu.add_button('Play', self.__start_game)
        menu.add_button('Quit', pygame_menu.events.EXIT)
        menu.mainloop(self.__screen)

    def __load_map(self, path):
        with open(os.path.join(Settings.CURR_PATH, path + ".txt"), 'r') as f:
            data = f.read()
        data = data.split('\n')
        game_map = []
        for row in data:
            tiles = row.split(' ')
            game_map.append(list(tiles))

        return game_map

    def __load_tiles_imgs(self):
        tiles = dict()
        for i in range(0, 29):
            formatted = '%02d' % i
            tiles[formatted] = pygame.image.load(os.path.join(Settings.CURR_PATH, 'tiles/%s.png' % formatted))

        return tiles

    def start(self):
        pygame.init()
        pygame.display.set_caption(Settings.GAME_NAME_LABEL)

        #Setting up the music
        pygame.mixer.music.load(os.path.join(Settings.CURR_PATH, self.__music_path))
        pygame.mixer.music.play(-1)

        self.__init_map()

        self.__create_start_menu()

    def __draw_background(self):
        pygame.draw.rect(self.__display, Settings.BACKGROUND_COLOR, pygame.Rect(0, 120, 300, 80))

        for background_object in Settings.BACKGROUND_OBJECTS_DATA:  # some background object
            obj_rect = pygame.Rect(background_object[1][0] - self.__scroll[0] * background_object[0],
                                   background_object[1][1] - self.__scroll[1] * background_object[0], background_object[1][2],
                                   background_object[1][3])
            if background_object[0] == 0.5:
                pygame.draw.rect(self.__display, (14, 222, 150), obj_rect)
            else:
                pygame.draw.rect(self.__display, (9, 91, 85), obj_rect)

    def __count_scroll(self):
        self.__true_scroll[0] += (self.__player.get_player_rect().x - self.__true_scroll[
            0] - Settings.WIDTH_FOR_PERSON_CENTER) / 20  # / 20 this effect of camera move
        self.__true_scroll[1] += (self.__player.get_player_rect().y - self.__true_scroll[
            1] - Settings.HEIGHT_FOR_PERSON_CENTER) / 20

        self.__scroll = [int(x) for x in self.__true_scroll]

    def __init_map(self):
        y = 0
        for layer in self.__game_map:
            x = 0
            for tile in layer:
                if tile in Settings.SPIKE_NUMBERS:
                    self.__spikes.append(pygame.Rect(x * Settings.TILE_SIZE, y * Settings.TILE_SIZE, Settings.TILE_SIZE,
                                              Settings.TILE_SIZE))
                elif tile != '**':
                    self.__tile_rects.append(pygame.Rect(x * Settings.TILE_SIZE, y * Settings.TILE_SIZE, Settings.TILE_SIZE,
                                                  Settings.TILE_SIZE))
                x += 1
            y += 1

    def __redraw_map(self):
        y = 0
        for layer in self.__game_map:
            x = 0
            for tile in layer:
                if tile != '**':
                    self.__display.blit(self.__tiles_imgs[tile],(x * Settings.TILE_SIZE - self.__scroll[0], y * Settings.TILE_SIZE - self.__scroll[1]))  # 16 this width and height our png
                x += 1
            y += 1

    def __start_game(self):
        while True: # game loop
            self.__display.fill(Settings.SKY_COLOR)  # clear screen by filling it with blue all environment will be here

            if self.__grass_sound_timer > 0:
                self.__grass_sound_timer -= 10

            self.__count_scroll()

            self.__draw_background()

            self.__redraw_map()

            self.__player.redraw()

            for event in pygame.event.get():  # event loop
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        menu = pygame_menu.Menu(Settings.WINDOW_SIZE[1], Settings.WINDOW_SIZE[0], 'Pause', theme=pygame_menu.themes.THEME_DARK)

                        menu.add_button('Continue', self.__start_game)
                        menu.add_button('Quit', pygame_menu.events.EXIT)
                        menu.mainloop(self.__screen)

                    if event.key == K_1:  # off music
                        pygame.mixer.music.fadeout(1000)
                    if event.key == K_2:  # on music
                        pygame.mixer.music.play(-1)
                    if event.key == K_RIGHT:
                        self.__player.move_right()
                    if event.key == K_LEFT:
                        self.__player.move_left()
                    if event.key == K_UP:
                        self.__player.jump()
                if event.type == KEYUP:
                    if event.key == K_RIGHT:
                        self.__player.stop_right()
                    if event.key == K_LEFT:
                        self.__player.stop_left()

            self.__screen.blit(pygame.transform.scale(self.__display, Settings.WINDOW_SIZE), (0, 0))  # rendering game session
            pygame.display.update()  # update display
            self.__clock.tick(60)  # maintain 60fps
