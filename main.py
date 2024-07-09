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

# Setup full screen display with alpha transparency
screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
pygame.display.set_caption('CRT Monitor Effect')

# Enable alpha blending
screen.set_alpha(128)

# Load and scale image for display
image = pygame.image.load('image.jpg').convert() # Image still to be created
image = pygame.transform.scale(image, (screen_width, screen_height))

# Set up clock for controlling the frame rate
clock = pygame.time.Clock()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                running = False

    # Clear the screen with transparent black
    screen.fill((0,0,0,0))

    #Create a copy of the image to apply the CRT effect
    crt_image = image.copy()
    apply_crt_effect(crt_image)

    # Draw the image with effect
    screen.blit(crt_image, (0, 0))

    pygame.display.flip()

    #Cap the frame rate at 60 FPS
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()