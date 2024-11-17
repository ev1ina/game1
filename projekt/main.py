import pygame
from settings import *
from scripts.player import Main_character
from scripts.enemy import Enemy02
from scripts.tilemaps import TileMap
from scripts.items import ItemBox, HeathBar
from scripts.ui import draw_bg, draw_text
from scripts.dagger import Dagger

# Initialize Pygame
pygame.init()

diamond_box_img = pygame.image.load('rocky/Collectible/Diamond/1.png').convert_alpha()
dag1_box_img = pygame.image.load('rocky/Collectible/Dag/1.png').convert_alpha()
dag_box_img = pygame.transform.scale(dag1_box_img, (int(dag1_box_img.get_width() * 2), int(dag1_box_img.get_height() * 2)))
heart_box_img = pygame.image.load('rocky/Collectible/Heart/1.png').convert_alpha()


# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Rocky')
clock = pygame.time.Clock()

# Load the map
map = TileMap("data/SCV failid/test3.csv")

# Create groups for sprites
dagger_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()

# Initialize game objects
player = Main_character('Gino Character', 200, 200, 1.65, 5, 20)
health_bar = HeathBar(10, 10, player.health, player.health)
enemy = Enemy02('Enemy02', 300, 200, 1.65, 2)
enemy_group.add(enemy)

# Create temporary item boxes
item_box_group.add(ItemBox('Health', 100, 450))
item_box_group.add(ItemBox('Ammo', 400, 450))
item_box_group.add(ItemBox('Diamond', 600, 450))

item_boxes = {
    "Health"    : heart_box_img,
    "Ammo"      : dag_box_img,
    "Diamond"   : diamond_box_img
}



# Game loop
run = True
while run:
    clock.tick(FPS)

    draw_bg(screen)
    map.draw_map(screen)

    # Display collectibles
    draw_text('DIAMONDES:', font, WHITE, 10, 35)
    for x in range(player.diamondes):
        screen.blit(item_boxes['Diamond'], (160 + (x * 25), 37))

    # Display health
    health_bar.draw(player.health)

    # Display ammo
    draw_text('AMMO:', font, WHITE, 10, 65)
    for x in range(player.ammo):
        screen.blit(item_boxes['Ammo'], (100 + (x * 7), 67))

    # Update and draw player
    player.update()
    player.draw(screen)

    # Update and draw enemies
    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw(screen)

    # Check collisions
    for dagger in dagger_group:
        if pygame.sprite.collide_rect(dagger, enemy) and enemy.alive:
            enemy.take_damage(25)
            dagger.kill()

    # Update item boxes
    item_box_group.update()

    # Draw groups
    dagger_group.update()
    dagger_group.draw(screen)
    item_box_group.draw(screen)

    # Player actions
    if player.alive:
        if player.is_throwing:
            player.update_action(3)  # Throw attack
        elif shoot:
            player.is_throwing = True
        elif player.is_hit:
            player.update_action(5)  # Hit
        elif player.in_air:
            player.update_action(2)  # Jump
        elif moving_left or moving_right:
            player.update_action(1)  # Run
        else:
            player.update_action(0)  # Idle
        player.move(moving_left, moving_right)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()

pygame.quit()
