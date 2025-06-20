"""
CRT Filter Effects Module

Contains all the visual effects and processing logic for the CRT filter.
"""

import pygame
import numpy as np
from typing import Tuple, Optional


class CRTFilter:
    """Applies various CRT monitor effects to pygame surfaces."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # Effect parameters
        self.scanline_intensity = 0.05
        self.curvature = 0.0
        self.vignette_intensity = 0.1
        self.chromatic_aberration = 0.5
        self.performance_mode = True
        
        # Frame buffer for feedback detection
        self.prev_frame: Optional[pygame.Surface] = None
        self.frame_buffer = []
        self.buffer_size = 3
        self.capture_retry_count = 0
        self.max_retries = 5
    
    def update_parameters(self, **kwargs) -> None:
        """Update filter parameters from keyword arguments."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def add_frame_to_buffer(self, frame: pygame.Surface) -> None:
        """Add frame to buffer and maintain buffer size."""
        self.frame_buffer.append(frame)
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)
    
    def detect_feedback_loop(self, current_frame: pygame.Surface) -> bool:
        """Detect if current frame is too similar to recent frames (feedback loop)."""
        if len(self.frame_buffer) < 2:
            return False
        
        try:
            # Convert current frame to numpy array for comparison
            current_array = pygame.surfarray.array3d(current_frame)
            
            # Compare with recent frames
            for buffered_frame in self.frame_buffer[-2:]:  # Check last 2 frames
                buffered_array = pygame.surfarray.array3d(buffered_frame)
                
                # Calculate difference
                diff = np.mean(np.abs(current_array.astype(float) - buffered_array.astype(float)))
                
                # If difference is too small, we might have a feedback loop
                if diff < 5.0:  # Threshold for similarity
                    return True
                    
        except Exception:
            pass  # If comparison fails, assume no feedback
            
        return False
    
    def create_coordinate_grid(self, width: int, height: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Create coordinate grids for geometric transformations."""
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + Y**2)
        return X, Y, R
    
    def apply_scanlines(self, surface: pygame.Surface) -> None:
        """Apply horizontal scanlines to simulate CRT scan pattern."""
        height = surface.get_height()
        width = surface.get_width()
        
        for y in range(0, height, 2):
            line_surface = pygame.Surface((width, 1), pygame.SRCALPHA)
            line_surface.fill((0, 0, 0, int(255 * self.scanline_intensity)))
            surface.blit(line_surface, (0, y))
    
    def apply_chromatic_aberration(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply chromatic aberration effect (color channel separation)."""
        result = surface.copy()
        width = surface.get_width()
        
        pixels = pygame.surfarray.pixels3d(result)
        offset = max(1, int(self.chromatic_aberration * (width / self.width)))
        
        # Separate and shift color channels
        red = pixels[:, :, 0].copy()
        pixels[offset:, :, 0] = red[:-offset, :]
        
        blue = pixels[:, :, 2].copy()
        pixels[:-offset, :, 2] = blue[offset:, :]
        
        del pixels
        return result
    
    def apply_vignette(self, surface: pygame.Surface) -> None:
        """Apply vignette effect (darkening at edges)."""
        width = surface.get_width()
        height = surface.get_height()
        
        _, _, R = self.create_coordinate_grid(width, height)
        intensity = np.clip(1.0 - R * self.vignette_intensity, 0, 1)
        color_values = (intensity * 255).astype(np.uint8)
        
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)
        pixels = pygame.surfarray.pixels3d(vignette)
        pixels[:] = color_values.T[:, :, np.newaxis]
        del pixels
        
        surface.blit(vignette, (0, 0), special_flags=pygame.BLEND_MULT)
    
    def apply_curvature(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply barrel distortion to simulate curved CRT screen."""
        if self.curvature == 0:  # Skip if no curvature
            return surface.copy()
            
        width = surface.get_width()
        height = surface.get_height()
        
        # Create curved surface with same format as input
        curved = pygame.Surface((width, height), surface.get_flags())
        
        # Calculate distortion with reduced strength
        X, Y, R = self.create_coordinate_grid(width, height)
        F = 1 + R * (self.curvature * R * 0.25)  # Further reduce effect strength
        
        source_x = ((X * F + 1) * width / 2).astype(np.int32)
        source_y = ((Y * F + 1) * height / 2).astype(np.int32)
        
        source_x = np.clip(source_x, 0, width - 1)
        source_y = np.clip(source_y, 0, height - 1)
        
        # Copy pixels with proper format preservation
        pixels = pygame.surfarray.pixels3d(curved)
        source_pixels = pygame.surfarray.pixels3d(surface)
        pixels[:] = source_pixels[source_x.T, source_y.T]
        
        del pixels
        del source_pixels
        return curved
    
    def apply_effects(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply all CRT effects to the surface."""
        result = surface.copy()
        
        if self.performance_mode:
            # Process at lower resolution for better performance
            scale = 0.5
            small_size = (int(self.width * scale), int(self.height * scale))
            small_surface = pygame.transform.smoothscale(result, small_size)
            
            small_surface = self.apply_chromatic_aberration(small_surface)
            small_surface = self.apply_curvature(small_surface)
            self.apply_scanlines(small_surface)
            self.apply_vignette(small_surface)
            
            result = pygame.transform.smoothscale(small_surface, (self.width, self.height))
        else:
            # Full resolution processing
            result = self.apply_chromatic_aberration(result)
            result = self.apply_curvature(result)
            self.apply_scanlines(result)
            self.apply_vignette(result)
        
        return result
    
    def process_frame(self, surface: pygame.Surface) -> pygame.Surface:
        """
        Process a frame with feedback detection and frame buffering.
        
        Returns the processed surface, handling feedback loops appropriately.
        """
        # Check for feedback loop before processing
        if self.detect_feedback_loop(surface):
            # Use previous frame if feedback detected
            if self.prev_frame is not None:
                self.capture_retry_count += 1
                
                # If too many retries, pause briefly
                if self.capture_retry_count > self.max_retries:
                    import time
                    time.sleep(0.1)
                    self.capture_retry_count = 0
                
                return self.prev_frame
            else:
                # No previous frame, apply filter anyway
                filtered_surface = self.apply_effects(surface)
                self.prev_frame = filtered_surface.copy()
                return filtered_surface
        else:
            # No feedback detected, process normally
            self.capture_retry_count = 0
            self.add_frame_to_buffer(surface.copy())
            
            # Apply filter
            filtered_surface = self.apply_effects(surface)
            self.prev_frame = filtered_surface.copy()
            return filtered_surface
