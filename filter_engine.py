"""
Filter Engine Module

Main engine that coordinates screen capture, filtering, and display.
"""

import pygame
import sys
import time
from typing import Dict
from crt_filter import CRTFilter
from window_manager import WindowManager, get_monitor_refresh_rate
from screen_capture import ScreenCapture


class FilterEngine:
    """Main engine that runs the CRT filter loop."""
    
    def __init__(self, control_panel, monitor: Dict):
        self.control_panel = control_panel
        self.monitor = monitor
        self.running = True
        
        # Initialize components
        self.window_manager = WindowManager()
        self.screen_capture = ScreenCapture(self.window_manager)
        
        # Setup display
        self.screen = self.window_manager.setup_overlay_window(monitor)
        self.clock = pygame.time.Clock()
        
        # Get refresh rate
        if sys.platform == 'linux':
            self.refresh_rate = get_monitor_refresh_rate(monitor)
        else:
            self.refresh_rate = 60.0
        print(f"Using refresh rate: {self.refresh_rate} Hz")
        
        # Create CRT filter
        self.crt_filter = CRTFilter(monitor['width'], monitor['height'])
        self._sync_filter_settings()
    
    def _sync_filter_settings(self) -> None:
        """Sync filter settings from control panel."""
        if hasattr(self.control_panel, 'crt_filter') and self.control_panel.crt_filter:
            # Update our filter with control panel settings
            self.crt_filter.update_parameters(
                scanline_intensity=self.control_panel.scanline_intensity,
                curvature=self.control_panel.curvature,
                vignette_intensity=self.control_panel.vignette_intensity,
                chromatic_aberration=self.control_panel.chromatic_aberration,
                performance_mode=self.control_panel.performance_mode
            )
        
        # Set control panel's filter reference
        self.control_panel.crt_filter = self.crt_filter
    
    def handle_keyboard_input(self, event: pygame.event.Event) -> bool:
        """
        Handle keyboard input for filter adjustments.
        
        Returns True if the engine should continue running, False to exit.
        """
        if event.key == pygame.K_ESCAPE:
            self.running = False
            self.control_panel.running = False
            self.control_panel.root.after(100, self.control_panel.root.quit)
            return False
        elif event.key == pygame.K_1:
            self.control_panel.scanline_var.set(max(0, self.control_panel.scanline_var.get() - 0.05))
            self.control_panel.update_filter_params()
        elif event.key == pygame.K_2:
            self.control_panel.scanline_var.set(min(0.5, self.control_panel.scanline_var.get() + 0.05))
            self.control_panel.update_filter_params()
        elif event.key == pygame.K_3:
            self.control_panel.curve_var.set(max(0, self.control_panel.curve_var.get() - 0.02))
            self.control_panel.update_filter_params()
        elif event.key == pygame.K_4:
            self.control_panel.curve_var.set(min(0.5, self.control_panel.curve_var.get() + 0.02))
            self.control_panel.update_filter_params()
        elif event.key == pygame.K_5:
            self.control_panel.chroma_var.set(max(0, self.control_panel.chroma_var.get() - 0.5))
            self.control_panel.update_filter_params()
        elif event.key == pygame.K_6:
            self.control_panel.chroma_var.set(min(5, self.control_panel.chroma_var.get() + 0.5))
            self.control_panel.update_filter_params()
        elif event.key == pygame.K_7:
            self.control_panel.vignette_var.set(max(0, self.control_panel.vignette_var.get() - 0.05))
            self.control_panel.update_filter_params()
        elif event.key == pygame.K_8:
            self.control_panel.vignette_var.set(min(0.5, self.control_panel.vignette_var.get() + 0.05))
            self.control_panel.update_filter_params()
        elif event.key == pygame.K_p:
            self.control_panel.perf_var.set(not self.control_panel.perf_var.get())
            self.control_panel.update_filter_params()
        
        return True
    
    def run(self) -> None:
        """Main filter loop."""
        try:
            while self.control_panel.running and self.running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.control_panel.running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        if not self.handle_keyboard_input(event):
                            break
                
                # Capture and process frame
                screen_surface = self.screen_capture.capture_screen(self.control_panel.selected_monitor)
                
                if screen_surface is not None:
                    # Process frame through CRT filter
                    filtered_surface = self.crt_filter.process_frame(screen_surface)
                    
                    # Update display
                    self.screen.fill((0, 0, 0))
                    self.screen.blit(filtered_surface, (0, 0))
                    pygame.display.flip()
                
                # Control frame rate
                self.clock.tick(self.refresh_rate)
                
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.screen_capture.close()


def run_filter(control_panel, monitor: Dict) -> None:
    """
    Main entry point for running the CRT filter.
    
    This function creates and runs the FilterEngine.
    """
    engine = FilterEngine(control_panel, monitor)
    engine.run()
