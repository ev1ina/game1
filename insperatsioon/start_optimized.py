import pygame
import os
import random
import csv
import button

# Algseadistused
pygame.init()

# Ekraani suurus
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Rocky')

# FPS ja kella seaded
clock = pygame.time.Clock()
FPS = 60

# Konstandid
GRAVITY = 0.75
ROWS, COLS = 16, 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 19
MAX_LEVELS = 3
SCROLL_THRESH = 200

# Mängu muutujad
level = 0
start_game = False
moving_left = moving_right = shoot = False
screen_scroll = bg_scroll = 0

# Grupid
sprite_groups = {
    "dagger": pygame.sprite.Group(),
    "enemy": pygame.sprite.Group(),
    "item_box": pygame.sprite.Group(),
    "decoration": pygame.sprite.Group(),
    "cristall": pygame.sprite.Group(),
    "exit": pygame.sprite.Group()
}

# Käsitletud tasemed käsitsemiseks
level_cache = {}

# Värvide määramine
COLORS = {
    "BG": (0, 73, 100),
    "RED": (255, 0, 0),
    "WHITE": (1, 40, 55),
    "GREEN": (0, 255, 0),
    "BLACK": (0, 0, 0)
}

# Teksti stiil
font = pygame.font.SysFont('Futura', 30)

# Globaalsete andmete ettevalmistus
img_list = []
back_list = []
item_boxes = {}

# Funktsioonid

def load_tile_images(tile_count, tile_path, tile_size):
    images = []
    for i in range(1, tile_count + 1):
        img = pygame.image.load(f"{tile_path}/{i}.png").convert_alpha()
        img = pygame.transform.scale(img, (tile_size, tile_size))
        images.append(img)
    return images

def load_image(path, scale_factor=1):
    img = pygame.image.load(path).convert_alpha()
    if scale_factor != 1:
        img = pygame.transform.scale(
            img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor))
        )
    return img

def load_level_data(level):
    if level in level_cache:
        return level_cache[level]

    data = []
    with open(f'levelid/level{level}_data.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            data.append([int(tile) for tile in row])
    level_cache[level] = data
    return data

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill(COLORS["BG"])
    width = back_list[0].get_width()
    for x in range(4):
        screen.blit(back_list[0], ((x * width) - bg_scroll * 0.5, 0))
        for i in range(1, len(back_list)):
            screen.blit(back_list[i], ((x * width) - bg_scroll * (0.5 + i * 0.1), SCREEN_HEIGHT - back_list[i].get_height() + 100))

def update_and_draw_groups(groups, screen):
    for group in groups.values():
        group.update()
        group.draw(screen)

def reset_level():
    for group in sprite_groups.values():
        group.empty()
    return [[-1] * COLS for _ in range(ROWS)]

# Laadime ressursid
dagger_img2 = load_image('rocky/Sprites/Gino Character/PNG/dagger/1.png', 1.5)
img_list = load_tile_images(TILE_TYPES, 'rocky/01. Rocky Level/tiles', TILE_SIZE)
back_list = [load_image(f'rocky/01. Rocky Level/{i}.png') for i in range(1, 9)]

item_boxes = {
    "Health": load_image('rocky/Collectible/Heart/1.png'),
    "Ammo": load_image('rocky/Collectible/Dag/1.png', 2),
    "Diamond": load_image('rocky/Collectible/Diamond/1.png')
}

# Klassid (klassid "Main_character", "World", "Enemy02" jne jäävad sarnaseks eelnevaga ja neid siia ei lisata täielikult)

class World:
    def __init__(self):
        self.obstavle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    if tile <= 5 or tile == 18:
                        self.obstavle_list.append((img, img_rect))
        return None, None, None

    def draw(self):
        for tile in self.obstavle_list:
            screen.blit(tile[0], tile[1])

# Mängu loogika
world = World()
world_data = load_level_data(level)

run = True
while run:
    clock.tick(FPS)
    if not start_game:
        # Lisa menüünuppude loogika
        pass
    else:
        draw_bg()
        world.draw()
        update_and_draw_groups(sprite_groups, screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
