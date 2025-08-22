"""
Async Event Processor.

This module provides background processing for heavy calculations
and long-running event processing tasks.
"""

import asyncio
import logging
from typing import List, Optional, Callable, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import queue

from src.fund.events.domain.base_event import FundDomainEvent
from src.fund.events.consumption.event_bus import EventBus

logger = logging.getLogger(__name__)


class AsyncEventProcessor:
    """
    Asynchronous event processor for background processing.
    
    This class handles:
    1. Background processing of heavy calculations
    2. Async event publishing and consumption
    3. Thread and process pool management
    4. Queue management for event processing
    """
    
    def __init__(self, max_workers: int = 4, use_process_pool: bool = False):
        """
        Initialize the async event processor.
        
        Args:
            max_workers: Maximum number of worker threads/processes
            use_process_pool: Whether to use ProcessPoolExecutor instead of ThreadPoolExecutor
        """
        self.max_workers = max_workers
        self.use_process_pool = use_process_pool
        
        # Initialize executor
        if use_process_pool:
            self.executor = ProcessPoolExecutor(max_workers=max_workers)
            logger.info(f"Initialized ProcessPoolExecutor with {max_workers} workers")
        else:
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            logger.info(f"Initialized ThreadPoolExecutor with {max_workers} workers")
        
        # Event processing queue
        self.event_queue = queue.Queue()
        
        # Processing statistics
        self._stats = {
            'events_queued': 0,
            'events_processed': 0,
            'events_failed': 0,
            'workers_active': 0,
            'queue_size': 0,
            'last_processed': None
        }
        
        # Processing state
        self._running = False
        self._workers: List[threading.Thread] = []
        
        logger.info(f"Initialized AsyncEventProcessor with {max_workers} workers")
    
    def start(self) -> None:
        """Start the async event processor."""
        if self._running:
            logger.warning("AsyncEventProcessor is already running")
            return
        
        self._running = True
        
        # Start worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"AsyncEventWorker-{i}",
                daemon=True
            )
            worker.start()
            self._workers.append(worker)
        
        logger.info(f"Started AsyncEventProcessor with {self.max_workers} workers")
    
    def stop(self) -> None:
        """Stop the async event processor."""
        if not self._running:
            logger.warning("AsyncEventProcessor is not running")
            return
        
        self._running = False
        
        # Wait for workers to finish
        for worker in self._workers:
            worker.join(timeout=5.0)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Stopped AsyncEventProcessor")
    
    def submit_event(self, event: FundDomainEvent, processor_func: Callable) -> None:
        """
        Submit an event for async processing.
        
        Args:
            event: The domain event to process
            processor_func: Function to process the event
        """
        if not self._running:
            raise RuntimeError("AsyncEventProcessor is not running")
        
        # Add to queue
        self.event_queue.put((event, processor_func))
        self._stats['events_queued'] += 1
        self._stats['queue_size'] = self.event_queue.qsize()
        
        logger.debug(f"Queued event {type(event).__name__} for async processing")
    
    def submit_batch(self, events: List[FundDomainEvent], processor_func: Callable) -> None:
        """
        Submit multiple events for async processing.
        
        Args:
            events: List of domain events to process
            processor_func: Function to process the events
        """
        for event in events:
            self.submit_event(event, processor_func)
    
    def _worker_loop(self) -> None:
        """Main worker loop for processing events."""
        logger.debug(f"Started worker thread: {threading.current_thread().name}")
        
        while self._running:
            try:
                # Get event from queue with timeout
                try:
                    event, processor_func = self.event_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                self._stats['workers_active'] += 1
                self._stats['queue_size'] = self.event_queue.qsize()
                
                try:
                    # Process the event
                    logger.debug(f"Processing event {type(event).__name__} in worker thread")
                    
                    # Submit to executor for actual processing
                    future = self.executor.submit(processor_func, event)
                    
                    # Wait for completion (with timeout)
                    result = future.result(timeout=300)  # 5 minute timeout
                    
                    self._stats['events_processed'] += 1
                    self._stats['last_processed'] = datetime.now()
                    
                    logger.debug(f"Successfully processed event {type(event).__name__} in worker thread")
                    
                except Exception as e:
                    self._stats['events_failed'] += 1
                    logger.error(f"Error processing event {type(event).__name__} in worker thread: {e}")
                
                finally:
                    self._stats['workers_active'] -= 1
                    self.event_queue.task_done()
                    
            except Exception as e:
                logger.error(f"Error in worker thread {threading.current_thread().name}: {e}")
        
        logger.debug(f"Stopped worker thread: {threading.current_thread().name}")
    
    def process_event_async(self, event: FundDomainEvent, processor_func: Callable) -> None:
        """
        Process an event asynchronously using the executor.
        
        Args:
            event: The domain event to process
            processor_func: Function to process the event
        """
        if not self._running:
            raise RuntimeError("AsyncEventProcessor is not running")
        
        future = self.executor.submit(processor_func, event)
        
        # Update statistics
        self._stats['events_queued'] += 1
        
        logger.debug(f"Submitted event {type(event).__name__} for async processing")
        
        return future
    
    def get_stats(self) -> dict:
        """
        Get processing statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        stats = self._stats.copy()
        stats['queue_size'] = self.event_queue.qsize()
        stats['running'] = self._running
        stats['worker_count'] = len(self._workers)
        return stats
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> None:
        """
        Wait for all queued events to complete processing.
        
        Args:
            timeout: Maximum time to wait in seconds
        """
        self.event_queue.join()
        logger.info("All queued events have completed processing")
    
    def clear_queue(self) -> None:
        """Clear all queued events."""
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
                self.event_queue.task_done()
            except queue.Empty:
                break
        
        self._stats['queue_size'] = 0
        logger.info("Cleared event processing queue")
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
