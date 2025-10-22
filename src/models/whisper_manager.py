"""
Whisper model manager for handling model loading, inference, and resource management.
"""
import threading
import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import numpy as np
import queue


class WhisperManager:
    """Manages Whisper model loading, inference, and resource management."""
    
    def __init__(self, event_bus, config_manager=None):
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize with defaults, will be overridden by config if available
        self.model_size = "small"
        self.device = "auto"
        self.compute_type = "float16"
        self.unload_timeout = 300  # 5 minutes
        self.language = "auto"
        self.temperature = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
        self.beam_size = 5
        self.compression_ratio_threshold = 2.4
        self.logit_threshold = -1.0
        self.no_speech_threshold = 0.6
        
        # Model state
        self.model = None
        self.is_loaded = False
        self.is_loading = False
        self.last_activity_time = 0
        self.unload_timer = None
        self.transcription_queue = queue.Queue()
        
        # Threading
        self.transcription_thread = None
        self.model_lock = threading.Lock()
        
        # Register event handlers
        self.event_bus.subscribe('audio_chunk', self._on_audio_chunk)
        self.event_bus.subscribe('transcription_start', self._on_start_transcription)
        self.event_bus.subscribe('transcription_stop', self._on_stop_transcription)
        
        # Load configuration if provided
        if config_manager:
            self._load_config()
    
    def _load_config(self):
        """Load configuration values."""
        if self.config_manager:
            self.model_size = self.config_manager.get('model_size', 'small')
            self.device = self.config_manager.get('device', 'auto')
            self.compute_type = self.config_manager.get('compute_type', 'float16')
            self.unload_timeout = self.config_manager.get('unload_timeout', 300)
            self.language = self.config_manager.get('language', 'auto')
            self.temperature = self.config_manager.get('temperature', [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
            self.beam_size = self.config_manager.get('beam_size', 5)
            self.compression_ratio_threshold = self.config_manager.get('compression_ratio_threshold', 2.4)
            self.logit_threshold = self.config_manager.get('logit_threshold', -1.0)
            self.no_speech_threshold = self.config_manager.get('no_speech_threshold', 0.6)
    
    def initialize(self):
        """Initialize the model manager."""
        self.logger.info("Initializing Whisper model manager")
        
        # Load configuration
        self._load_config()
        self.logger.info("Whisper model manager initialized")
    
    def load_model(self):
        """Load the Whisper model (lazy loading)."""
        with self.model_lock:
            if self.is_loaded or self.is_loading:
                return
            
            self.is_loading = True
            self.logger.info(f"Loading Whisper model: {self.model_size}")
            
            # Start model loading in a separate thread to avoid blocking
            load_thread = threading.Thread(target=self._load_model_thread, daemon=True)
            load_thread.start()
    
    def _load_model_thread(self):
        """Load the model in a separate thread."""
        try:
            # Import here to avoid dependency issues during initialization
            from faster_whisper import WhisperModel
            
            # Determine device and compute type
            if self.device == "auto":
                device = "cuda" if self._is_cuda_available() else "cpu"
            else:
                device = self.device
            
            # Load the model
            self.model = WhisperModel(
                self.model_size,
                device=device,
                compute_type=self.compute_type,
                download_root=self._get_model_cache_dir()
            )
            
            with self.model_lock:
                self.is_loaded = True
                self.is_loading = False
                self.last_activity_time = time.time()
                
            self.logger.info(f"Whisper model loaded successfully on {device}")
            self.event_bus.publish('model_loaded')
            
            # Start transcription thread
            if self.transcription_thread is None or not self.transcription_thread.is_alive():
                self.transcription_thread = threading.Thread(target=self._transcription_worker, daemon=True)
                self.transcription_thread.start()
                
        except Exception as e:
            self.logger.error(f"Error loading Whisper model: {e}", exc_info=True)
            with self.model_lock:
                self.is_loading = False
            self.event_bus.publish('model_load_error', {'error': str(e)})
    
    def _is_cuda_available(self) -> bool:
        """Check if CUDA is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def _get_model_cache_dir(self) -> str:
        """Get the model cache directory."""
        cache_dir = Path.home() / ".cache" / "whisper_models"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return str(cache_dir)
    
    def unload_model(self):
        """Unload the Whisper model to free resources."""
        with self.model_lock:
            if not self.is_loaded:
                return
            
            self.logger.info("Unloading Whisper model")
            
            # Clear the transcription queue
            while not self.transcription_queue.empty():
                try:
                    self.transcription_queue.get_nowait()
                except queue.Empty:
                    break
            
            # Clear the model reference
            self.model = None
            self.is_loaded = False
            self.last_activity_time = 0
            
            # Cancel any scheduled unloading
            if self.unload_timer:
                self.unload_timer.cancel()
                self.unload_timer = None
            
            self.logger.info("Whisper model unloaded")
            self.event_bus.publish('model_unloaded')
    
    def schedule_unload(self):
        """Schedule model unloading after timeout."""
        with self.model_lock:
            if not self.is_loaded:
                return
            
            # Cancel existing timer
            if self.unload_timer:
                self.unload_timer.cancel()
            
            # Schedule new timer
            self.unload_timer = threading.Timer(self.unload_timeout, self.unload_model)
            self.unload_timer.daemon = True
            self.unload_timer.start()
    
    def _on_audio_chunk(self, event):
        """Handle incoming audio chunks."""
        if not self.is_loaded:
            return
            
        # Update last activity time
        self.last_activity_time = time.time()
        
        # Cancel scheduled unloading since we're active
        if self.unload_timer:
            self.unload_timer.cancel()
            self.unload_timer = None
        
        # Add audio chunk to transcription queue
        try:
            self.transcription_queue.put_nowait(event.data)
        except queue.Full:
            self.logger.warning("Transcription queue is full, dropping audio chunk")
    
    def _transcription_worker(self):
        """Worker thread for processing transcription requests."""
        while True:
            try:
                # Wait for audio chunk
                audio_chunk = self.transcription_queue.get(timeout=1.0)
                
                # Perform transcription
                if self.is_loaded and self.model:
                    transcription = self._transcribe_audio(audio_chunk['data'], audio_chunk['sample_rate'])
                    
                    # Publish result
                    self.event_bus.publish('transcription_result', {
                        'text': transcription,
                        'timestamp': time.time()
                    })
                
                self.transcription_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in transcription worker: {e}", exc_info=True)
    
    def _transcribe_audio(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Transcribe audio data using the Whisper model."""
        try:
            # Ensure audio is in the right format
            if sample_rate != 16000:
                # Resample if needed (in a real implementation, use proper resampling)
                import librosa
                audio_data = librosa.resample(audio_data.astype(np.float32), orig_sr=sample_rate, target_sr=16000)
            
            # Perform transcription with configurable parameters
            segments, info = self.model.transcribe(
                audio_data,
                beam_size=self.beam_size,
                language=self.language,
                temperature=self.temperature,
                compression_ratio_threshold=self.compression_ratio_threshold,
                logprob_threshold=self.logit_threshold,
                no_speech_threshold=self.no_speech_threshold
            )
            
            # Combine all segments
            transcription = ""
            for segment in segments:
                transcription += segment.text + " "
            
            return transcription.strip()
            
        except Exception as e:
            self.logger.error(f"Error during transcription: {e}", exc_info=True)
            return ""
    
    def _get_temperature(self) -> list:
        """Get temperature settings for transcription."""
        # Using configurable temperatures
        return self.temperature
    
    def shutdown(self):
        """Shutdown the model manager."""
        self.logger.info("Shutting down Whisper model manager")
        
        # Unload model if loaded
        with self.model_lock:
            if self.unload_timer:
                self.unload_timer.cancel()
        
        if self.is_loaded:
            self.unload_model()
        
        self.logger.info("Whisper model manager shut down")
    
    def _on_start_transcription(self, event):
        """Handle transcription start event."""
        self.load_model()
    
    def _on_stop_transcription(self, event):
        """Handle transcription stop event."""
        self.schedule_unload()