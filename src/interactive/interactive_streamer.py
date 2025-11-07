"""
Interactive Streamer - Provides real-time progress updates for interactive mode.
Shows findings as they're discovered and allows user interaction.
"""

from typing import Dict, List, Optional
from datetime import datetime
from apify import Actor

from src.streaming.progress_streamer import ProgressStreamer


class InteractiveStreamer(ProgressStreamer):
    """
    Enhanced progress streamer for interactive mode.
    Provides real-time updates and allows user interaction.
    """
    
    def __init__(self):
        """Initialize interactive streamer."""
        super().__init__()
        self.findings_updates: List[Dict] = []
        self.sources_updates: List[Dict] = []
        self.insights_updates: List[Dict] = []
    
    def add_finding(self, finding: str, source: Optional[Dict] = None):
        """
        Add a new finding update.
        
        Args:
            finding: Finding text
            source: Optional source dictionary
        """
        update = {
            'finding': finding,
            'source': source,
            'timestamp': datetime.now().isoformat()
        }
        self.findings_updates.append(update)
        
        # Update Key-Value Store (async, but called from sync context)
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule async update
                asyncio.create_task(self._update_findings_store())
            else:
                loop.run_until_complete(self._update_findings_store())
        except Exception:
            pass  # Skip if async context not available
    
    def add_source(self, source: Dict):
        """
        Add a new source update.
        
        Args:
            source: Source dictionary
        """
        self.sources_updates.append(source)
        # Update Key-Value Store (async, but called from sync context)
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._update_sources_store())
            else:
                loop.run_until_complete(self._update_sources_store())
        except Exception:
            pass
    
    def add_insight(self, insight: str, category: Optional[str] = None):
        """
        Add a new insight update.
        
        Args:
            insight: Insight text
            category: Optional category
        """
        update = {
            'insight': insight,
            'category': category,
            'timestamp': datetime.now().isoformat()
        }
        self.insights_updates.append(update)
        # Update Key-Value Store (async, but called from sync context)
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._update_insights_store())
            else:
                loop.run_until_complete(self._update_insights_store())
        except Exception:
            pass
    
    def get_current_findings(self) -> List[Dict]:
        """
        Get current findings discovered so far.
        
        Returns:
            List of findings
        """
        return self.findings_updates
    
    def get_current_sources(self) -> List[Dict]:
        """
        Get current sources discovered so far.
        
        Returns:
            List of sources
        """
        return self.sources_updates
    
    def get_current_insights(self) -> List[Dict]:
        """
        Get current insights discovered so far.
        
        Returns:
            List of insights
        """
        return self.insights_updates
    
    def get_interactive_summary(self) -> Dict:
        """
        Get interactive summary of current progress.
        
        Returns:
            Summary dictionary
        """
        return {
            'progress_percentage': self.get_progress_percentage(),
            'findings_count': len(self.findings_updates),
            'sources_count': len(self.sources_updates),
            'insights_count': len(self.insights_updates),
            'recent_findings': self.findings_updates[-5:] if len(self.findings_updates) > 5 else self.findings_updates,
            'recent_sources': self.sources_updates[-5:] if len(self.sources_updates) > 5 else self.sources_updates,
            'recent_insights': self.insights_updates[-5:] if len(self.insights_updates) > 5 else self.insights_updates
        }
    
    async def _update_findings_store(self):
        """Update findings in Key-Value Store."""
        try:
            await Actor.set_value('interactive_findings', self.findings_updates[-20:])  # Last 20
        except Exception as e:
            Actor.log.warning(f"Failed to update findings store: {e}")
    
    async def _update_sources_store(self):
        """Update sources in Key-Value Store."""
        try:
            await Actor.set_value('interactive_sources', self.sources_updates[-50:])  # Last 50
        except Exception as e:
            Actor.log.warning(f"Failed to update sources store: {e}")
    
    async def _update_insights_store(self):
        """Update insights in Key-Value Store."""
        try:
            await Actor.set_value('interactive_insights', self.insights_updates[-20:])  # Last 20
        except Exception as e:
            Actor.log.warning(f"Failed to update insights store: {e}")


def create_interactive_streamer() -> InteractiveStreamer:
    """Create an interactive streamer instance."""
    return InteractiveStreamer()

