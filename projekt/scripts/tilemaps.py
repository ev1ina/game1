import pygame
import csv
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

class TileMap:
    def __init__(self, filename):
        self.tile_size = TILE_SIZE
        self.start_x, self.start_y = 0, 0
        self.tiles = self.load_tiles(filename)
        self.map_surface = pygame.Surface((self.map_w, self.map_h))
        self.map_surface.set_colorkey(BLACK)
        self.load_map()

    def draw_map(self, screen):
        screen.blit(self.map_surface, (0, 0))

    def load_map(self):
        for tile in self.tiles:
            tile.draw(self.map_surface)

    def read_csv(self, filename):
        map_data = []
        with open(filename, 'test3.csv') as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                map_data.append(list(row))
        return map_data

    def load_tiles(self, filename):
        tiles = []
        map_data = self.read_csv(filename)
        x, y = 0, 0
        for row in map_data:
            x = 0
            for tile in row:
                if tile == '1493' or tile == '1494':
                    tiles.append(Tile(pygame.image.load('assets/tiles/Tiles/t_grpond.png').convert_alpha(), x * self.tile_size, y * self.tile_size))
                elif tile == '968' or tile == '969':
                    tiles.append(Tile(pygame.image.load('assets/tiles/Tiles/t_grpond.png').convert_alpha(), x * self.tile_size, y * self.tile_size))
                x += 1
            y += 1

        self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
        return tiles