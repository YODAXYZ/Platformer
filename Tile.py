import pygame

import Settings


class Tile:
    def __init__(self, x, y, number):
        self.__x = x
        self.__y = y
        self.__number = number
        self.__rect = pygame.Rect(x * Settings.TILE_SIZE, y * Settings.TILE_SIZE, Settings.TILE_SIZE, Settings.TILE_SIZE)

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_rect(self):
        return self.__rect

    def get_number(self):
        return self.__number