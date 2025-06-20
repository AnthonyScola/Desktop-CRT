"""
GUI Control Panel Module

Handles the tkinter-based control interface for the CRT filter.
"""

import tkinter as tk
from tkinter import ttk, Menu
import mss
import pygame
import threading
from PIL import Image, ImageTk
from typing import Optional
from filter_engine import run_filter


class ControlPanel:
    """Main GUI control panel for the CRT filter application."""
    
    def __init__(self):
        self.running = False
        self.selected_monitor = 0
        self.filter_thread: Optional[threading.Thread] = None
        self.crt_filter = None  # Will be set by FilterEngine
        self.sct = mss.mss()
        self.preview_update_id: Optional[str] = None
        
        # Initialize filter parameters
        self._init_filter_parameters()
        
        # Create and setup GUI
        self._create_main_window()
        self._create_menu()
        self._setup_tabs()
        
        # Start preview updates
        self.update_preview()
    
    def _init_filter_parameters(self) -> None:
        """Initialize default filter parameters."""
        self.scanline_intensity = 0.05
        self.curvature = 0.0
        self.vignette_intensity = 0.05
        self.chromatic_aberration = 0.25
        self.performance_mode = True
    
    def _create_main_window(self) -> None:
        """Create the main application window."""
        self.root = tk.Tk()
        self.root.title("CRT Filter Controls")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _create_menu(self) -> None:
        """Create the application menu bar."""
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
        
        help_menu.add_command(
            label="Keyboard Shortcuts", 
            command=lambda: self._show_shortcuts(shortcuts)
        )
    
    def _show_shortcuts(self, shortcuts: list) -> None:
        """Display keyboard shortcuts in a popup window."""
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.resizable(False, False)
        
        for shortcut in shortcuts:
            ttk.Label(shortcuts_window, text=shortcut, padding=5).pack(anchor='w')
    
    def _setup_tabs(self) -> None:
        """Setup the main notebook tabs."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Create tabs
        self.target_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.target_tab, text='Select Target')
        self.notebook.add(self.settings_tab, text='Filter Settings')
        
        self._setup_target_tab()
        self._setup_settings_tab()
    
    def _setup_target_tab(self) -> None:
        """Setup the target selection tab."""
        # Monitor selection
        monitor_frame = ttk.LabelFrame(self.target_tab, text="Select Monitor", padding=10)
        monitor_frame.pack(fill='x', padx=5, pady=5)
        
        self.monitor_var = tk.StringVar()
        monitors = [f"Monitor {i+1}" for i in range(len(mss.mss().monitors[1:]))]
        self.monitor_var.set(monitors[0] if monitors else "No monitors found")
        
        for i, monitor in enumerate(monitors):
            ttk.Radiobutton(
                monitor_frame, 
                text=monitor, 
                variable=self.monitor_var,
                value=monitor, 
                command=self._on_monitor_select
            ).pack(anchor='w')
        
        # Start button
        self.start_button = ttk.Button(
            monitor_frame, 
            text="Start Filter", 
            command=self.toggle_filter
        )
        self.start_button.pack(pady=10)
        
        # Preview
        preview_frame = ttk.LabelFrame(self.target_tab, text="Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack()
    
    def _setup_settings_tab(self) -> None:
        """Setup the filter settings tab."""
        # Scanlines
        self._create_setting_frame(
            "Scanlines", 
            self.scanline_intensity, 
            0, 0.5, 
            'scanline_var'
        )
        
        # Curvature
        self._create_setting_frame(
            "Screen Curvature", 
            self.curvature, 
            0, 0.5, 
            'curve_var'
        )
        
        # Chromatic Aberration
        self._create_setting_frame(
            "Chromatic Aberration", 
            self.chromatic_aberration, 
            0, 5, 
            'chroma_var'
        )
        
        # Vignette
        self._create_setting_frame(
            "Vignette", 
            self.vignette_intensity, 
            0, 0.5, 
            'vignette_var'
        )
        
        # Performance Mode
        perf_frame = ttk.LabelFrame(self.settings_tab, text="Performance Mode", padding=10)
        perf_frame.pack(fill='x', padx=5, pady=5)
        
        self.perf_var = tk.BooleanVar(value=self.performance_mode)
        ttk.Checkbutton(
            perf_frame, 
            text="Enable Performance Mode", 
            variable=self.perf_var,
            command=self.update_filter_params
        ).pack()
    
    def _create_setting_frame(self, title: str, initial_value: float, 
                            min_val: float, max_val: float, var_name: str) -> None:
        """Create a settings frame with a scale widget."""
        frame = ttk.LabelFrame(self.settings_tab, text=title, padding=10)
        frame.pack(fill='x', padx=5, pady=5)
        
        var = tk.DoubleVar(value=initial_value)
        setattr(self, var_name, var)
        
        ttk.Scale(
            frame, 
            from_=min_val, 
            to=max_val, 
            variable=var,
            command=self.update_filter_params
        ).pack(fill='x')
    
    def update_filter_params(self, *args) -> None:
        """Update filter parameters from GUI controls."""
        self.scanline_intensity = self.scanline_var.get()
        self.curvature = self.curve_var.get()
        self.vignette_intensity = self.vignette_var.get()
        self.chromatic_aberration = self.chroma_var.get()
        self.performance_mode = self.perf_var.get()
        
        if self.crt_filter:
            self.crt_filter.update_parameters(
                scanline_intensity=self.scanline_intensity,
                curvature=self.curvature,
                vignette_intensity=self.vignette_intensity,
                chromatic_aberration=self.chromatic_aberration,
                performance_mode=self.performance_mode
            )
    
    def _on_monitor_select(self) -> None:
        """Handle monitor selection change."""
        monitor_num = int(self.monitor_var.get().split()[-1]) - 1
        self.selected_monitor = monitor_num
    
    def update_preview(self) -> None:
        """Update the preview image."""
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
                img = self._apply_preview_filter(img)
            
            # Convert to PhotoImage and update display
            photo = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo
            
        except Exception as e:
            print(f"Preview update error: {e}")
        
        if not self.preview_update_id:
            self.preview_update_id = self.root.after(100, self.update_preview)
    
    def _apply_preview_filter(self, img: Image.Image) -> Image.Image:
        """Apply CRT filter to preview image."""
        try:
            # Convert to pygame surface for filtering
            img_str = img.tobytes()
            img_surface = pygame.image.fromstring(img_str, img.size, img.mode)
            filtered_surface = self.crt_filter.apply_effects(img_surface)
            
            # Convert back to PIL
            filtered_str = pygame.image.tostring(filtered_surface, 'RGB')
            return Image.frombytes('RGB', filtered_surface.get_size(), filtered_str)
        except Exception as e:
            print(f"Preview filter error: {e}")
            return img
    
    def toggle_filter(self) -> None:
        """Start or stop the CRT filter."""
        if not self.running and not self.filter_thread:
            self._start_filter()
        else:
            self._stop_filter()
    
    def _start_filter(self) -> None:
        """Start the CRT filter."""
        pygame.init()
        monitor = self.sct.monitors[self.selected_monitor + 1]
        
        self.running = True
        self.start_button.configure(text="Stop Filter")
        self.filter_thread = threading.Thread(target=run_filter, args=(self, monitor))
        self.filter_thread.start()
        self.root.bind('<Escape>', lambda e: self._stop_filter())
    
    def _stop_filter(self) -> None:
        """Stop the CRT filter."""
        if self.running:
            self.running = False
            self.start_button.configure(text="Start Filter")
            self.root.unbind('<Escape>')
            
            if self.filter_thread:
                self.filter_thread.join()
                self.filter_thread = None
                pygame.quit()
    
    def on_closing(self) -> None:
        """Handle application closing."""
        self.running = False
        
        if self.filter_thread:
            self.filter_thread.join()
        
        if self.preview_update_id:
            self.root.after_cancel(self.preview_update_id)
        
        self.sct.close()
        self.root.destroy()
