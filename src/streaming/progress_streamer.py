"""
Progress Streamer - Provides real-time progress updates.
Calculates progress percentage and time estimates.
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from apify import Actor

from src.events.event_emitter import EventEmitter, EventType, EventSeverity, get_event_emitter


class ProgressStreamer:
    """
    Streams real-time progress updates during research execution.
    Calculates progress percentage and time estimates.
    """
    
    def __init__(self, event_emitter: Optional[EventEmitter] = None):
        """
        Initialize progress streamer.
        
        Args:
            event_emitter: Event emitter instance (optional)
        """
        self.event_emitter = event_emitter or get_event_emitter()
        self.start_time: Optional[datetime] = None
        self.operation_times: Dict[str, float] = {}
    
    def start(self, total_steps: int, operation: str = "research"):
        """
        Start progress tracking.
        
        Args:
            total_steps: Total number of steps
            operation: Operation name
        """
        self.start_time = datetime.now()
        self.event_emitter.emit_status(
            "started",
            f"Started {operation} with {total_steps} steps",
            EventSeverity.INFO
        )
    
    def update(
        self,
        current_step: int,
        total_steps: int,
        operation: str,
        message: Optional[str] = None,
        insights: Optional[List[str]] = None
    ):
        """
        Update progress.
        
        Args:
            current_step: Current step number
            total_steps: Total steps
            operation: Current operation name
            message: Optional message
            insights: Optional list of insights found
        """
        if total_steps == 0:
            progress_percentage = 0.0
        else:
            progress_percentage = (current_step / total_steps) * 100
        
        # Calculate time estimates
        time_remaining = None
        if self.start_time and current_step > 0:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            avg_time_per_step = elapsed / current_step
            remaining_steps = total_steps - current_step
            time_remaining_seconds = avg_time_per_step * remaining_steps
            time_remaining = timedelta(seconds=int(time_remaining_seconds))
        
        # Emit progress event
        progress_data = {
            'operation': operation,
            'progress_percentage': round(progress_percentage, 2),
            'current_step': current_step,
            'total_steps': total_steps,
            'message': message,
            'time_elapsed': str(datetime.now() - self.start_time) if self.start_time else None,
            'time_remaining': str(time_remaining) if time_remaining else None,
            'insights': insights or []
        }
        
        self.event_emitter.emit_progress(
            operation=operation,
            progress_percentage=progress_percentage,
            current_step=current_step,
            total_steps=total_steps,
            message=message
        )
        
        # Also save to key-value store for polling
        Actor.set_value("latest_progress", progress_data)
        
        return progress_data
    
    def complete(self, summary: Dict):
        """
        Mark progress as complete.
        
        Args:
            summary: Completion summary
        """
        if self.start_time:
            total_time = datetime.now() - self.start_time
            summary['total_time'] = str(total_time)
        
        self.event_emitter.emit_completion(summary)
        Actor.set_value("latest_progress", {
            **summary,
            'status': 'completed',
            'progress_percentage': 100.0
        })
    
    def error(self, error_message: str, context: Optional[Dict] = None):
        """
        Emit error event.
        
        Args:
            error_message: Error message
            context: Error context
        """
        self.event_emitter.emit_error(error_message, context)
        Actor.set_value("latest_progress", {
            'status': 'error',
            'error': error_message,
            'context': context or {}
        })


def create_progress_streamer() -> ProgressStreamer:
    """
    Create a progress streamer instance.
    
    Returns:
        ProgressStreamer instance
    """
    return ProgressStreamer()

