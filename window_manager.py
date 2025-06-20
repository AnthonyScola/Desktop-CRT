"""
Window Manager Module

Handles overlay window creation, positioning, and manipulation for the CRT filter.
"""

import pygame
import subprocess
import sys
import os
import time
from typing import Dict, Optional, Tuple


class WindowManager:
    """Manages the overlay window properties and positioning."""
    
    def __init__(self):
        self.window_id: Optional[str] = None
        self.capture_delay = 0.02  # 20ms delay after hiding before capture
        
    def setup_overlay_window(self, monitor: Dict) -> pygame.Surface:
        """Set up a transparent, click-through overlay window on the selected monitor."""
        # Set window position and size to match the selected monitor
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{monitor['left']},{monitor['top']}"
        screen = pygame.display.set_mode(
            (monitor['width'], monitor['height']), 
            pygame.NOFRAME | pygame.SRCALPHA
        )
        pygame.display.set_caption('CRT Filter Overlay')
        
        self._setup_linux_window_properties()
        return screen
    
    def _setup_linux_window_properties(self) -> None:
        """Configure Linux-specific window properties for click-through overlay."""
        if sys.platform != "linux":
            return
            
        try:
            wm_info = pygame.display.get_wm_info()
            self.window_id = str(wm_info.get('window'))
            
            if not self.window_id or self.window_id == 'None':
                print("Could not get window ID from pygame. Overlay window properties may not be set.")
                return
                
            # Set window properties for overlay behavior
            self._set_window_class()
            self._set_window_type()
            self._set_window_state()
            self._set_window_hints()
            
        except (subprocess.CalledProcessError, FileNotFoundError, Exception) as e:
            print(f"Error setting up window properties: {e}")
            print("Note: Install xdotool/xprop/xwininfo for full functionality")
    
    def _set_window_class(self) -> None:
        """Set window class for easier identification."""
        subprocess.run([
            'xprop', '-id', self.window_id,
            '-set', 'WM_CLASS', 'crt-filter-overlay'
        ], check=False)
    
    def _set_window_type(self) -> None:
        """Set window type to dock for click-through behavior."""
        subprocess.run([
            'xprop', '-id', self.window_id,
            '-f', '_NET_WM_WINDOW_TYPE', '32a',
            '-set', '_NET_WM_WINDOW_TYPE', '_NET_WM_WINDOW_TYPE_DOCK'
        ], check=False)
    
    def _set_window_state(self) -> None:
        """Make window always on top and sticky."""
        subprocess.run([
            'xprop', '-id', self.window_id,
            '-f', '_NET_WM_STATE', '32a',
            '-set', '_NET_WM_STATE', '_NET_WM_STATE_ABOVE,_NET_WM_STATE_STICKY'
        ], check=False)
    
    def _set_window_hints(self) -> None:
        """Set override redirect to bypass window manager."""
        subprocess.run([
            'xprop', '-id', self.window_id,
            '-f', '_MOTIF_WM_HINTS', '32c',
            '-set', '_MOTIF_WM_HINTS', '2, 0, 0, 0, 0'
        ], check=False)
    
    def hide_window(self) -> bool:
        """Hide the overlay window for screen capture. Returns True if successful."""
        if not self.window_id or self.window_id == 'None':
            return False
            
        try:
            # Try xdotool first (more reliable)
            subprocess.run(['xdotool', 'windowminimize', self.window_id], 
                         check=False, timeout=0.1)
            time.sleep(self.capture_delay)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback to wmctrl
            try:
                subprocess.run(['wmctrl', '-i', '-r', self.window_id, '-b', 'add,hidden'], 
                             check=False, timeout=0.1)
                time.sleep(self.capture_delay)
                return True
            except:
                return False
    
    def restore_window(self) -> None:
        """Restore the overlay window after screen capture."""
        if not self.window_id or self.window_id == 'None':
            return
            
        try:
            # Try to unminimize first
            subprocess.run(['xdotool', 'windowmap', self.window_id], 
                         check=False, timeout=0.1)
        except:
            # Fallback to wmctrl
            try:
                subprocess.run(['wmctrl', '-i', '-r', self.window_id, '-b', 'remove,hidden'], 
                             check=False, timeout=0.1)
            except:
                pass
        
        # Ensure window stays on top
        try:
            subprocess.run(['wmctrl', '-i', '-r', self.window_id, '-b', 'add,above'], 
                         check=False, timeout=0.1)
        except:
            pass
    
    def ensure_window_restored(self) -> None:
        """Emergency window restoration with all methods."""
        if not self.window_id or self.window_id == 'None':
            return
            
        try:
            subprocess.run(['xdotool', 'windowmap', self.window_id], check=False, timeout=0.1)
            subprocess.run(['wmctrl', '-i', '-r', self.window_id, '-b', 'remove,hidden'], 
                         check=False, timeout=0.1)
            subprocess.run(['wmctrl', '-i', '-r', self.window_id, '-b', 'add,above'], 
                         check=False, timeout=0.1)
        except:
            pass


def get_monitor_refresh_rate(monitor: Dict) -> float:
    """Detect the refresh rate of the selected monitor using xrandr. Fallback to 60Hz if not found."""
    try:
        # Get monitor geometry string
        geom = f"{monitor['width']}x{monitor['height']}+{monitor['left']}+{monitor['top']}"
        # Call xrandr and parse output
        xrandr_out = subprocess.check_output(['xrandr', '--verbose'], encoding='utf-8')
        
        # Find the connected output with matching geometry
        current_output = None
        for line in xrandr_out.splitlines():
            if ' connected ' in line:
                current_output = line.split()[0]
            if current_output and geom.split('+')[0] in line and '+' in line:
                # This line should have the mode and refresh rate
                parts = line.strip().split()
                if len(parts) >= 2 and parts[0] == geom.split('+')[0]:
                    # Look for * indicating current mode
                    for i, part in enumerate(parts):
                        if '*' in part:
                            try:
                                return float(parts[i])
                            except Exception:
                                continue
        
        # Fallback: try to find the first refresh rate with *
        for line in xrandr_out.splitlines():
            if '*' in line:
                try:
                    return float(line.strip().split()[0])
                except Exception:
                    continue
    except Exception as e:
        print(f"Could not detect refresh rate, defaulting to 60Hz: {e}")
    return 60.0
