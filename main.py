"""
CRT Filter - Real-time screen filter with CRT monitor effects

This application captures the screen in real-time and applies various CRT effects like
scanlines, curvature, chromatic aberration, and vignette.

To prevent the overlay window from capturing itself and causing a black screen:
1. The overlay window is temporarily hidden/minimized before screen capture
2. A frame buffer system detects feedback loops by comparing consecutive frames
3. If feedback is detected, the previous clean frame is reused
4. Multiple fallback methods ensure reliable window hiding (xdotool, wmctrl)
5. Proper timing delays prevent race conditions between hiding and capture

The feedback detection system prevents the common issue where the filter captures
its own output, leading to a black screen or feedback loop.
"""

import sys
import signal
from gui import ControlPanel


def main():
    """Main entry point for the CRT Filter application."""
    control_panel = ControlPanel()

    def handle_exit(signum, frame):
        """Handle exit signals gracefully."""
        print("\nExiting...")
        control_panel.running = False
        try:
            control_panel.root.quit()
        except Exception:
            pass
        sys.exit(0)

    # Set up signal handlers
    signal.signal(signal.SIGINT, handle_exit)   # Handle Ctrl+C
    signal.signal(signal.SIGTERM, handle_exit)  # Handle kill

    # Start the GUI main loop
    control_panel.root.mainloop()


if __name__ == "__main__":
    main()
