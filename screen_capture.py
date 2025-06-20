"""
Screen Capture Module

Handles screen capture functionality with overlay window management.
"""

import mss
import pygame
import time
from PIL import Image
from typing import Dict, Optional
from window_manager import WindowManager


class ScreenCapture:
    """Manages screen capture with overlay window coordination."""
    
    def __init__(self, window_manager: WindowManager):
        self.sct = mss.mss()
        self.window_manager = window_manager
    
    def capture_screen(self, monitor_index: int) -> Optional[pygame.Surface]:
        """
        Capture screen with overlay window hiding to prevent feedback.
        
        Returns pygame surface of captured screen or None if capture fails.
        """
        try:
            # Hide overlay window before capture
            window_hidden = self.window_manager.hide_window()
            
            # Capture screen
            monitor_info = self.sct.monitors[monitor_index + 1]
            screen_shot = self.sct.grab(monitor_info)
            
            # Restore overlay window after capture
            if window_hidden:
                self.window_manager.restore_window()
            
            # Convert to pygame surface
            return self._convert_to_pygame_surface(screen_shot)
            
        except Exception as e:
            print(f"Error during screen capture: {e}")
            # Ensure window is restored even if there's an error
            self.window_manager.ensure_window_restored()
            return None
    
    def _convert_to_pygame_surface(self, screenshot) -> pygame.Surface:
        """Convert MSS screenshot to pygame surface."""
        # Convert to PIL Image
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        
        # Convert to pygame surface
        img_str = img.tobytes()
        screen_surface = pygame.image.fromstring(img_str, img.size, img.mode)
        return screen_surface.convert()  # Convert to display format
    
    def close(self) -> None:
        """Clean up resources."""
        self.sct.close()
