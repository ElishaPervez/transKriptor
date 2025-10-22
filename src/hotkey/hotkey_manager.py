"""
Hotkey manager for global hotkey handling.
"""
import threading
import logging
from typing import Callable, Optional
from pynput import keyboard


class HotkeyManager:
    """Manages global hotkey registration and handling."""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # Hotkey configuration
        self.hotkey_string = "ctrl+alt+t"
        self.callback = None
        
        # Hotkey state
        self.is_initialized = False
        self.hotkey_listener = None
        
    def initialize(self, hotkey: str = "ctrl+alt+t", callback: Callable = None):
        """Initialize the hotkey manager."""
        self.logger.info(f"Initializing hotkey manager with hotkey: {hotkey}")
        
        self.hotkey_string = hotkey.lower()
        self.callback = callback
        
        # Parse the hotkey string and create the hotkey listener
        try:
            # Use GlobalHotKeys for robust hotkey handling
            self.hotkey_listener = keyboard.GlobalHotKeys({
                self.hotkey_string: self._on_hotkey_pressed
            })
            self.hotkey_listener.start()
            
            self.is_initialized = True
            self.logger.info("Hotkey manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing hotkey manager: {e}")
            raise
    
    def _on_hotkey_pressed(self):
        """Handle the hotkey press event."""
        self.logger.debug(f"Hotkey pressed: {self.hotkey_string}")
        
        if self.callback:
            # Run callback in a separate thread to avoid blocking the listener
            thread = threading.Thread(target=self.callback, daemon=True)
            thread.start()
    
    def register_hotkey(self, hotkey: str, callback: Callable):
        """Register a new hotkey with a callback."""
        self.logger.info(f"Registering new hotkey: {hotkey}")
        
        # Stop the current listener
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        # Update the hotkey
        self.hotkey_string = hotkey.lower()
        self.callback = callback
        
        # Create a new listener with the updated hotkey
        self.hotkey_listener = keyboard.GlobalHotKeys({
            self.hotkey_string: self._on_hotkey_pressed
        })
        self.hotkey_listener.start()
    
    def unregister_hotkey(self):
        """Unregister the current hotkey."""
        self.logger.info("Unregistering hotkey")
        
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.hotkey_listener = None
    
    def shutdown(self):
        """Shutdown the hotkey manager."""
        self.logger.info("Shutting down hotkey manager")
        
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        self.is_initialized = False
        self.logger.info("Hotkey manager shut down")