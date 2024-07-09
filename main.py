import pygame
import sys
import random
import math

#Apply changes to the screen

def apply_crt_effect(surface):
    width, height = surface.get_size()
    for y in range(height):
        for x in range(width):
            color = surface.get_at((x, y))
            # Add scanlines effect
            if y % 2 == 0:
                color = (color[0] // 2, color[1] // 2, color[2] // 2)
            # Add RGB offset effect
            if random.random() > 0.99:
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            

# Initialise Pygame
pygame.init()

# Get display size
screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h

# Setup full screen display
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)

# Load and scale image for display

