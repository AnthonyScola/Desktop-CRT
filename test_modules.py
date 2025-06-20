#!/usr/bin/env python3
"""
Test script for the CRT Filter application.

This script tests the modular components to ensure everything works correctly.
"""

import sys
import unittest
from unittest.mock import Mock, patch


class TestCRTFilterModules(unittest.TestCase):
    """Test cases for CRT Filter modules."""
    
    def test_config_import(self):
        """Test configuration module import."""
        from config import CONFIG, FILTER_SETTINGS, AppConfig, FilterSettings
        
        self.assertIsInstance(CONFIG, AppConfig)
        self.assertIsInstance(FILTER_SETTINGS, FilterSettings)
        self.assertEqual(CONFIG.default_monitor, 0)
        self.assertEqual(FILTER_SETTINGS.scanline_intensity, 0.05)
    
    def test_crt_filter(self):
        """Test CRT filter functionality."""
        from crt_filter import CRTFilter
        
        crt_filter = CRTFilter(1920, 1080)
        self.assertEqual(crt_filter.width, 1920)
        self.assertEqual(crt_filter.height, 1080)
        self.assertEqual(crt_filter.scanline_intensity, 0.05)
        
        # Test parameter update
        crt_filter.update_parameters(scanline_intensity=0.1)
        self.assertEqual(crt_filter.scanline_intensity, 0.1)
    
    def test_window_manager(self):
        """Test window manager functionality."""
        from window_manager import WindowManager, get_monitor_refresh_rate
        
        window_manager = WindowManager()
        self.assertEqual(window_manager.capture_delay, 0.02)
        
        # Test monitor refresh rate fallback
        fake_monitor = {'width': 1920, 'height': 1080, 'left': 0, 'top': 0}
        refresh_rate = get_monitor_refresh_rate(fake_monitor)
        self.assertIsInstance(refresh_rate, float)
        self.assertGreater(refresh_rate, 0)
    
    def test_screen_capture(self):
        """Test screen capture module."""
        from screen_capture import ScreenCapture
        from window_manager import WindowManager
        
        window_manager = WindowManager()
        screen_capture = ScreenCapture(window_manager)
        
        # Test cleanup
        screen_capture.close()
    
    def test_filter_engine_components(self):
        """Test filter engine imports."""
        from filter_engine import FilterEngine, run_filter
        
        # Just test that the imports work
        self.assertTrue(callable(run_filter))
    
    def test_gui_components(self):
        """Test GUI module imports."""
        from gui import ControlPanel
        
        # Test that ControlPanel can be imported
        self.assertTrue(callable(ControlPanel))


def main():
    """Run the test suite."""
    print("Running CRT Filter Module Tests...")
    print("=" * 50)
    
    # Run the tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "=" * 50)
    print("✅ All module tests completed!")
    print("\nTo run the actual application, use: python main.py")


if __name__ == "__main__":
    main()
