"""
Configuration manager for the transcription assistant.
"""
import json
import os
from typing import Any, Dict
from pathlib import Path


class ConfigManager:
    """Manages application configuration and settings."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.default_config = {
            "hotkey": "ctrl+alt+t",
            "model_size": "small",  # tiny, base, small, medium, large
            "device": "auto",  # auto, cuda, cpu
            "compute_type": "float16",  # float16, float32, int8, int8_float16
            "unload_timeout": 300,  # 5 minutes in seconds
            "sample_rate": 16000,
            "chunk_duration": 0.5,  # 500ms chunks
            "vad_enabled": True,
            "vad_threshold": 0.3,
            "output_mode": "clipboard",  # clipboard, active_window, file
            "language": "auto",  # auto, en, es, fr, etc.
            "temperature": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            "compression_ratio_threshold": 2.4,
            "logit_threshold": -1.0,
            "no_speech_threshold": 0.6,
            "enable_telemetry": False
        }
        
        # Load or create config
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file, create default if not exists."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    config = self.default_config.copy()
                    config.update(user_config)
                    return config
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config, using defaults: {e}")
                return self.default_config.copy()
        else:
            # Create default config file
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any] = None) -> None:
        """Save configuration to file."""
        config_to_save = config if config is not None else self.config
        try:
            # Create directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save to file."""
        self.config[key] = value
        self.save_config()