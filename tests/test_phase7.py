"""
Unit tests for Phase 7: Real-Time Progress Streaming & User Experience
"""

import pytest
from datetime import datetime
from src.events.event_emitter import EventEmitter, EventType, EventSeverity
from src.streaming.progress_streamer import ProgressStreamer
from src.streaming.webhook_handler import WebhookHandler


class TestEventEmitter:
    """Test event emitter."""
    
    def test_emitter_initialization(self):
        """Test emitter initialization."""
        emitter = EventEmitter()
        assert len(emitter.listeners) == 0
        assert len(emitter.event_history) == 0
    
    def test_register_listener(self):
        """Test registering event listener."""
        emitter = EventEmitter()
        callback_called = []
        
        def callback(event):
            callback_called.append(event)
        
        emitter.on(EventType.PROGRESS, callback)
        assert EventType.PROGRESS in emitter.listeners
    
    def test_emit_event(self):
        """Test emitting event."""
        emitter = EventEmitter()
        callback_called = []
        
        def callback(event):
            callback_called.append(event)
        
        emitter.on(EventType.PROGRESS, callback)
        emitter.emit(EventType.PROGRESS, {'test': 'data'})
        
        assert len(callback_called) == 1
        assert callback_called[0]['type'] == 'progress'
    
    def test_emit_progress(self):
        """Test emitting progress event."""
        emitter = EventEmitter()
        emitter.emit_progress("test", 50.0, 5, 10, "message")
        
        assert len(emitter.event_history) == 1
        assert emitter.event_history[0]['type'] == 'progress'
    
    def test_emit_status(self):
        """Test emitting status event."""
        emitter = EventEmitter()
        emitter.emit_status("test_status", "test message", EventSeverity.INFO)
        
        assert len(emitter.event_history) == 1
        assert emitter.event_history[0]['type'] == 'status'
    
    def test_get_event_history(self):
        """Test getting event history."""
        emitter = EventEmitter()
        emitter.emit_progress("test", 50.0, 5, 10)
        emitter.emit_status("test", "message")
        
        progress_events = emitter.get_event_history(EventType.PROGRESS)
        assert len(progress_events) == 1
        
        all_events = emitter.get_event_history()
        assert len(all_events) == 2


class TestProgressStreamer:
    """Test progress streamer."""
    
    def test_streamer_initialization(self):
        """Test streamer initialization."""
        streamer = ProgressStreamer()
        assert streamer.start_time is None
    
    def test_start(self):
        """Test starting progress tracking."""
        streamer = ProgressStreamer()
        streamer.start(total_steps=10, operation="test")
        
        assert streamer.start_time is not None
        assert len(streamer.event_emitter.event_history) > 0
    
    def test_update(self):
        """Test updating progress."""
        streamer = ProgressStreamer()
        streamer.start(total_steps=10)
        
        progress_data = streamer.update(
            current_step=5,
            total_steps=10,
            operation="test",
            message="test message"
        )
        
        assert progress_data['progress_percentage'] == 50.0
        assert progress_data['current_step'] == 5
        assert progress_data['total_steps'] == 10
    
    def test_complete(self):
        """Test completing progress."""
        streamer = ProgressStreamer()
        streamer.start(total_steps=10)
        streamer.complete({'status': 'done'})
        
        assert len(streamer.event_emitter.event_history) > 0
    
    def test_error(self):
        """Test error handling."""
        streamer = ProgressStreamer()
        streamer.error("test error", {'context': 'data'})
        
        assert len(streamer.event_emitter.event_history) > 0


class TestWebhookHandler:
    """Test webhook handler."""
    
    def test_handler_initialization(self):
        """Test handler initialization."""
        handler = WebhookHandler()
        assert len(handler.webhook_urls) == 0
    
    def test_add_webhook(self):
        """Test adding webhook URL."""
        handler = WebhookHandler()
        handler.add_webhook("https://example.com/webhook")
        
        assert len(handler.webhook_urls) == 1
        assert "https://example.com/webhook" in handler.webhook_urls
    
    @pytest.mark.asyncio
    async def test_send_webhook_invalid_url(self):
        """Test sending webhook to invalid URL."""
        handler = WebhookHandler()
        # Should handle gracefully
        result = await handler.send_webhook(
            "https://invalid-url-that-does-not-exist-12345.com",
            {'test': 'data'}
        )
        # Should return False after retries
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_to_all_webhooks(self):
        """Test sending to all webhooks."""
        handler = WebhookHandler()
        handler.add_webhook("https://example.com/webhook1")
        
        results = await handler.send_to_all_webhooks({'test': 'data'})
        
        assert results['total'] == 1
        assert 'successful' in results
        assert 'failed' in results


class TestIntegration:
    """Integration tests for Phase 7."""
    
    def test_progress_tracking_workflow(self):
        """Test complete progress tracking workflow."""
        streamer = ProgressStreamer()
        
        streamer.start(total_steps=10, operation="test")
        assert streamer.start_time is not None
        
        for i in range(1, 11):
            progress = streamer.update(
                current_step=i,
                total_steps=10,
                operation="test",
                message=f"Step {i}"
            )
            assert progress['progress_percentage'] == i * 10
        
        streamer.complete({'status': 'done'})
        assert len(streamer.event_emitter.event_history) > 0
    
    def test_event_listener_workflow(self):
        """Test event listener workflow."""
        emitter = EventEmitter()
        events_received = []
        
        def listener(event):
            events_received.append(event)
        
        emitter.on(EventType.PROGRESS, listener)
        emitter.emit_progress("test", 50.0, 5, 10)
        
        assert len(events_received) == 1
        assert events_received[0]['type'] == 'progress'



