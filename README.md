# CRT Filter

A real-time CRT (Cathode Ray Tube) filter effect for your screen with customizable parameters. This application creates a nostalgic retro CRT monitor effect overlay with features like scanlines, screen curvature, chromatic aberration, and vignette effects.

## Features

- Real-time screen filtering
- Customizable effects:
  - Scanlines intensity
  - Screen curvature
  - Chromatic aberration
  - Vignette effect
- Performance mode for better frame rates
- Click-through overlay window
- Multi-monitor support
- Live preview
- Keyboard shortcuts for quick adjustments

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
3. Click "Start Filter" to apply the effect
4. Use keyboard shortcuts to adjust parameters in real-time

### Keyboard Shortcuts

- `ESC` - Exit Filter
- `0` - Show/Hide Controls
- `1/2` - Adjust Scanlines (±0.05)
- `3/4` - Adjust Curvature (±0.1)
- `5/6` - Adjust Chromatic Aberration (±0.5)
- `7/8` - Adjust Vignette (±0.05)
- `P` - Toggle Performance Mode

## How It Works

The application creates a transparent, click-through overlay window that captures your screen in real-time and applies various post-processing effects to simulate a CRT monitor:

- **Scanlines**: Alternating dark lines to simulate the scan pattern of CRT displays
- **Screen Curvature**: Warps the image to mimic the curved glass of old CRT monitors
- **Chromatic Aberration**: Color separation effect common in CRT displays
- **Vignette**: Darkening of the screen corners
- **Performance Mode**: Reduces resolution during processing for better performance

## Contributing

Feel free to open issues or submit pull requests with improvements.

## License

This project is open source and available under the MIT License.
