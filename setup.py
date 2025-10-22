"""
Setup script for the Whisper Transcription Assistant.
"""
from setuptools import setup, find_packages
import os

# Read the README file for long description
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="transcriptor",
    version="1.0.0",
    author="Elisha Pervez",
    author_email="",
    description="Desktop-wide transcription assistant powered by Whisper model with RTX 50 series support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ElishaPervez/transKriptor",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'transcriptor=main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Console",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications :: Qt",
        "Natural Language :: English",
        "Typing :: Typed",
    ],
    python_requires='>=3.8',
    keywords='whisper, transcription, audio, ai, machine-learning, cuda, gpu, rtx, nvidia',
    project_urls={
        'Source': 'https://github.com/ElishaPervez/transKriptor',
        'Tracker': 'https://github.com/ElishaPervez/transKriptor/issues',
        'Documentation': 'https://github.com/ElishaPervez/transKriptor#readme',
    },
    include_package_data=True,
    zip_safe=False,
)