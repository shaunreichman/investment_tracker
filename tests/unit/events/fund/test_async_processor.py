"""
Test Async Event Processor.

This module tests the AsyncEventProcessor's specific functionality:
- Thread/process pool management
- Event queue management
- Background processing coordination
- Statistics tracking
- Lifecycle management

**FOCUS**: Only tests AsyncEventProcessor functionality
**RELIANCE**: Other tests cover event handling, domain events, and event bus
"""

import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from src.fund.events.consumption.async_processor import AsyncEventProcessor
from src.fund.events.domain.base_event import FundDomainEvent


class TestAsyncEventProcessor:
    """Test AsyncEventProcessor functionality in isolation."""
    
    def test_initialization_default_thread_pool(self):
        """Test default initialization with ThreadPoolExecutor."""
        processor = AsyncEventProcessor()
        
        assert processor.max_workers == 4
        assert processor.use_process_pool is False
        assert isinstance(processor.executor, ThreadPoolExecutor)
        assert processor._running is False
        assert len(processor._workers) == 0
        assert processor._stats['events_queued'] == 0
        assert processor._stats['events_processed'] == 0
        assert processor._stats['events_failed'] == 0
    
    def test_initialization_custom_workers(self):
        """Test initialization with custom worker count."""
        processor = AsyncEventProcessor(max_workers=8)
        
        assert processor.max_workers == 8
        assert processor.executor._max_workers == 8
    
    def test_initialization_process_pool(self):
        """Test initialization with ProcessPoolExecutor."""
        processor = AsyncEventProcessor(max_workers=2, use_process_pool=True)
        
        assert processor.use_process_pool is True
        assert isinstance(processor.executor, ProcessPoolExecutor)
        assert processor.executor._max_workers == 2
    
    def test_start_stop_lifecycle(self):
        """Test start and stop lifecycle management."""
        processor = AsyncEventProcessor(max_workers=2)
        
        # Test start
        processor.start()
        assert processor._running is True
        assert len(processor._workers) == 2
        
        # Verify worker threads are running
        for worker in processor._workers:
            assert worker.is_alive()
            assert worker.name.startswith("AsyncEventWorker-")
        
        # Test stop
        processor.stop()
        assert processor._running is False
        
        # Verify executor is shutdown
        assert processor.executor._shutdown is True
    
    def test_start_already_running(self):
        """Test start when already running."""
        processor = AsyncEventProcessor(max_workers=1)
        processor.start()
        
        # Try to start again
        processor.start()  # Should log warning but not crash
        
        processor.stop()
    
    def test_stop_not_running(self):
        """Test stop when not running."""
        processor = AsyncEventProcessor(max_workers=1)
        
        # Try to stop when not running
        processor.stop()  # Should log warning but not crash
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with AsyncEventProcessor(max_workers=1) as processor:
            assert processor._running is True
            assert len(processor._workers) == 1
        
        # Should be stopped after context exit
        assert processor._running is False
    
    def test_submit_event_not_running(self):
        """Test submit_event when processor is not running."""
        processor = AsyncEventProcessor(max_workers=1)
        mock_event = Mock(spec=FundDomainEvent)
        mock_processor_func = Mock()
        
        with pytest.raises(RuntimeError, match="AsyncEventProcessor is not running"):
            processor.submit_event(mock_event, mock_processor_func)
    
    def test_submit_event_running(self):
        """Test submit_event when processor is running."""
        processor = AsyncEventProcessor(max_workers=1)
        processor.start()
        
        mock_event = Mock(spec=FundDomainEvent)
        mock_processor_func = Mock()
        
        processor.submit_event(mock_event, mock_processor_func)
        
        # Verify event was queued
        assert processor._stats['events_queued'] == 1
        assert processor._stats['queue_size'] == 1
        
        processor.stop()
    
    def test_submit_batch(self):
        """Test batch event submission."""
        processor = AsyncEventProcessor(max_workers=1)
        processor.start()
        
        mock_events = [Mock(spec=FundDomainEvent) for _ in range(3)]
        mock_processor_func = Mock()
        
        processor.submit_batch(mock_events, mock_processor_func)
        
        # Verify all events were queued
        assert processor._stats['events_queued'] == 3
        assert processor._stats['queue_size'] == 3
        
        processor.stop()
    
    def test_process_event_async(self):
        """Test direct async event processing."""
        processor = AsyncEventProcessor(max_workers=1)
        processor.start()
        
        mock_event = Mock(spec=FundDomainEvent)
        mock_processor_func = Mock()
        
        future = processor.process_event_async(mock_event, mock_processor_func)
        
        # Verify future was returned and event was queued
        assert future is not None
        assert processor._stats['events_queued'] == 1
        
        processor.stop()
    
    def test_get_stats(self):
        """Test statistics retrieval."""
        processor = AsyncEventProcessor(max_workers=2)
        
        # Get stats before starting
        stats = processor.get_stats()
        assert stats['running'] is False
        assert stats['worker_count'] == 0
        assert stats['queue_size'] == 0
        
        # Start and get stats
        processor.start()
        stats = processor.get_stats()
        assert stats['running'] is True
        assert stats['worker_count'] == 2
        
        processor.stop()
    
    def test_clear_queue(self):
        """Test queue clearing functionality."""
        processor = AsyncEventProcessor(max_workers=1)
        processor.start()
        
        # Add some events to queue
        mock_events = [Mock(spec=FundDomainEvent) for _ in range(3)]
        mock_processor_func = Mock()
        
        for event in mock_events:
            processor.submit_event(event, mock_processor_func)
        
        assert processor._stats['queue_size'] == 3
        
        # Clear queue
        processor.clear_queue()
        assert processor._stats['queue_size'] == 0
        
        processor.stop()
    
    def test_wait_for_completion(self):
        """Test waiting for completion functionality."""
        processor = AsyncEventProcessor(max_workers=1)
        processor.start()
        
        # This should not block since queue is empty
        processor.wait_for_completion()
        
        processor.stop()
    
    def test_worker_thread_naming(self):
        """Test worker thread naming convention."""
        processor = AsyncEventProcessor(max_workers=3)
        processor.start()
        
        # Verify worker thread names
        expected_names = ["AsyncEventWorker-0", "AsyncEventWorker-1", "AsyncEventWorker-2"]
        actual_names = [worker.name for worker in processor._workers]
        
        assert actual_names == expected_names
        
        processor.stop()
    
    def test_executor_shutdown_on_stop(self):
        """Test that executor is properly shutdown on stop."""
        processor = AsyncEventProcessor(max_workers=1)
        processor.start()
        
        # Verify executor is running
        assert processor.executor._shutdown is False
        
        processor.stop()
        
        # Verify executor is shutdown
        assert processor.executor._shutdown is True
    
    def test_queue_task_done_called(self):
        """Test that queue.task_done() is called after processing."""
        processor = AsyncEventProcessor(max_workers=1)
        processor.start()
        
        # Mock the queue to track task_done calls
        original_task_done = processor.event_queue.task_done
        task_done_called = False
        
        def mock_task_done():
            nonlocal task_done_called
            task_done_called = True
            original_task_done()
        
        processor.event_queue.task_done = mock_task_done
        
        # Submit an event
        mock_event = Mock(spec=FundDomainEvent)
        mock_processor_func = Mock()
        processor.submit_event(mock_event, mock_processor_func)
        
        # Wait a bit for processing
        time.sleep(0.1)
        
        # Verify task_done was called
        assert task_done_called
        
        processor.stop()
    
    def test_worker_thread_daemon_flag(self):
        """Test that worker threads are created as daemon threads."""
        processor = AsyncEventProcessor(max_workers=1)
        processor.start()
        
        # Verify worker thread is daemon
        assert processor._workers[0].daemon is True
        
        processor.stop()
    
    def test_max_workers_validation(self):
        """Test that max_workers parameter is properly set."""
        test_cases = [1, 4, 8, 16]
        
        for workers in test_cases:
            processor = AsyncEventProcessor(max_workers=workers)
            assert processor.max_workers == workers
            assert processor.executor._max_workers == workers
    
    def test_use_process_pool_flag(self):
        """Test use_process_pool flag setting."""
        # Test thread pool (default)
        processor_thread = AsyncEventProcessor(max_workers=1)
        assert processor_thread.use_process_pool is False
        assert isinstance(processor_thread.executor, ThreadPoolExecutor)
        
        # Test process pool
        processor_process = AsyncEventProcessor(max_workers=1, use_process_pool=True)
        assert processor_process.use_process_pool is True
        assert isinstance(processor_process.executor, ProcessPoolExecutor)
    
    def test_initial_stats_state(self):
        """Test initial statistics state."""
        processor = AsyncEventProcessor(max_workers=1)
        
        expected_stats = {
            'events_queued': 0,
            'events_processed': 0,
            'events_failed': 0,
            'workers_active': 0,
            'queue_size': 0,
            'last_processed': None
        }
        
        for key, expected_value in expected_stats.items():
            assert processor._stats[key] == expected_value
