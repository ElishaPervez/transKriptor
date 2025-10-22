# Whisper Transcription Assistant

A desktop-wide transcription assistant powered by the Whisper model that activates via a hotkey and transcribes live microphone input into text. Optimized for modern GPUs including the RTX 50 series with intelligent resource management.

## Features

- Global hotkey activation (default: Ctrl+Alt+T)
- Real-time speech-to-text transcription using Whisper models
- Intelligent resource management with lazy loading and auto-unloading
- GPU-accelerated inference with support for modern GPUs
- Lightweight overlay interface
- Configurable settings (model size, hotkey, unload timeout, etc.)

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for installing from source)

## Installation

1. Clone or download this repository

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. For GPU acceleration (recommended), ensure you have:
   - CUDA-compatible GPU
   - Properly installed NVIDIA drivers
   - Compatible PyTorch build with CUDA support:
     ```bash
     # For CUDA 11.8
     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

     # For CUDA 12.1
     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
     ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Press the global hotkey (Ctrl+Alt+T by default) to activate transcription
3. Speak into your microphone
4. View the transcription results in the overlay window
5. Press the hotkey again to stop transcription

## Configuration

The application uses a `config.json` file for settings. You can configure:

- `hotkey`: Global activation hotkey (default: "ctrl+alt+t")
- `model_size`: Whisper model size ("tiny", "base", "small", "medium", "large", "large-v2", "large-v3") 
- `device`: Compute device ("auto", "cuda", "cpu")
- `compute_type`: Precision type ("float16", "float32", "int8", "int8_float16")
- `unload_timeout`: Time in seconds before auto-unloading model (default: 300 for 5 minutes)
- `vad_enabled`: Enable voice activity detection (default: True)
- `output_mode`: Where to send transcription ("clipboard", "active_window", "file")

## Architecture

The application follows a modular architecture with the following components:

- **Core**: Main application coordinator
- **Audio**: Microphone input and processing
- **Models**: Whisper model management and inference
- **UI**: Overlay window and user interface
- **Hotkey**: Global hotkey handling
- **Config**: Configuration management
- **Utils**: Shared utilities (event bus, etc.)

## Performance Optimization

### GPU Acceleration
- Uses TensorRT, CUDA, or optimized PyTorch for GPU acceleration
- Supports mixed precision (FP16/BF16) for faster inference
- Automatically falls back to CPU if GPU is unavailable

### Resource Management
- Lazy loading: Models are loaded only when transcription is active
- Auto-unloading: Models are unloaded after configurable inactivity period
- Memory efficient audio processing with proper buffering

### RTX 50 Series Support
- For RTX 50 series (Blackwell architecture), special PyTorch installation required
- Standard PyTorch releases do not officially support RTX 50 series (sm_120 architecture)
- To use RTX 50 series, you need one of the following:
  1. PyTorch nightly builds with CUDA 12.8+ support
  2. Custom PyTorch build compiled from source with CUDA 12.8+
  3. Wait for official support in PyTorch 2.8+ (expected release)
- Optimized for 9th gen Tensor Cores with FP4, FP8, FP16, and BF16 operations
- Efficient VRAM management leveraging 16GB+ memory on high-end models
- Takes advantage of enhanced AI inference capabilities of Blackwell architecture
- Includes TensorRT optimization for maximum performance on RTX 50-series cards

## Troubleshooting

### Audio Issues
- Make sure your microphone is properly selected in system audio settings
- Check that the application has microphone permissions

### GPU Issues
- Verify that PyTorch is installed with CUDA support: `python -c "import torch; print(torch.cuda.is_available())"`
- Check that you have sufficient VRAM for the selected model size

### Hotkey Issues
- The application requires system-level permissions to register global hotkeys
- Try running as administrator if hotkeys don't work

## License

This project is licensed under the MIT License - see the LICENSE file for details.