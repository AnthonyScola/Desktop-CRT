# CRT Filter

A real-time CRT (Cathode Ray Tube) filter effect for your screen with customizable parameters. This application creates a nostalgic retro CRT monitor effect overlay with features like scanlines, screen curvature, chromatic aberration, and vignette effects.

## Features

- **Real-time screen filtering** with optimized performance
- **Customizable effects**:
  - Scanlines intensity
  - Screen curvature
  - Chromatic aberration
  - Vignette effect
- **Advanced feedback prevention** system to avoid black screen issues
- **Performance mode** for better frame rates on lower-end hardware
- **Click-through overlay window** that doesn't interfere with other applications
- **Multi-monitor support** with automatic refresh rate detection
- **Live preview** in the control panel
- **Keyboard shortcuts** for quick adjustments during use
- **Modular architecture** for easy maintenance and extensibility

## Architecture

The application is built with a modular architecture for maintainability:

```
├── main.py              # Entry point and signal handling
├── gui.py              # Tkinter-based control panel
├── filter_engine.py    # Main filtering engine and coordination
├── crt_filter.py       # CRT effects implementation
├── window_manager.py   # Overlay window management
├── screen_capture.py   # Screen capture with feedback prevention
├── config.py           # Configuration and settings management
└── requirements.txt    # Python dependencies
```

### Key Components

- **FilterEngine**: Coordinates all components and runs the main filter loop
- **CRTFilter**: Implements visual effects (scanlines, curvature, etc.)
- **WindowManager**: Handles overlay window positioning and properties
- **ScreenCapture**: Manages screen capture with overlay hiding to prevent feedback
- **ControlPanel**: Provides the GUI interface for configuration

## Requirements

- Python 3.x
- Required Python packages (install via `pip install -r requirements.txt`):
  - pygame
  - numpy
  - mss
  - Pillow
  - python-xlib

### Linux Dependencies
- x11-utils
- xdotool

## Installation

1. Clone the repository:
```bash
git clone https://github.com/terafora/CRT-Filter.git
cd CRT-Filter
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install system dependencies (Linux):
```bash
sudo apt-get install x11-utils xdotool
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Select your target monitor from the dropdown menu
3. Adjust filter settings using the sliders in the "Filter Settings" tab
4. Click "Start Filter" to apply the effect
5. Use keyboard shortcuts to adjust parameters in real-time

### Keyboard Shortcuts

- `ESC` - Exit Filter
- `0` - Show/Hide Controls
- `1/2` - Adjust Scanlines (±0.05)
- `3/4` - Adjust Curvature (±0.02)
- `5/6` - Adjust Chromatic Aberration (±0.5)
- `7/8` - Adjust Vignette (±0.05)
- `P` - Toggle Performance Mode

## How It Works

The application creates a transparent, click-through overlay window that captures your screen in real-time and applies various post-processing effects to simulate a CRT monitor:

### Effects

- **Scanlines**: Alternating dark lines to simulate the scan pattern of CRT displays
- **Screen Curvature**: Warps the image to mimic the curved glass of old CRT monitors
- **Chromatic Aberration**: Color separation effect common in CRT displays
- **Vignette**: Darkening of the screen corners
- **Performance Mode**: Reduces resolution during processing for better performance

### Feedback Prevention

The application includes a sophisticated feedback prevention system:

1. **Window Hiding**: The overlay window is temporarily hidden during screen capture
2. **Frame Buffering**: Recent frames are stored and compared to detect feedback loops
3. **Smart Recovery**: If feedback is detected, the system uses the previous clean frame
4. **Multiple Fallback Methods**: Uses both `xdotool` and `wmctrl` for reliable window management
5. **Timing Controls**: Proper delays prevent race conditions between hiding and capture

## Performance Tips

- **Enable Performance Mode**: Processes effects at lower resolution for better frame rates
- **Adjust Effect Intensity**: Lower values generally perform better
- **Monitor Selection**: Choose the monitor with the lowest refresh rate if using multiple displays
- **System Requirements**: Better performance on systems with dedicated graphics cards

## Troubleshooting

### Black Screen Issues
The application includes advanced feedback prevention, but if you still experience black screens:
- Ensure `xdotool` and `wmctrl` are installed
- Try different monitors if using a multi-monitor setup
- Enable Performance Mode for more reliable operation

### Performance Issues
- Enable Performance Mode in settings
- Reduce effect intensities
- Close unnecessary applications
- Consider using a lower refresh rate monitor

### Window Management Issues
- Install missing dependencies: `sudo apt-get install x11-utils xdotool`
- Check that your window manager supports the required X11 properties
- Try running with different desktop environments

## Development

The modular architecture makes it easy to extend the application:

- **Add new effects**: Implement in `CRTFilter` class
- **Improve window management**: Extend `WindowManager` class
- **Add new capture methods**: Extend `ScreenCapture` class
- **Enhance GUI**: Modify `ControlPanel` class

## Contributing

Feel free to open issues or submit pull requests with improvements. The modular structure makes it easy to contribute specific enhancements.

## License

This project is open source and available under the MIT License.
