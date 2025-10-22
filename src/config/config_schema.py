"""
Configuration schema using Pydantic for validation.
"""
from pydantic import BaseModel, validator
from typing import List, Literal, Union, Optional
import json
from pathlib import Path


class TranscriptionConfig(BaseModel):
    """Configuration schema for the transcription assistant."""
    
    # Hotkey settings
    hotkey: str = "ctrl+alt+t"
    
    # Model settings
    model_size: Literal["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"] = "small"
    device: Literal["auto", "cuda", "cpu"] = "auto"
    compute_type: Literal["float16", "float32", "int8", "int8_float16"] = "float16"
    
    # Resource management
    unload_timeout: int = 300  # 5 minutes in seconds
    
    # Audio settings
    sample_rate: int = 16000
    chunk_duration: float = 0.5  # 500ms chunks
    vad_enabled: bool = True  # This now controls faster-whisper's VAD
    vad_threshold: float = 0.01  # Not used when using faster-whisper's VAD
    use_faster_whisper_vad: bool = True  # Whether to use faster-whisper's built-in VAD
    
    # Transcription settings
    language: str = "auto"  # auto, en, es, fr, etc.
    temperature: List[Union[float, int]] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    compression_ratio_threshold: float = 2.4
    logit_threshold: float = -1.0
    no_speech_threshold: float = 0.6
    beam_size: int = 5
    
    # Output settings
    output_mode: Literal["clipboard", "active_window", "file"] = "clipboard"
    
    # Telemetry
    enable_telemetry: bool = False
    
    @validator('unload_timeout')
    def validate_unload_timeout(cls, v):
        if v < 30:  # Minimum 30 seconds
            raise ValueError('unload_timeout must be at least 30 seconds')
        return v
    
    @validator('sample_rate')
    def validate_sample_rate(cls, v):
        if v not in [8000, 11025, 16000, 22050, 32000, 44100, 48000]:
            raise ValueError('sample_rate must be a standard rate')
        return v
    
    @validator('chunk_duration')
    def validate_chunk_duration(cls, v):
        if v <= 0 or v > 2.0:  # Max 2 seconds per chunk
            raise ValueError('chunk_duration must be between 0 and 2.0 seconds')
        return v


def validate_config(config_dict: dict) -> TranscriptionConfig:
    """Validate configuration dictionary against the schema."""
    try:
        return TranscriptionConfig(**config_dict)
    except Exception as e:
        raise ValueError(f"Invalid configuration: {str(e)}")


def create_default_config() -> TranscriptionConfig:
    """Create a default configuration instance."""
    return TranscriptionConfig()


def load_config_from_file(file_path: Union[str, Path]) -> TranscriptionConfig:
    """Load and validate configuration from a JSON file."""
    path = Path(file_path)
    
    if not path.exists():
        # Create default config file
        default_config = create_default_config()
        save_config_to_file(default_config, path)
        return default_config
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        return validate_config(config_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")


def save_config_to_file(config: TranscriptionConfig, file_path: Union[str, Path]) -> None:
    """Save configuration to a JSON file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config.dict(), f, indent=2, ensure_ascii=False)


# Update the ConfigManager to use Pydantic
if __name__ == "__main__":
    # Example usage
    config = create_default_config()
    print("Default config:", config)
    
    # Save to file
    save_config_to_file(config, "config.json")
    
    # Load from file
    loaded_config = load_config_from_file("config.json")
    print("Loaded config:", loaded_config)