import pygame
import sys
import os
import numpy as np
import mss
import tkinter as tk
from tkinter import ttk, Menu
from PIL import Image, ImageTk, ImageDraw
import threading
import subprocess

class ControlPanel:
    def __init__(self):
        self.running = False  # Start as not running
        self.selected_monitor = 0
        self.selected_window = None
        self.filter_thread = None
        self.crt_filter = None  # Will be initialized when filter starts
        self.sct = mss.mss()  # Create single mss instance
        self.preview_update_id = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("CRT Filter Controls")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create menu bar
        self.create_menu()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tabs
        self.target_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.target_tab, text='Select Target')
        self.notebook.add(self.settings_tab, text='Filter Settings')
        
        self.setup_target_tab()
        self.setup_settings_tab()
        
        # Update preview periodically
        self.update_preview()

    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # Help menu with shortcuts
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        shortcuts = [
            "ESC - Exit Filter",
            "0 - Show/Hide Controls",
            "1/2 - Adjust Scanlines (±0.05)",
            "3/4 - Adjust Curvature (±0.1)",
            "5/6 - Adjust Chromatic Aberration (±0.5)",
            "7/8 - Adjust Vignette (±0.05)",
            "P - Toggle Performance Mode"
        ]
        
        help_menu.add_command(label="Keyboard Shortcuts", command=lambda: self.show_shortcuts(shortcuts))

    def show_shortcuts(self, shortcuts):
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.resizable(False, False)
        
        for shortcut in shortcuts:
            ttk.Label(shortcuts_window, text=shortcut, padding=5).pack(anchor='w')

    def setup_target_tab(self):
        # Monitor selection
        monitor_frame = ttk.LabelFrame(self.target_tab, text="Select Monitor", padding=10)
        monitor_frame.pack(fill='x', padx=5, pady=5)
        
        self.monitor_var = tk.StringVar()
        monitors = [f"Monitor {i+1}" for i in range(len(mss.mss().monitors[1:]))]
        self.monitor_var.set(monitors[0])
        
        for i, monitor in enumerate(monitors):
            ttk.Radiobutton(monitor_frame, text=monitor, variable=self.monitor_var, 
                          value=monitor, command=self.on_monitor_select).pack(anchor='w')
        
        # Start button
        self.start_button = ttk.Button(monitor_frame, text="Start Filter", command=self.toggle_filter)
        self.start_button.pack(pady=10)
        
        # Preview
        preview_frame = ttk.LabelFrame(self.target_tab, text="Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack()

    def setup_settings_tab(self):
        # Initialize default values
        self.scanline_intensity = 0.05  # Start with lighter scanlines
        self.curvature = 0.0  # Start flat
        self.vignette_intensity = 0.05  # Even lighter vignette
        self.chromatic_aberration = 0.25  # Less chromatic aberration
        self.performance_mode = True
        
        # Scanlines
        scanline_frame = ttk.LabelFrame(self.settings_tab, text="Scanlines", padding=10)
        scanline_frame.pack(fill='x', padx=5, pady=5)
        
        self.scanline_var = tk.DoubleVar(value=self.scanline_intensity)
        ttk.Scale(scanline_frame, from_=0, to=0.5, variable=self.scanline_var, 
                 command=self.update_filter_params).pack(fill='x')
        
        # Curvature
        curve_frame = ttk.LabelFrame(self.settings_tab, text="Screen Curvature", padding=10)
        curve_frame.pack(fill='x', padx=5, pady=5)
        
        self.curve_var = tk.DoubleVar(value=self.curvature)
        ttk.Scale(curve_frame, from_=0, to=0.5, variable=self.curve_var,
                 command=self.update_filter_params).pack(fill='x')
        
        # Chromatic Aberration
        chroma_frame = ttk.LabelFrame(self.settings_tab, text="Chromatic Aberration", padding=10)
        chroma_frame.pack(fill='x', padx=5, pady=5)
        
        self.chroma_var = tk.DoubleVar(value=self.chromatic_aberration)
        ttk.Scale(chroma_frame, from_=0, to=5, variable=self.chroma_var,
                 command=self.update_filter_params).pack(fill='x')
        
        # Vignette
        vignette_frame = ttk.LabelFrame(self.settings_tab, text="Vignette", padding=10)
        vignette_frame.pack(fill='x', padx=5, pady=5)
        
        self.vignette_var = tk.DoubleVar(value=self.vignette_intensity)
        ttk.Scale(vignette_frame, from_=0, to=0.5, variable=self.vignette_var,
                 command=self.update_filter_params).pack(fill='x')
        
        # Performance Mode
        perf_frame = ttk.LabelFrame(self.settings_tab, text="Performance Mode", padding=10)
        perf_frame.pack(fill='x', padx=5, pady=5)
        
        self.perf_var = tk.BooleanVar(value=self.performance_mode)
        ttk.Checkbutton(perf_frame, text="Enable Performance Mode", variable=self.perf_var,
                       command=self.update_filter_params).pack()

    def update_filter_params(self, *args):
        self.scanline_intensity = self.scanline_var.get()
        self.curvature = self.curve_var.get()
        self.vignette_intensity = self.vignette_var.get()
        self.chromatic_aberration = self.chroma_var.get()
        self.performance_mode = self.perf_var.get()
        
        if self.crt_filter:
            self.crt_filter.scanline_intensity = self.scanline_intensity
            self.crt_filter.curvature = self.curvature
            self.crt_filter.vignette_intensity = self.vignette_intensity
            self.crt_filter.chromatic_aberration = self.chromatic_aberration
            self.crt_filter.performance_mode = self.performance_mode

    def on_monitor_select(self):
        monitor_num = int(self.monitor_var.get().split()[-1]) - 1
        self.selected_monitor = monitor_num

    def update_preview(self):
        if not self.running and self.preview_update_id:
            self.preview_update_id = None
            return
            
        try:
            monitor = self.sct.monitors[self.selected_monitor + 1]
            screenshot = self.sct.grab(monitor)
            
            # Convert to PIL Image and resize for preview
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            img.thumbnail((300, 200))
            
            # Apply preview filter if running
            if self.running and self.crt_filter:
                # Convert to pygame surface for filtering
                img_str = img.tobytes()
                img_surface = pygame.image.fromstring(img_str, img.size, img.mode)
                filtered_surface = self.crt_filter.apply(img_surface)
                
                # Convert back to PIL
                filtered_str = pygame.image.tostring(filtered_surface, 'RGB')
                img = Image.frombytes('RGB', filtered_surface.get_size(), filtered_str)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo
        except Exception as e:
            print(f"Preview update error: {e}")
        
        if not self.preview_update_id:
            self.preview_update_id = self.root.after(100, self.update_preview)  # Lower update rate

    def toggle_filter(self):
        if not self.running and not self.filter_thread:
            # Start the filter
            pygame.init()
            screen_info = pygame.display.Info()
            self.crt_filter = CRTFilter(screen_info.current_w, screen_info.current_h)
            self.update_filter_params()
            
            self.running = True
            self.start_button.configure(text="Stop Filter")
            self.filter_thread = threading.Thread(target=run_filter, args=(self,))
            self.filter_thread.start()
            self.root.bind('<Escape>', lambda e: self.stop_filter())
            
            # Hide GUI
            self.root.withdraw()
        else:
            self.stop_filter()
            
    def stop_filter(self):
        if self.running:
            self.running = False
            self.start_button.configure(text="Start Filter")
            self.root.unbind('<Escape>')
            if self.filter_thread:
                self.filter_thread.join()
                self.filter_thread = None
                pygame.quit()

    def on_closing(self):
        self.running = False
        if self.filter_thread:
            self.filter_thread.join()
        if self.preview_update_id:
            self.root.after_cancel(self.preview_update_id)
        self.sct.close()
        self.root.destroy()

class CRTFilter:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.scanline_intensity = 0.05
        self.curvature = 0.0
        self.vignette_intensity = 0.1
        self.chromatic_aberration = 0.5
        self.performance_mode = True
        self.prev_frame = None  # Store previous frame

    def create_coordinate_grid(self, width, height):
        x = np.linspace(-1, 1, width)
        y = np.linspace(-1, 1, height)
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + Y**2)
        return X, Y, R

    def apply_scanlines(self, surface):
        height = surface.get_height()
        width = surface.get_width()
        for y in range(0, height, 2):
            line_surface = pygame.Surface((width, 1), pygame.SRCALPHA)
            line_surface.fill((0, 0, 0, int(255 * self.scanline_intensity)))
            surface.blit(line_surface, (0, y))

    def apply_chromatic_aberration(self, surface):
        result = surface.copy()
        width = surface.get_width()
        
        pixels = pygame.surfarray.pixels3d(result)
        offset = max(1, int(self.chromatic_aberration * (width / self.width)))
        
        red = pixels[:, :, 0].copy()
        pixels[offset:, :, 0] = red[:-offset, :]
        
        blue = pixels[:, :, 2].copy()
        pixels[:-offset, :, 2] = blue[offset:, :]
        
        del pixels
        return result

    def apply_vignette(self, surface):
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

    def apply_curvature(self, surface):
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

    def apply(self, surface):
        result = surface.copy()
        
        if self.performance_mode:
            scale = 0.5
            small_size = (int(self.width * scale), int(self.height * scale))
            small_surface = pygame.transform.smoothscale(result, small_size)
            
            small_surface = self.apply_chromatic_aberration(small_surface)
            small_surface = self.apply_curvature(small_surface)
            self.apply_scanlines(small_surface)
            self.apply_vignette(small_surface)
            
            result = pygame.transform.smoothscale(small_surface, (self.width, self.height))
        else:
            result = self.apply_chromatic_aberration(result)
            result = self.apply_curvature(result)
            self.apply_scanlines(result)
            self.apply_vignette(result)
        
        return result

