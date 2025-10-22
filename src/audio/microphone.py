"""
Microphone manager for audio capture and processing.
"""
import threading
import queue
import time
import logging
import numpy as np
from typing import Optional, Callable
import sounddevice as sd


class MicrophoneManager:
    """Manages microphone input and audio processing."""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # Audio configuration
        self.sample_rate = 16000  # Standard for Whisper
        self.channels = 1  # Mono
        self.chunk_duration = 0.5  # 500ms chunks
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        
        # Audio state
        self.is_capturing = False
        self.is_initialized = False
        self.stream = None
        self.audio_queue = queue.Queue()
        self.capture_thread = None
        self.device_id = None
        
        # Voice activity detection
        self.vad_enabled = True
        self.vad_threshold = 0.01  # Adjust based on testing
        
        # Register event handlers
        self.event_bus.subscribe('transcription_start', self._on_start_transcription)
        self.event_bus.subscribe('transcription_stop', self._on_stop_transcription)
    
    def initialize(self):
        """Initialize the microphone manager."""
        self.logger.info("Initializing microphone manager")
        
        # Find the default input device
        try:
            default_device = sd.query_devices(kind='input')
            self.device_id = default_device['index']
            self.sample_rate = int(default_device['default_samplerate'])
            self.logger.info(f"Using audio device: {default_device['name']} (ID: {self.device_id})")
        except Exception as e:
            self.logger.error(f"Could not get default audio device: {e}")
            # Fallback to first available input device
            devices = sd.query_devices()
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    self.device_id = i
                    self.sample_rate = int(device['default_samplerate'])
                    self.logger.info(f"Using fallback audio device: {device['name']} (ID: {i})")
                    break
            else:
                raise RuntimeError("No input audio devices found")
        
        self.is_initialized = True
        self.logger.info("Microphone manager initialized successfully")
    
    def start_capture(self):
        """Start capturing audio from the microphone."""
        if self.is_capturing:
            return
            
        self.logger.info("Starting audio capture")
        
        # Create and start the audio stream
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                channels=self.channels,
                dtype='float32',
                device=self.device_id,
                callback=self._audio_callback
            )
            
            self.stream.start()
            self.is_capturing = True
            
            # Start processing thread
            self.capture_thread = threading.Thread(target=self._process_audio, daemon=True)
            self.capture_thread.start()
            
            self.event_bus.publish('audio_started')
            
        except Exception as e:
            self.logger.error(f"Error starting audio capture: {e}")
            raise
    
    def stop_capture(self):
        """Stop capturing audio."""
        if not self.is_capturing:
            return
            
        self.logger.info("Stopping audio capture")
        
        self.is_capturing = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        # Clear the audio queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        # Wait for processing thread to finish
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        
        self.event_bus.publish('audio_stopped')
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio input."""
        if status:
            self.logger.warning(f"Audio stream status: {status}")
        
        # Convert to float32 numpy array
        audio_data = indata.copy()
        
        # Add to queue for processing
        if self.is_capturing and self.audio_queue.qsize() < 10:  # Prevent queue overflow
            self.audio_queue.put(audio_data.flatten())
    
    def _process_audio(self):
        """Process audio chunks in a separate thread."""
        while self.is_capturing:
            try:
                # Get audio data from queue
                audio_chunk = self.audio_queue.get(timeout=0.1)
                
                # Apply voice activity detection if enabled
                if self.vad_enabled and not self._is_voice_present(audio_chunk):
                    continue
                
                # Publish audio chunk for transcription
                self.event_bus.publish('audio_chunk', {
                    'data': audio_chunk,
                    'sample_rate': self.sample_rate,
                    'timestamp': time.time()
                })
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing audio: {e}")
                break
    
    def _is_voice_present(self, audio_chunk: np.ndarray) -> bool:
        """Simple voice activity detection based on amplitude."""
        if len(audio_chunk) == 0:
            return False
            
        # Calculate RMS (Root Mean Square) amplitude
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        return rms > self.vad_threshold
    
    def shutdown(self):
        """Shutdown the microphone manager."""
        self.logger.info("Shutting down microphone manager")
        
        if self.is_capturing:
            self.stop_capture()
        
        self.is_initialized = False
        self.logger.info("Microphone manager shut down")
    
    def _on_start_transcription(self, event):
        """Handle transcription start event."""
        self.start_capture()
    
    def _on_stop_transcription(self, event):
        """Handle transcription stop event."""
        self.stop_capture()