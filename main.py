"""
Main entry point for the Whisper Transcription Assistant.

This application provides a desktop-wide transcription service that can be activated
via a global hotkey to transcribe live microphone input using Whisper models.
"""
import sys
import signal
import logging
from src.core.app import TranscriptionApp

def setup_logging():
    """Configure the logging system."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('transcription_app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Whisper Transcription Assistant")
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received interrupt signal, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize and run the application
    app = TranscriptionApp()
    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise
    finally:
        logger.info("Application shutting down")

if __name__ == "__main__":
    main()