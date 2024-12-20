# CRT Filter

A Python-based CRT (Cathode Ray Tube) screen filter effect using Pygame. This application creates a realistic CRT monitor effect with various customizable parameters.

## Features

- Real-time screen capture and filtering
- Monitor selection
- Live preview
- Adjustable parameters:
  - Scanline intensity
  - Screen curvature
  - Chromatic aberration
  - Vignette effect
- Performance mode for better frame rates

## Usage

1. Launch the application:
```bash
python main.py
```

2. In the "Select Target" tab:
   - Choose the monitor you want to apply the filter to
   - Click "Start Filter" to begin
   - Click "Stop Filter" to stop the effect

3. In the "Filter Settings" tab, adjust parameters:
   - Scanlines: Controls the intensity of horizontal scanlines
   - Screen Curvature: Adjusts the barrel distortion effect
   - Chromatic Aberration: Controls RGB channel separation
   - Vignette: Adjusts corner darkening effect
   - Performance Mode: Toggle for better performance on slower systems

## Controls

- Use sliders to adjust effects in real-time
- ESC: Exit the filter when it's running
- Window close button: Exit the application

## Requirements

- Python 3.x
- Pygame
- NumPy
- Pillow (PIL)
- MSS (screen capture)
- Tkinter (included with Python)

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
