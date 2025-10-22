"""
Overlay window for displaying transcription results.
"""
import sys
import threading
import logging
from typing import Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                            QWidget, QLabel, QPushButton, QHBoxLayout, QSystemTrayIcon,
                            QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette


class OverlayWindow(QMainWindow):
    """Overlay window for displaying transcription results."""
    
    # Custom signal for updating UI from other threads
    update_text_signal = pyqtSignal(str)
    
    def __init__(self, event_bus):
        super().__init__()
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # Window state
        self.is_initialized = False
        self.is_visible = False
        self.transcription_text = ""
        
        # UI elements
        self.main_widget = None
        self.text_display = None
        self.status_label = None
        self.close_button = None
        
        # Threading
        self.ui_thread = None
        
        # Register event handlers
        self.event_bus.subscribe('transcription_result', self._on_transcription_result)
        self.event_bus.subscribe('transcription_start', self._on_transcription_start)
        self.event_bus.subscribe('transcription_stop', self._on_transcription_stop)
        
        # Connect the custom signal
        self.update_text_signal.connect(self._update_text_display)
    
    def initialize(self):
        """Initialize the overlay window."""
        self.logger.info("Initializing overlay window")
        
        # Initialize Qt application if not already done
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
        
        # Create the UI
        self._create_ui()
        
        # Position the window (top-right corner by default)
        self._position_window()
        
        # Hide initially
        self.hide()
        
        self.is_initialized = True
        self.logger.info("Overlay window initialized successfully")
    
    def _create_ui(self):
        """Create the user interface."""
        # Set window properties
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create central widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Create status label
        self.status_label = QLabel("Press hotkey to start transcription")
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 0.7);
                padding: 5px;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Create text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        self.text_display.setFont(QFont("Arial", 12))
        layout.addWidget(self.text_display)
        
        # Create close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.close_button.clicked.connect(self._on_close_clicked)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.main_widget.setLayout(layout)
        
        # Set window size
        self.resize(400, 200)
    
    def _position_window(self):
        """Position the window on screen."""
        # Position at top-right corner
        screen_geometry = self.app.desktop().screenGeometry()
        x = screen_geometry.width() - self.width() - 20
        y = 20
        self.move(x, y)
    
    def _on_transcription_result(self, event):
        """Handle transcription result events."""
        result = event.data
        text = result.get('text', '')
        
        # Update UI from the main thread using signal
        self.update_text_signal.emit(text)
    
    def _update_text_display(self, text):
        """Update the text display (called from UI thread)."""
        if self.text_display:
            # Append new text to existing text
            current_text = self.text_display.toPlainText()
            if current_text:
                current_text += "\n" + text
            else:
                current_text = text
            
            self.text_display.setPlainText(current_text)
            # Scroll to bottom
            self.text_display.moveCursor(self.text_display.textCursor().End)
    
    def _on_transcription_start(self, event):
        """Handle transcription start events."""
        self._set_status("Listening...")
        self._show_window()
    
    def _on_transcription_stop(self, event):
        """Handle transcription stop events."""
        self._set_status("Transcription stopped")
        # Keep window visible briefly to show results
        QTimer.singleShot(3000, self._hide_if_not_focused)
    
    def _set_status(self, status: str):
        """Set the status label text."""
        if self.status_label:
            self.status_label.setText(status)
    
    def _show_window(self):
        """Show the overlay window."""
        if not self.is_visible:
            self.show()
            self.is_visible = True
    
    def _hide_window(self):
        """Hide the overlay window."""
        if self.is_visible:
            self.hide()
            self.is_visible = False
    
    def _hide_if_not_focused(self):
        """Hide window if it's not focused."""
        if self.is_visible and not self.hasFocus():
            self._hide_window()
    
    def _on_close_clicked(self):
        """Handle close button click."""
        self._hide_window()
    
    def show(self):
        """Override show to ensure proper positioning."""
        self._position_window()
        super().show()
    
    def hide(self):
        """Override hide."""
        super().hide()
        self.is_visible = False
    
    def shutdown(self):
        """Shutdown the overlay window."""
        self.logger.info("Shutting down overlay window")
        
        if self.is_visible:
            self.hide()
        
        self.is_initialized = False
        self.logger.info("Overlay window shut down")