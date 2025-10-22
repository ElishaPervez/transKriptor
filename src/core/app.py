"""
Core application class that manages all subsystems.
"""
import threading
import time
import logging
from typing import Optional
from src.audio.microphone import MicrophoneManager
from src.models.whisper_manager import WhisperManager
from src.hotkey.hotkey_manager import HotkeyManager
from src.ui.overlay import OverlayWindow
from src.config.config_manager import ConfigManager
from src.utils.event_bus import EventBus


class TranscriptionApp:
    """Main application class that coordinates all subsystems."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigManager()
        self.event_bus = EventBus()
        
        # Initialize subsystems
        self.microphone_manager = MicrophoneManager(self.event_bus)
        self.whisper_manager = WhisperManager(self.event_bus)
        self.hotkey_manager = HotkeyManager(self.event_bus)
        self.overlay = OverlayWindow(self.event_bus)
        
        # Application state
        self.is_running = False
        self.transcription_active = False
        self.app_thread = None
        
    def run(self):
        """Start the application and all subsystems."""
        self.logger.info("Initializing transcription assistant...")
        
        try:
            # Initialize all subsystems
            self.microphone_manager.initialize()
            self.whisper_manager.initialize()
            self.hotkey_manager.initialize(
                hotkey=self.config.get('hotkey', 'ctrl+alt+t'),
                callback=self._toggle_transcription
            )
            self.overlay.initialize()
            
            # Start the main application loop
            self.is_running = True
            self.logger.info("All subsystems initialized, starting main loop")
            
            # Keep the main thread alive
            while self.is_running:
                time.sleep(0.1)  # Small sleep to prevent busy waiting
                
        except Exception as e:
            self.logger.error(f"Error during application startup: {e}", exc_info=True)
            raise
        finally:
            self.shutdown()
    
    def _toggle_transcription(self):
        """Toggle transcription state based on hotkey activation."""
        if not self.transcription_active:
            self.logger.info("Starting transcription session")
            self.start_transcription()
        else:
            self.logger.info("Stopping transcription session")
            self.stop_transcription()
    
    def start_transcription(self):
        """Start the transcription process."""
        if self.transcription_active:
            return
            
        self.transcription_active = True
        self.event_bus.publish('transcription_start')
        
        # Start audio capture
        self.microphone_manager.start_capture()
        
        # Load the model (lazy loading)
        self.whisper_manager.load_model()
    
    def stop_transcription(self):
        """Stop the transcription process."""
        if not self.transcription_active:
            return
            
        self.transcription_active = False
        self.event_bus.publish('transcription_stop')
        
        # Stop audio capture
        self.microphone_manager.stop_capture()
        
        # Schedule model unloading
        self.whisper_manager.schedule_unload()
    
    def shutdown(self):
        """Gracefully shutdown all subsystems."""
        self.logger.info("Shutting down application...")
        
        # Stop transcription if active
        if self.transcription_active:
            self.stop_transcription()
        
        # Shutdown subsystems in reverse order
        self.overlay.shutdown()
        self.hotkey_manager.shutdown()
        self.whisper_manager.shutdown()
        self.microphone_manager.shutdown()
        
        self.is_running = False
        self.logger.info("Application shutdown complete")