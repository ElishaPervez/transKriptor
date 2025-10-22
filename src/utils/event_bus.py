"""
Event bus for inter-component communication.
"""
import threading
from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    """Represents an event in the system."""
    name: str
    data: Any = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class EventBus:
    """Thread-safe event bus for communication between components."""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._lock = threading.RLock()
    
    def subscribe(self, event_name: str, handler: Callable) -> None:
        """Subscribe to an event."""
        with self._lock:
            if event_name not in self._handlers:
                self._handlers[event_name] = []
            if handler not in self._handlers[event_name]:
                self._handlers[event_name].append(handler)
    
    def unsubscribe(self, event_name: str, handler: Callable) -> None:
        """Unsubscribe from an event."""
        with self._lock:
            if event_name in self._handlers:
                try:
                    self._handlers[event_name].remove(handler)
                except ValueError:
                    pass  # Handler was not subscribed
    
    def publish(self, event_name: str, data: Any = None) -> None:
        """Publish an event to all subscribers."""
        event = Event(name=event_name, data=data)
        
        with self._lock:
            handlers = self._handlers.get(event_name, []).copy()
        
        # Call handlers outside the lock to prevent deadlocks
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler for {event_name}: {e}")