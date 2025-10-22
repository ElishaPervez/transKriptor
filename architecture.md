# Transcription Assistant - System Architecture

## Overview
A modular, desktop-wide transcription application that uses Whisper models for real-time speech-to-text conversion with intelligent resource management and global hotkey activation.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Launcher /    │    │  Global Hotkey  │    │   Overlay UI    │
│ Background      │    │    Manager      │    │                 │
│   Service       │    │                 │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      ▼                      │
          │        ┌─────────────────────────┐          │
          │        │   Audio Subsystem     │          │
          │        │   (Microphone Input)  │          │
          │        └─────────────────────────┘          │
          │                      │                      │
          │        ┌─────────────────────────┐          │
          │        │  Model Manager /      │          │
          │        │   Inference Engine    │          │
          │        └─────────────────────────┘          │
          │                      │                      │
          │        ┌─────────────────────────┐          │
          │        │  Transcription Pipe-  │          │
          │        │        line           │          │
          │        └─────────────────────────┘          │
          │                      │                      │
          │        ┌─────────────────────────┐          │
          │        │     Output Sink       │          │
          └─────────────────────────────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │                           │
          ┌─────────▼─────────┐   ┌─────────────▼──────────┐
          │  Config & Pers.   │   │ Logging & Monitoring │
          │                   │   │                      │
          └───────────────────┘   └──────────────────────┘
```

## Component Design

### 1. Launcher / Background Service
- **Purpose**: Initializes and manages all subsystems, handles application lifecycle
- **Responsibilities**:
  - Starts at system boot (optional)
  - Coordinates subsystem startup/shutdown
  - Monitors system resources and manages model loading/unloading
  - Handles inter-subsystem communication via events/observer pattern
- **Technology**: Python main application with threading for subsystem management
- **Configuration**: Starts minimized, system tray icon for configuration

### 2. Global Hotkey Manager
- **Purpose**: Registers and handles global hotkey activation
- **Responsibilities**:
  - Register user-defined hotkeys (default: Ctrl+Alt+T)
  - Handle hotkey conflicts with other applications
  - Provide fallback hotkey mechanisms
  - Allow runtime hotkey reconfiguration
- **Technology Options**: 
  - pynput (cross-platform)
  - keyboard (Windows-focused)
  - Platform-specific APIs if needed
- **Features**: 
  - Configurable hotkeys via Settings UI
  - Conflict detection
  - Hotkey testing interface

### 3. Overlay UI
- **Purpose**: Provides lightweight UI for transcription status and settings
- **Responsibilities**:
  - Display transcription output in real-time
  - Show listening status (visual indicator)
  - Provide quick access to configuration
  - Minimal resource usage when not active
- **Technology Options**:
  - PyQt/PySide (mature, cross-platform)
  - Dear PyGui (lightweight, GPU-accelerated)
  - Tkinter (built-in, simple)
- **Features**:
  - Configurable position and appearance
  - Auto-hide when not in use
  - Keyboard navigation support
  - Accessibility features

### 4. Audio Subsystem
- **Purpose**: Capture, process, and buffer microphone input
- **Responsibilities**:
  - Enumerate and select audio input devices
  - Apply real-time audio processing (noise reduction, AGC)
  - Stream audio to transcription pipeline
  - Handle different sample rates and formats
  - Implement Voice Activity Detection (VAD) to optimize processing
- **Technology Options**:
  - sounddevice (real-time capable)
  - pyaudio (established, cross-platform)
  - PortAudio bindings
- **Specifications**:
  - Target 16kHz sample rate, mono
  - Low-latency buffering (250-500ms chunks)
  - VAD to skip silence periods

### 5. Model Manager / Inference Engine
- **Purpose**: Handles Whisper model loading, execution, and resource management
- **Responsibilities**:
  - Lazy load models when transcription is requested
  - Auto-unload models after configurable timeout (default: 5 minutes)
  - Support multiple backends (PyTorch, ONNX Runtime, TensorRT)
  - Manage VRAM allocation and fallback to CPU if needed
  - Handle model variant selection (tiny, base, small, medium, large)
- **Technology Options**:
  - faster-whisper (optimized inference)
  - OpenAI Whisper + CTranslate2
  - ONNX Runtime for optimized execution
  - TensorRT for maximum GPU performance
- **Resource Management**:
  - Monitor GPU memory usage
  - Fallback to CPU if GPU memory insufficient
  - Track inference times and model performance

### 6. Transcription Pipeline
- **Purpose**: Processes audio chunks and generates text output
- **Responsibilities**:
  - Chunk audio into appropriate segments for Whisper
  - Handle streaming inference with partial results
  - Manage context between chunks for continuity
  - Apply post-processing to improve output quality
- **Features**:
  - Real-time partial transcription
  - Context preservation between chunks
  - Error handling and retry logic
  - Support for multiple languages

### 7. Output Sink
- **Purpose**: Deliver transcribed text to destination
- **Responsibilities**:
  - Copy to clipboard automatically
  - Send text to currently focused input field
  - Save to file option
  - Emit system events for integration with other apps
- **Options**:
  - Auto-send to active window
  - Manual copy option
  - File export
  - API endpoint for other applications

### 8. Configuration & Persistence
- **Purpose**: Store settings and user preferences
- **Responsibilities**:
  - Save/load user configuration (hotkeys, model selection, etc.)
  - Validate configuration schema
  - Handle profile management for different use cases
- **Format**: JSON/YAML with Pydantic validation
- **Storage**: Local config file with backup

### 9. Logging, Monitoring & Telemetry
- **Purpose**: Track application performance and issues
- **Responsibilities**:
  - Log errors, warnings, and operational status
  - Monitor GPU usage and performance metrics
  - Collect anonymized usage data (opt-in)
  - Provide diagnostic information
- **Features**:
  - Configurable log levels
  - Performance metrics collection
  - Diagnostic export for troubleshooting

## Resource Management Strategy

### Lazy Loading Implementation
- Models only loaded when transcription is actively requested
- Background service maintains minimal memory footprint
- Model loaded to GPU memory only when needed
- Automatic unloading after 5-minute inactivity (configurable)

### GPU Optimization
- Use half-precision (FP16) where possible
- Implement TensorRT optimization for supported GPUs
- Support for quantized models (INT8) for faster inference
- Monitor VRAM usage and adjust batch sizes accordingly

## Security Considerations
- Microphone access permission handling
- Data privacy (no audio or text stored by default)
- Secure configuration file permissions
- Input sanitization for all user-configurable settings

## Cross-Platform Compatibility
- Primary development on Windows
- Modular architecture for easy porting to Linux/macOS
- Platform-specific audio and hotkey handling
- Consistent UI experience across platforms

## Performance Targets
- Sub-200ms latency from speech to text display
- Minimal CPU/GPU usage when idle
- Efficient memory management to prevent leaks
- Sustained real-time transcription performance