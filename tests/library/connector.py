"""
Apify Actor Connector

Provides a shared connector for running tests against the deployed Actor.
Configuration is loaded from config.json.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from apify_client import ApifyClient


class ActorConnector:
    """Connector for interacting with the deployed Actor."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the connector with configuration.
        
        Args:
            config_path: Path to config.json file. Defaults to config.json in same directory.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize Apify client
        # Prioritize environment variable over config file for security
        token = os.getenv('APIFY_TOKEN') or self.config.get('apifyToken')
        if not token:
            raise ValueError(
                "Apify token not found. Set APIFY_TOKEN environment variable or 'apifyToken' in config.json."
            )
        
        self.client = ApifyClient(token=token)
        self.actor_id = self.config['actorId']
        self.actor_version = self.config.get('actorVersion', 'latest')
        self.timeout = self.config.get('timeout', 3600)
        self.wait_for_finish = self.config.get('waitForFinish', True)
    
    def run_actor(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the Actor with given input data.
        
        Args:
            input_data: Input data for the Actor
            
        Returns:
            Run result dictionary with status, defaultDatasetId, etc.
        """
        # Build call parameters
        call_params = {
            'run_input': input_data,
            'timeout_secs': self.timeout,
        }
        
        # If wait_for_finish is True, set wait_secs to timeout value
        # If False, set wait_secs to 0 (don't wait)
        if self.wait_for_finish:
            call_params['wait_secs'] = self.timeout
        else:
            call_params['wait_secs'] = 0
        
        # Add webhooks if configured
        webhooks = self._build_webhooks()
        if webhooks:
            call_params['webhooks'] = webhooks
        
        run = self.client.actor(self.actor_id).call(**call_params)
        
        # Handle case where run might be None (if wait_secs was 0)
        if run is None:
            raise RuntimeError(
                "Actor run started but did not complete within wait time. "
                "Set waitForFinish to true or increase timeout."
            )
        
        return {
            'runId': run['id'],
            'status': run['status'],
            'defaultDatasetId': run.get('defaultDatasetId'),
            'defaultKeyValueStoreId': run.get('defaultKeyValueStoreId'),
            'stats': run.get('stats', {}),
            'options': run.get('options', {})
        }
    
    def get_dataset_items(self, dataset_id: str) -> list:
        """
        Get all items from a dataset.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            List of dataset items
        """
        dataset = self.client.dataset(dataset_id)
        return list(dataset.iterate_items())
    
    def get_key_value_store_value(self, store_id: str, key: str = 'OUTPUT') -> Any:
        """
        Get value from key-value store.
        
        Args:
            store_id: Key-value store ID
            key: Key to retrieve (default: 'OUTPUT')
            
        Returns:
            Stored value
        """
        store = self.client.key_value_store(store_id)
        record = store.get_record(key)
        return record['value'] if record else None
    
    def get_run_status(self, run_id: str) -> Dict[str, Any]:
        """
        Get the status of a run.
        
        Args:
            run_id: Run ID
            
        Returns:
            Run status dictionary
        """
        run = self.client.run(run_id).get()
        return {
            'runId': run['id'],
            'status': run['status'],
            'stats': run.get('stats', {}),
            'options': run.get('options', {})
        }
    
    def _build_webhooks(self) -> Optional[list]:
        """Build webhook configuration if webhookUrl is set."""
        webhook_url = self.config.get('webhookUrl')
        if webhook_url:
            return [{
                'eventTypes': ['ACTOR.RUN.SUCCEEDED', 'ACTOR.RUN.FAILED'],
                'requestUrl': webhook_url
            }]
        return None

