import asyncio
from typing import Optional, List, Dict
from datetime import datetime, timezone

class SearchQueueManager:
    """
    Singleton manager to enforce a FIFO queue for rate searches.
    Since web scraping uses a single virtual display and browser context,
    only one search can be active at a time.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchQueueManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._lock = asyncio.Lock()
        self.active_search_id: Optional[str] = None
        self.active_search_info: Optional[str] = None
        self.queue: List[str] = []
        self.queue_info: Dict[str, str] = {}
        self.search_completion_time: Dict[str, datetime] = {}
        self._initialized = True

    async def enqueue_and_wait(self, search_id: str, search_info: str) -> None:
        """
        Adds a search to the queue and waits until it becomes the active search.
        """
        async with self._lock:
            if search_id not in self.queue and self.active_search_id != search_id:
                self.queue.append(search_id)
                self.queue_info[search_id] = search_info

        # Polling loop to wait for turn
        while True:
            async with self._lock:
                # If no active search and we are first in queue, take the lock
                if self.active_search_id is None and self.queue and self.queue[0] == search_id:
                    self.active_search_id = self.queue.pop(0)
                    self.active_search_info = self.queue_info.pop(search_id, "Unknown Route")
                    return
                # If we are already the active search, proceed
                elif self.active_search_id == search_id:
                    return
            await asyncio.sleep(2)

    async def get_queue_status(self, search_id: str) -> dict:
        """
        Returns the current position of the search in the queue.
        0 means it is the active search. >0 means it is waiting.
        """
        async with self._lock:
            if self.active_search_id == search_id:
                return {
                    "position": 0,
                    "active_search_info": self.active_search_info
                }
            if search_id in self.queue:
                return {
                    "position": self.queue.index(search_id) + 1,
                    "active_search_info": self.active_search_info
                }
            return {
                "position": -1, # Not in queue, might be finished
                "active_search_info": self.active_search_info
            }

    async def release_lock(self, search_id: str) -> bool:
        """
        Releases the lock so the next user can proceed.
        Returns True if a lock was actually released.
        """
        async with self._lock:
            if self.active_search_id == search_id:
                self.active_search_id = None
                self.active_search_info = None
                return True
            # If they cancel while queued
            if search_id in self.queue:
                self.queue.remove(search_id)
                if search_id in self.queue_info:
                    del self.queue_info[search_id]
                return True
        return False

    async def mark_search_completed(self, search_id: str):
        """
        Marks a search as completed internally so we can track the auto-release timeout.
        """
        async with self._lock:
            if self.active_search_id == search_id:
                self.search_completion_time[search_id] = datetime.now(timezone.utc)

    async def auto_release_check(self, search_id: str, timeout_seconds: int = 300) -> bool:
        """
        Called periodically in a background task to check if the user has held the lock
        longer than the timeout since completion.
        """
        async with self._lock:
            if self.active_search_id != search_id:
                return False
            completion_time = self.search_completion_time.get(search_id)
            if not completion_time:
                return False
            
            elapsed = (datetime.now(timezone.utc) - completion_time).total_seconds()
            if elapsed >= timeout_seconds:
                # Force release
                self.active_search_id = None
                self.active_search_info = None
                del self.search_completion_time[search_id]
                return True
        return False

# Global instance
queue_manager = SearchQueueManager()
