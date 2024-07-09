import pygame
import sys

pygame.init()

# Get Display Size
screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h

# Setup full screen display
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)