def setup_overlay_window():
    """Set up a transparent, click-through overlay window."""
    # Create transparent overlay window
    screen = pygame.display.set_mode((0, 0), pygame.NOFRAME | pygame.SRCALPHA)
    pygame.display.set_caption('CRT Filter')
    
    if sys.platform == "linux":
        try:
            # Get window ID
            window_id = subprocess.check_output(['xdotool', 'search', '--name', 'CRT Filter']).decode().strip()
            if window_id:
                # Set window type to dock for click-through
                subprocess.run([
                    'xprop', '-id', window_id,
                    '-f', '_NET_WM_WINDOW_TYPE', '32a',
                    '-set', '_NET_WM_WINDOW_TYPE', '_NET_WM_WINDOW_TYPE_DOCK'
                ])
                
                # Make window always on top and sticky
                subprocess.run([
                    'xprop', '-id', window_id,
                    '-f', '_NET_WM_STATE', '32a',
                    '-set', '_NET_WM_STATE', '_NET_WM_STATE_ABOVE,_NET_WM_STATE_STICKY'
                ])
                
                # Set window shape to make it click-through
                subprocess.run(['xwininfo', '-id', window_id, '-shape'])
                
                # Set override redirect to bypass window manager
                subprocess.run([
                    'xprop', '-id', window_id,
                    '-f', '_MOTIF_WM_HINTS', '32c',
                    '-set', '_MOTIF_WM_HINTS', '2, 0, 0, 0, 0'
                ])
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error setting up window properties: {e}")
            print("Note: Install xdotool for full functionality")
    
    return screen

