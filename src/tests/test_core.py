"""
Basic tests for the transcription assistant.
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.config.config_manager import ConfigManager
from src.utils.event_bus import EventBus


class TestConfigManager(unittest.TestCase):
    """Test the configuration manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = ConfigManager(config_file="test_config.json")
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove test config file if it exists
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
    
    def test_config_defaults(self):
        """Test that config has all default values."""
        defaults = {
            "hotkey": "ctrl+alt+t",
            "model_size": "small",
            "device": "auto",
            "compute_type": "float16",
            "unload_timeout": 300,
            # Add other defaults as needed
        }
        
        for key, default_value in defaults.items():
            with self.subTest(key=key):
                self.assertEqual(self.config_manager.get(key), default_value)
    
    def test_config_set_get(self):
        """Test setting and getting configuration values."""
        test_key = "test_value"
        test_val = "test"
        
        self.config_manager.set(test_key, test_val)
        self.assertEqual(self.config_manager.get(test_key), test_val)


class TestEventBus(unittest.TestCase):
    """Test the event bus."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.event_bus = EventBus()
        self.event_received = False
        self.event_data = None
    
    def test_event_subscription(self):
        """Test event subscription and publishing."""
        def test_handler(event):
            self.event_received = True
            self.event_data = event.data
        
        self.event_bus.subscribe('test_event', test_handler)
        self.event_bus.publish('test_event', {'message': 'Hello World'})
        
        self.assertTrue(self.event_received)
        self.assertEqual(self.event_data['message'], 'Hello World')
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers to the same event."""
        self.received_events = []
        
        def handler1(event):
            self.received_events.append(f"handler1_{event.name}")
        
        def handler2(event):
            self.received_events.append(f"handler2_{event.name}")
        
        self.event_bus.subscribe('multi_test', handler1)
        self.event_bus.subscribe('multi_test', handler2)
        self.event_bus.publish('multi_test')
        
        self.assertEqual(len(self.received_events), 2)
        self.assertIn('handler1_multi_test', self.received_events)
        self.assertIn('handler2_multi_test', self.received_events)


if __name__ == '__main__':
    unittest.main()