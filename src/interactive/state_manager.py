"""
State Manager - Manages research state for save/restore functionality.
Enables saving research progress and resuming later.
"""

from typing import Dict, List, Optional
from datetime import datetime
from apify import Actor


class StateManager:
    """
    Manages research state for save/restore functionality.
    Handles saving and loading research state.
    """
    
    def __init__(self, run_id: Optional[str] = None):
        """
        Initialize state manager.
        
        Args:
            run_id: Optional run ID for state management
        """
        self.run_id = run_id or self._generate_run_id()
    
    def _generate_run_id(self) -> str:
        """Generate unique run ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    async def save_state(
        self,
        query: str,
        progress: float,
        sources_found: List[Dict],
        analyses_complete: List[Dict],
        next_steps: List[str],
        additional_data: Optional[Dict] = None
    ) -> str:
        """
        Save research state.
        
        Args:
            query: Research query
            progress: Progress percentage (0-100)
            sources_found: List of sources found so far
            analyses_complete: List of completed analyses
            next_steps: List of next steps
            additional_data: Optional additional data
            
        Returns:
            State ID for retrieval
        """
        state = {
            'run_id': self.run_id,
            'query': query,
            'progress': progress,
            'sources_found': sources_found,
            'analyses_complete': analyses_complete,
            'next_steps': next_steps,
            'timestamp': datetime.now().isoformat(),
            'additional_data': additional_data or {}
        }
        
        # Save to Apify Key-Value Store
        state_key = f'research_state_{self.run_id}'
        await Actor.set_value(state_key, state)
        
        Actor.log.info(f"Saved research state: {self.run_id} (progress: {progress:.1f}%)")
        
        return self.run_id
    
    async def load_state(self, run_id: Optional[str] = None) -> Optional[Dict]:
        """
        Load research state.
        
        Args:
            run_id: Optional run ID (uses instance run_id if not provided)
            
        Returns:
            State dictionary or None if not found
        """
        state_id = run_id or self.run_id
        state_key = f'research_state_{state_id}'
        
        try:
            state = await Actor.get_value(state_key)
            if state:
                Actor.log.info(f"Loaded research state: {state_id}")
                return state
        except Exception as e:
            Actor.log.warning(f"Failed to load state {state_id}: {e}")
        
        return None
    
    async def list_saved_states(self, limit: int = 10) -> List[Dict]:
        """
        List saved research states.
        
        Args:
            limit: Maximum number of states to return
            
        Returns:
            List of state summaries
        """
        # Note: Apify Key-Value Store doesn't have list functionality
        # This would need to be implemented with a separate index
        # For now, return empty list
        Actor.log.warning("List saved states not fully implemented - requires index")
        return []
    
    async def delete_state(self, run_id: str) -> bool:
        """
        Delete saved research state.
        
        Args:
            run_id: Run ID to delete
            
        Returns:
            True if deleted successfully
        """
        state_key = f'research_state_{run_id}'
        try:
            await Actor.set_value(state_key, None)
            Actor.log.info(f"Deleted research state: {run_id}")
            return True
        except Exception as e:
            Actor.log.warning(f"Failed to delete state {run_id}: {e}")
            return False
    
    def get_run_id(self) -> str:
        """
        Get current run ID.
        
        Returns:
            Run ID string
        """
        return self.run_id


def create_state_manager(run_id: Optional[str] = None) -> StateManager:
    """Create a state manager instance."""
    return StateManager(run_id)