def run_filter(control_panel):
    import subprocess  # Add missing import
    
    # Setup overlay window
    screen = setup_overlay_window()
    
    clock = pygame.time.Clock()
    sct = mss.mss()
    
    # Set window to be always on top and click-through
    try:
        window_id = subprocess.check_output(['xdotool', 'search', '--name', 'CRT Filter']).decode().strip()
        if window_id:
            subprocess.run(['xdotool', 'windowraise', window_id])
            subprocess.run(['wmctrl', '-i', '-r', window_id, '-b', 'add,above,sticky'])
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error setting window properties: {e}")
    
    try:
        while control_panel.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    control_panel.running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        control_panel.running = False
                        control_panel.root.after(100, control_panel.root.quit)
                        break
                    elif event.key == pygame.K_1:
                        control_panel.scanline_var.set(max(0, control_panel.scanline_var.get() - 0.05))
                        control_panel.update_filter_params()
                    elif event.key == pygame.K_2:
                        control_panel.scanline_var.set(min(0.5, control_panel.scanline_var.get() + 0.05))
                        control_panel.update_filter_params()
                    elif event.key == pygame.K_3:
                        control_panel.curve_var.set(max(0, control_panel.curve_var.get() - 0.02))
                        control_panel.update_filter_params()
                    elif event.key == pygame.K_4:
                        control_panel.curve_var.set(min(0.5, control_panel.curve_var.get() + 0.02))
                        control_panel.update_filter_params()
                    elif event.key == pygame.K_5:
                        control_panel.chroma_var.set(max(0, control_panel.chroma_var.get() - 0.5))
                        control_panel.update_filter_params()
                    elif event.key == pygame.K_6:
                        control_panel.chroma_var.set(min(5, control_panel.chroma_var.get() + 0.5))
                        control_panel.update_filter_params()
                    elif event.key == pygame.K_7:
                        control_panel.vignette_var.set(max(0, control_panel.vignette_var.get() - 0.05))
                        control_panel.update_filter_params()
                    elif event.key == pygame.K_8:
                        control_panel.vignette_var.set(min(0.5, control_panel.vignette_var.get() + 0.05))
                        control_panel.update_filter_params()
                    elif event.key == pygame.K_p:
                        control_panel.perf_var.set(not control_panel.perf_var.get())
                        control_panel.update_filter_params()
                    elif event.key == pygame.K_0:
                        # Toggle GUI visibility
                        if control_panel.root.state() == 'withdrawn':
                            control_panel.root.deiconify()
                        else:
                            control_panel.root.withdraw()
            
            try:
                # Capture screen
                monitor = sct.monitors[control_panel.selected_monitor + 1]
                screen_shot = sct.grab(monitor)
                
                # Get filter window geometry
                window_id = subprocess.check_output(['xdotool', 'search', '--name', 'CRT Filter']).decode().strip()
                window_info = subprocess.check_output(['xwininfo', '-id', window_id]).decode()
                
                # Parse window geometry
                x = int(next(line.split(':')[1] for line in window_info.split('\n') if 'Absolute upper-left X' in line))
                y = int(next(line.split(':')[1] for line in window_info.split('\n') if 'Absolute upper-left Y' in line))
                width = int(next(line.split(':')[1] for line in window_info.split('\n') if 'Width' in line))
                height = int(next(line.split(':')[1] for line in window_info.split('\n') if 'Height' in line))
                
                # Convert to PIL Image
                img = Image.frombytes('RGB', screen_shot.size, screen_shot.rgb)
                
                # Create a mask to exclude the filter window region
                mask = Image.new('L', img.size, 255)
                draw = ImageDraw.Draw(mask)
                window_x = x - monitor['left']
                window_y = y - monitor['top']
                draw.rectangle([window_x, window_y, window_x + width, window_y + height], fill=0)
                
                # Apply the mask
                img.putalpha(mask)
                img = Image.alpha_composite(Image.new('RGBA', img.size, (0, 0, 0, 0)), img)
                img = img.convert('RGB')
                
                # Convert to pygame surface
                img_str = img.tobytes()
                screen_surface = pygame.image.fromstring(img_str, img.size, img.mode)
                screen_surface = screen_surface.convert()  # Convert to display format
                
                # Apply filter
                filtered_surface = control_panel.crt_filter.apply(screen_surface)
                
                # Update display
                screen.fill((0, 0, 0))
                screen.blit(filtered_surface, (0, 0))
                pygame.display.flip()
                
                # Control frame rate
                clock.tick(120)
            except Exception as e:
                print(f"Error during screen capture: {e}")
                continue
    finally:
        sct.close()

def main():
    control_panel = ControlPanel()
    control_panel.root.mainloop()

if __name__ == "__main__":
    main()
