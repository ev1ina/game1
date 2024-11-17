import pygame
from settings import *
import os

class Enemy02(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.in_air = True
        self.vel_y = 0
        self.direction = 1
        self.speed = speed
        self.attack_speed = speed
        self.alive = True
        self.health = 100
        self.is_hit = False
        self.action = 0  # 0 - Idle, 1 - Run, 2 - Attack, 3 - Hit, 4 - Death
        self.frame_index = 0
        self.flip = False
        self.animation_list = []
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        self.idling = False
        self.idle_counter = 0
        self.vision = pygame.Rect(0, 0, 70, 20)

        # Load animations
        animation_types = ['Idle', 'Run', 'Attack', 'Hit', 'Death']
        for animation in animation_types:
            temp_list = []
            folder_path = f'assets/sprites/{self.char_type}/{animation}'
            if os.path.exists(folder_path):
                num_of_frames = len(os.listdir(folder_path))
                for i in range(num_of_frames):
                    img = pygame.image.load(f'{folder_path}/{i+1}.png').convert_alpha()
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.collision_rect = pygame.Rect(
            self.rect.x + 10, self.rect.y + 10,
            self.rect.width - 20, self.rect.height - 20
        )

    def update(self):
        self.update_animation()
        self.check_alive()
        self.collision_rect.topleft = (self.rect.x + 10, self.rect.y + 10)

    def move(self):
        dx = 0
        dy = 0

        if self.in_air:
            self.vel_y += GRAVITY
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

        if self.rect.bottom + dy > 500:
            dy = 500 - self.rect.bottom
            self.in_air = False
        else:
            self.in_air = True

        if self.direction == 1:  # Moving right
            dx = self.speed
            self.flip = False
        elif self.direction == -1:  # Moving left
            dx = -self.speed
            self.flip = True

        self.move_counter += 1
        if self.move_counter > TILE_SIZE * 3:
            self.direction *= -1
            self.move_counter = 0

        self.rect.x += dx
        self.rect.y += dy

    def ai(self, player):
        if self.alive and player.alive:
            if not self.idling and self.vision.colliderect(player.collision_rect):
                self.update_action(2)  # Attack
                self.speed = self.attack_speed
                if player.rect.centerx < self.rect.centerx:
                    self.direction = -1
                elif player.rect.centerx > self.rect.centerx:
                    self.direction = 1
            else:
                self.move()

            self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 4:  # Death animation ends
                self.kill()
            else:
                self.frame_index = 0

        self.image = self.animation_list[self.action][self.frame_index]

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(4)  # Death animation

    def take_damage(self, damage):
        if self.alive:
            self.health -= damage
            self.update_action(3)  # Hit animation
            if self.health <= 0:
                self.alive = False
                self.update_action(4)  # Death animation

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        pygame.draw.rect(screen, RED, self.collision_rect, 1)