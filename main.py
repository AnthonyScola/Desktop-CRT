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
            # Simulate  the curvature of the CRT monitor
                offset_x = int(10 * math.sin(2 * math.pi * y / height))
                new_x = min(max(x + offset_x, 0), width - 1)
                surface.set_at((new_x, y), color)

# Initialise Pygame
pygame.init()

# Get display size
screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h

# Setup full screen display
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)

# Load and scale image for display

