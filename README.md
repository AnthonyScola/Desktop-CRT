# CRT Filter Effect

This project creates a CRT monitor and VHS recording effect overlay for your screen using Python and Pygame. The overlay adds scanlines, noise, and curvature to simulate the retro display effects.

## Features

- Full-screen overlay with CRT and VHS effects.
- Adjustable transparency to allow interaction with other windows.
- Close the application with `Shift + Esc`.

## Requirements

- Python 3.x
- Pygame

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Terafora/CRT-Filter.git
   cd CRT-Filter
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install pygame
   ```

4. **Add Your Image**
   - Place your image file in the project directory.
   - Update the image filename in the script if needed.

## Usage

1. **Run the Script**
   ```bash
   python main.py
   ```

2. **Interact with the Overlay**
   - The overlay will cover the entire screen.
   - To close the application, press `Shift + Esc`.

## WIP Items

- Visual filter image to overlay on the screen.

## Code Explanation

### Main Loop

- **Initialization**:
  ```python
  import pygame
  import sys
  import random
  import math
  ```

- **Setting Up Pygame**:
  ```python
  pygame.init()
  screen_info = pygame.display.Info()
  screen_width, screen_height = screen_info.current_w, screen_info.current_h
  screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
  pygame.display.set_caption("CRT Filter Effect")
  screen.set_alpha(128)
  ```

- **Loading and Scaling the Image**:
  ```python
  image = pygame.image.load('your_image.png').convert()
  image = pygame.transform.scale(image, (screen_width, screen_height))
  ```

- **Main Loop**:
  ```python
  running = True
  clock = pygame.time.Clock()
  while running:
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              running = False
          elif event.type == pygame.KEYDOWN:
              if event.key == pygame.K_ESCAPE and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                  running = False
      screen.fill((0, 0, 0, 0))
      crt_image = image.copy()
      apply_crt_effect(crt_image)
      screen.blit(crt_image, (0, 0))
      pygame.display.flip()
      clock.tick(60)
  pygame.quit()
  sys.exit()
  ```

- **CRT Effect Function**:
  ```python
  def apply_crt_effect(surface):
      width, height = surface.get_size()
      for y in range(height):
          for x in range(width):
              color = surface.get_at((x, y))
              if y % 2 == 0:
                  color = (color.r // 2, color.g // 2, color.b // 2)
              if random.random() > 0.99:
                  color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
              offset_x = int(10 * math.sin(2 * math.pi * y / height))
              new_x = min(max(x + offset_x, 0), width - 1)
              surface.set_at((new_x, y), color)
  ```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any changes.

## Contact

If you have any questions, feedback, or job opportunities, feel free to get in touch with Charlotte:

- **Email**: [charlie.stone649@gmail.com](mailto:charlie.stone649@gmail.com)
- **GitHub**: [Terafora](https://github.com/Terafora)
- **LinkedIn**: [Charlotte Stone](https://www.linkedin.com/in/charlotte-stone-web/)
