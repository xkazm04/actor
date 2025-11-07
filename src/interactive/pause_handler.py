"""
Pause Handler - Handles pause and resume functionality for research execution.
Allows users to pause research, make adjustments, and resume.
"""

from typing import Dict, Optional
from datetime import datetime
from apify import Actor


class PauseHandler:
    """
    Handles pause and resume functionality.
    Manages research state during pause/resume operations.
    """
    
    def __init__(self):
        """Initialize pause handler."""
        self.is_paused = False
        self.pause_reason: Optional[str] = None
        self.paused_at: Optional[datetime] = None
        self.resume_data: Optional[Dict] = None
    
    def pause(self, reason: Optional[str] = None):
        """
        Pause research execution.
        
        Args:
            reason: Optional reason for pausing
        """
        self.is_paused = True
        self.pause_reason = reason
        self.paused_at = datetime.now()
        Actor.log.info(f"Research paused: {reason or 'User requested'}")
    
    def resume(self) -> bool:
        """
        Resume research execution.
        
        Returns:
            True if successfully resumed
        """
        if not self.is_paused:
            return False
        
        self.is_paused = False
        pause_duration = (datetime.now() - self.paused_at).total_seconds() if self.paused_at else 0
        Actor.log.info(f"Research resumed after {pause_duration:.1f} seconds")
        
        self.pause_reason = None
        self.paused_at = None
        
        return True
    
    def is_paused_state(self) -> bool:
        """
        Check if research is currently paused.
        
        Returns:
            True if paused
        """
        return self.is_paused
    
    def get_pause_info(self) -> Optional[Dict]:
        """
        Get pause information.
        
        Returns:
            Pause info dictionary or None if not paused
        """
        if not self.is_paused:
            return None
        
        return {
            'is_paused': True,
            'reason': self.pause_reason,
            'paused_at': self.paused_at.isoformat() if self.paused_at else None,
            'pause_duration_seconds': (
                (datetime.now() - self.paused_at).total_seconds()
                if self.paused_at else 0
            )
        }
    
    def set_resume_data(self, data: Dict):
        """
        Set data needed for resume.
        
        Args:
            data: Resume data dictionary
        """
        self.resume_data = data
    
    def get_resume_data(self) -> Optional[Dict]:
        """
        Get resume data.
        
        Returns:
            Resume data dictionary or None
        """
        return self.resume_data


def create_pause_handler() -> PauseHandler:
    """Create a pause handler instance."""
    return PauseHandler()



