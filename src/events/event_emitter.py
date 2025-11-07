"""
Event Emitter - Centralized event emission system.
Emits structured events for progress tracking and monitoring.
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
from apify import Actor


class EventType(Enum):
    """Event types."""
    PROGRESS = "progress"
    STATUS = "status"
    SEARCH_COMPLETE = "search_complete"
    CONTENT_FETCHED = "content_fetched"
    ANALYSIS_COMPLETE = "analysis_complete"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    COMPLETION = "completion"


class EventSeverity(Enum):
    """Event severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class EventEmitter:
    """
    Centralized event emission system.
    Emits structured events for progress tracking.
    """
    
    def __init__(self):
        """Initialize event emitter."""
        self.listeners: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Dict] = []
        self.max_history = 1000
    
    def on(self, event_type: EventType, callback: Callable):
        """
        Register event listener.
        
        Args:
            event_type: Event type to listen for
            callback: Callback function
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    def emit(
        self,
        event_type: EventType,
        data: Dict,
        severity: EventSeverity = EventSeverity.INFO
    ):
        """
        Emit an event.
        
        Args:
            event_type: Event type
            data: Event data
            severity: Event severity
        """
        event = {
            'type': event_type.value,
            'severity': severity.value,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Notify listeners
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    Actor.log.warning(f"Event listener error: {e}")
        
        # Also emit via Apify Actor.events if available
        try:
            Actor.events.emit(event_type.value, event)
        except Exception:
            # Actor.events may not be available in all contexts
            pass
    
    def emit_progress(
        self,
        operation: str,
        progress_percentage: float,
        current_step: int,
        total_steps: int,
        message: Optional[str] = None
    ):
        """
        Emit progress event.
        
        Args:
            operation: Current operation name
            progress_percentage: Progress percentage (0-100)
            current_step: Current step number
            total_steps: Total steps
            message: Optional message
        """
        self.emit(
            EventType.PROGRESS,
            {
                'operation': operation,
                'progress_percentage': progress_percentage,
                'current_step': current_step,
                'total_steps': total_steps,
                'message': message
            },
            EventSeverity.INFO
        )
    
    def emit_status(
        self,
        status: str,
        message: str,
        severity: EventSeverity = EventSeverity.INFO
    ):
        """
        Emit status event.
        
        Args:
            status: Status name
            message: Status message
            severity: Event severity
        """
        self.emit(
            EventType.STATUS,
            {
                'status': status,
                'message': message
            },
            severity
        )
    
    def emit_search_complete(self, query: str, results_count: int):
        """Emit search completion event."""
        self.emit(
            EventType.SEARCH_COMPLETE,
            {
                'query': query,
                'results_count': results_count
            },
            EventSeverity.SUCCESS
        )
    
    def emit_content_fetched(self, url: str, status: str):
        """Emit content fetch event."""
        self.emit(
            EventType.CONTENT_FETCHED,
            {
                'url': url,
                'status': status
            },
            EventSeverity.INFO
        )
    
    def emit_analysis_complete(self, sources_analyzed: int, insights_count: int):
        """Emit analysis completion event."""
        self.emit(
            EventType.ANALYSIS_COMPLETE,
            {
                'sources_analyzed': sources_analyzed,
                'insights_count': insights_count
            },
            EventSeverity.SUCCESS
        )
    
    def emit_error(self, error: str, context: Optional[Dict] = None):
        """Emit error event."""
        self.emit(
            EventType.ERROR,
            {
                'error': error,
                'context': context or {}
            },
            EventSeverity.ERROR
        )
    
    def emit_completion(self, summary: Dict):
        """Emit completion event."""
        self.emit(
            EventType.COMPLETION,
            summary,
            EventSeverity.SUCCESS
        )
    
    def get_event_history(self, event_type: Optional[EventType] = None) -> List[Dict]:
        """
        Get event history.
        
        Args:
            event_type: Filter by event type (optional)
            
        Returns:
            List of events
        """
        if event_type:
            return [e for e in self.event_history if e['type'] == event_type.value]
        return self.event_history.copy()


# Global event emitter instance
_event_emitter: Optional[EventEmitter] = None


def get_event_emitter() -> EventEmitter:
    """Get global event emitter instance."""
    global _event_emitter
    if _event_emitter is None:
        _event_emitter = EventEmitter()
    return _event_emitter



