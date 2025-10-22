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
        self.listener = None
        self.current_hotkey = set()
        
        # Thread safety
        self.hotkey_lock = threading.Lock()
    
    def initialize(self, hotkey: str = "ctrl+alt+t", callback: Callable = None):
        """Initialize the hotkey manager."""
        self.logger.info(f"Initializing hotkey manager with hotkey: {hotkey}")
        
        self.hotkey_string = hotkey.lower()
        self.callback = callback
        
        # Parse the hotkey string
        self._parse_hotkey()
        
        # Start the keyboard listener
        self.listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.listener.start()
        
        self.is_initialized = True
        self.logger.info("Hotkey manager initialized successfully")
    
    def _parse_hotkey(self):
        """Parse the hotkey string into individual keys."""
        self.pressed_keys = set()
        
        # Split the hotkey string and normalize
        parts = self.hotkey_string.replace(" ", "").split("+")
        
        for part in parts:
            # Convert common key names to their proper format
            if part in ["ctrl", "control"]:
                self.pressed_keys.add(keyboard.Key.ctrl_l)
                self.pressed_keys.add(keyboard.Key.ctrl_r)
            elif part == "alt":
                self.pressed_keys.add(keyboard.Key.alt_l)
                self.pressed_keys.add(keyboard.Key.alt_r)
            elif part == "shift":
                self.pressed_keys.add(keyboard.Key.shift_l)
                self.pressed_keys.add(keyboard.Key.shift_r)
            elif part == "win" or part == "cmd":
                self.pressed_keys.add(keyboard.Key.cmd_l)
                self.pressed_keys.add(keyboard.Key.cmd_r)
            else:
                # For regular keys, add both cases
                self.pressed_keys.add(part.lower())
                self.pressed_keys.add(part.upper())
    
    def _on_key_press(self, key):
        """Handle key press events."""
        with self.hotkey_lock:
            self.current_hotkey.add(key)
            
            # Check if current keys match the required hotkey
            if self._is_hotkey_pressed():
                if self.callback:
                    # Run callback in a separate thread to avoid blocking the listener
                    thread = threading.Thread(target=self.callback)
                    thread.daemon = True
                    thread.start()
                
                # Clear the current hotkey to prevent repeated triggers
                self.current_hotkey.clear()
    
    def _on_key_release(self, key):
        """Handle key release events."""
        with self.hotkey_lock:
            # Remove the released key from the current hotkey set
            self.current_hotkey.discard(key)
    
    def _is_hotkey_pressed(self) -> bool:
        """Check if the required hotkey is currently pressed."""
        if not self.pressed_keys:
            return False
        
        # Check if all required keys are in the current hotkey set
        for required_key in self.pressed_keys:
            if isinstance(required_key, keyboard.Key):
                # For special keys, check if either left or right version is pressed
                if required_key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
                    if keyboard.Key.ctrl_l not in self.current_hotkey and keyboard.Key.ctrl_r not in self.current_hotkey:
                        return False
                elif required_key in [keyboard.Key.alt_l, keyboard.Key.alt_r]:
                    if keyboard.Key.alt_l not in self.current_hotkey and keyboard.Key.alt_r not in self.current_hotkey:
                        return False
                elif required_key in [keyboard.Key.shift_l, keyboard.Key.shift_r]:
                    if keyboard.Key.shift_l not in self.current_hotkey and keyboard.Key.shift_r not in self.current_hotkey:
                        return False
                elif required_key in [keyboard.Key.cmd_l, keyboard.Key.cmd_r]:
                    if keyboard.Key.cmd_l not in self.current_hotkey and keyboard.Key.cmd_r not in self.current_hotkey:
                        return False
                elif required_key not in self.current_hotkey:
                    return False
            else:
                # For regular keys, check if the key is pressed
                if required_key not in self.current_hotkey:
                    return False
        
        return True
    
    def register_hotkey(self, hotkey: str, callback: Callable):
        """Register a new hotkey with a callback."""
        self.logger.info(f"Registering new hotkey: {hotkey}")
        
        # Store the new hotkey
        self.hotkey_string = hotkey.lower()
        self.callback = callback
        
        # Re-parse the hotkey
        self._parse_hotkey()
    
    def unregister_hotkey(self):
        """Unregister the current hotkey."""
        self.logger.info("Unregistering hotkey")
        
        with self.hotkey_lock:
            self.pressed_keys.clear()
            self.current_hotkey.clear()
    
    def shutdown(self):
        """Shutdown the hotkey manager."""
        self.logger.info("Shutting down hotkey manager")
        
        if self.listener:
            self.listener.stop()
        
        self.is_initialized = False
        self.logger.info("Hotkey manager shut down")