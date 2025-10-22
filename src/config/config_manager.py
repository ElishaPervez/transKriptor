"""
Configuration manager for the transcription assistant.
"""
import json
import os
from typing import Any, Union
from pathlib import Path
from .config_schema import (
    load_config_from_file, 
    save_config_to_file, 
    create_default_config,
    TranscriptionConfig
)


class ConfigManager:
    """Manages application configuration and settings with Pydantic validation."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config: TranscriptionConfig = self.load_config()
    
    def load_config(self) -> TranscriptionConfig:
        """Load configuration from file with Pydantic validation, create default if not exists."""
        try:
            return load_config_from_file(self.config_file)
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")
            # Create default config file if it doesn't exist or is invalid
            default_config = create_default_config()
            save_config_to_file(default_config, self.config_file)
            return default_config
    
    def save_config(self, config: TranscriptionConfig = None) -> None:
        """Save configuration to file."""
        config_to_save = config if config is not None else self.config
        try:
            save_config_to_file(config_to_save, self.config_file)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        # Try to get from the validated config object first
        try:
            return getattr(self.config, key, default)
        except AttributeError:
            # Fallback to dictionary access if attribute doesn't exist
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save to file."""
        # Update the validated config object
        try:
            # Create a new config with updated values
            config_dict = self.config.dict()
            config_dict[key] = value
            self.config = TranscriptionConfig(**config_dict)
            self.save_config()
        except Exception as e:
            print(f"Error setting config value: {e}")
    
    def update(self, **kwargs) -> None:
        """Update multiple configuration values at once."""
        try:
            # Create a new config with updated values
            config_dict = self.config.dict()
            config_dict.update(kwargs)
            self.config = TranscriptionConfig(**config_dict)
            self.save_config()
        except Exception as e:
            print(f"Error updating config: {e}")
    
    @property
    def validated_config(self) -> TranscriptionConfig:
        """Return the validated config object."""
        return self.config