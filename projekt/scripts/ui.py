import pygame
from settings import *

def draw_text(text, font, text_col, x, y, screen):
    #Draws text on the screen.
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg(screen):
    #Fills the screen with the background color
    screen.fill(BG)