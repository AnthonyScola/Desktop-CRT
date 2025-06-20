"""
Configuration Module

Manages application settings and constants.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class FilterSettings:
    """Settings for CRT filter effects."""
    scanline_intensity: float = 0.05
    curvature: float = 0.0
    vignette_intensity: float = 0.05
    chromatic_aberration: float = 0.25
    performance_mode: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            'scanline_intensity': self.scanline_intensity,
            'curvature': self.curvature,
            'vignette_intensity': self.vignette_intensity,
            'chromatic_aberration': self.chromatic_aberration,
            'performance_mode': self.performance_mode
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterSettings':
        """Create settings from dictionary."""
        return cls(**data)


@dataclass
class AppConfig:
    """Main application configuration."""
    default_monitor: int = 0
    preview_size: tuple = (300, 200)
    preview_update_rate: int = 100  # milliseconds
    refresh_rate_fallback: float = 60.0
    
    # Window management
    capture_delay: float = 0.02  # seconds
    window_operation_timeout: float = 0.1  # seconds
    
    # Feedback detection
    frame_buffer_size: int = 3
    feedback_threshold: float = 5.0
    max_feedback_retries: int = 5
    feedback_retry_delay: float = 0.1  # seconds
    
    # Keyboard shortcuts
    keyboard_shortcuts: Dict[str, str] = None
    
    def __post_init__(self):
        if self.keyboard_shortcuts is None:
            self.keyboard_shortcuts = {
                "ESC": "Exit Filter",
                "0": "Show/Hide Controls",
                "1/2": "Adjust Scanlines (±0.05)",
                "3/4": "Adjust Curvature (±0.1)",
                "5/6": "Adjust Chromatic Aberration (±0.5)",
                "7/8": "Adjust Vignette (±0.05)",
                "P": "Toggle Performance Mode"
            }


# Global configuration instance
CONFIG = AppConfig()
FILTER_SETTINGS = FilterSettings()
