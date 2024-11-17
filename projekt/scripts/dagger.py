import pygame
from settings import *

class Dagger(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = pygame.image.load('assets/sprites/dagger.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * 2), int(self.image.get_height() * 2)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        """Update dagger position and check if it goes off-screen."""
        self.rect.x += (self.direction * self.speed)
        # Remove the dagger if it goes off-screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
