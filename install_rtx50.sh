#!/bin/bash
# Installation script for RTX 50 series support

# For RTX 50 series (Blackwell architecture) with CUDA 12.8 support, use:
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# Alternative: Install stable PyTorch (will not support RTX 50 series but works for older GPUs)
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install the rest of the requirements
pip install -r requirements.txt