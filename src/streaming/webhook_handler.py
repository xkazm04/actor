"""
Webhook Handler - Sends progress updates to webhook URLs.
Implements retry logic and supports multiple destinations.
"""

import asyncio
import aiohttp
from typing import List, Optional, Dict
from datetime import datetime
from apify import Actor

from src.events.event_emitter import EventEmitter, EventType, get_event_emitter


class WebhookHandler:
    """
    Handles webhook delivery for progress updates and completion notifications.
    """
    
    def __init__(self, webhook_urls: Optional[List[str]] = None, event_emitter: Optional[EventEmitter] = None):
        """
        Initialize webhook handler.
        
        Args:
            webhook_urls: List of webhook URLs (optional)
            event_emitter: Event emitter instance (optional)
        """
        self.webhook_urls = webhook_urls or []
        self.event_emitter = event_emitter or get_event_emitter()
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        
        # Register event listeners
        self.event_emitter.on(EventType.PROGRESS, self._on_progress)
        self.event_emitter.on(EventType.COMPLETION, self._on_completion)
        self.event_emitter.on(EventType.ERROR, self._on_error)
    
    def add_webhook(self, url: str):
        """
        Add webhook URL.
        
        Args:
            url: Webhook URL
        """
        if url and url not in self.webhook_urls:
            self.webhook_urls.append(url)
            Actor.log.info(f"Added webhook: {url}")
    
    async def send_webhook(
        self,
        url: str,
        payload: Dict,
        retry_count: int = 0
    ) -> bool:
        """
        Send webhook with retry logic.
        
        Args:
            url: Webhook URL
            payload: Payload to send
            retry_count: Current retry attempt
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status in [200, 201, 202, 204]:
                        Actor.log.debug(f"Webhook delivered successfully to {url}")
                        return True
                    else:
                        Actor.log.warning(f"Webhook returned status {response.status} from {url}")
                        return False
        
        except asyncio.TimeoutError:
            Actor.log.warning(f"Webhook timeout for {url}")
        except Exception as e:
            Actor.log.warning(f"Webhook delivery failed for {url}: {e}")
        
        # Retry if not exceeded max retries
        if retry_count < self.max_retries:
            await asyncio.sleep(self.retry_delay * (2 ** retry_count))  # Exponential backoff
            return await self.send_webhook(url, payload, retry_count + 1)
        
        return False
    
    async def send_to_all_webhooks(self, payload: Dict) -> Dict:
        """
        Send payload to all webhook URLs.
        
        Args:
            payload: Payload to send
            
        Returns:
            Dictionary with delivery results
        """
        results = {
            'total': len(self.webhook_urls),
            'successful': 0,
            'failed': 0,
            'results': []
        }
        
        for url in self.webhook_urls:
            success = await self.send_webhook(url, payload)
            results['results'].append({
                'url': url,
                'success': success
            })
            if success:
                results['successful'] += 1
            else:
                results['failed'] += 1
        
        return results
    
    def _on_progress(self, event: Dict):
        """Handle progress event."""
        if self.webhook_urls:
            # Send progress update asynchronously
            asyncio.create_task(self.send_to_all_webhooks({
                'event_type': 'progress',
                'timestamp': event['timestamp'],
                'data': event['data']
            }))
    
    def _on_completion(self, event: Dict):
        """Handle completion event."""
        if self.webhook_urls:
            # Send completion notification
            asyncio.create_task(self.send_to_all_webhooks({
                'event_type': 'completion',
                'timestamp': event['timestamp'],
                'data': event['data']
            }))
    
    def _on_error(self, event: Dict):
        """Handle error event."""
        if self.webhook_urls:
            # Send error notification
            asyncio.create_task(self.send_to_all_webhooks({
                'event_type': 'error',
                'timestamp': event['timestamp'],
                'data': event['data']
            }))


def create_webhook_handler(webhook_urls: Optional[List[str]] = None) -> WebhookHandler:
    """
    Create a webhook handler instance.
    
    Args:
        webhook_urls: List of webhook URLs
        
    Returns:
        WebhookHandler instance
    """
    return WebhookHandler(webhook_urls)



