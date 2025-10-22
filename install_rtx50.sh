#!/bin/bash
# Installation script for RTX 50 series support

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing PyTorch for RTX 50 series (CUDA 12.8 nightly build)..."
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# Alternative: Install stable PyTorch (will not support RTX 50 series but works for older GPUs)
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo "Installing other requirements..."
pip install -r requirements.txt

echo ""
echo "Installation complete!"
echo "To activate the environment in the future, run: source venv/bin/activate"