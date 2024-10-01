import asyncio
from .managed_thread import ManagedThread
import logging

logger = logging.getLogger(__name__)

class ThreadManager:
    def __init__(self):
        self.threads = {}

    def start_threads(self):
        for thread in self.threads.values():
            thread.start()

    async def stop_threads(self):
        stop_coroutines = []
        for thread in self.threads.values():
            thread.stop()
            stop_coroutines.append(asyncio.to_thread(thread.thread.join))
        await asyncio.gather(*stop_coroutines)

    def signal_stop_all(self):
        for thread in self.threads.values():
            if thread.loop:
                thread.loop.call_soon_threadsafe(thread.should_exit.set)

    def add_thread(self, name):
        if name in self.threads:
            logger.warning(f"Thread {name} already exists. Not adding.")
            return False
        
        new_thread = ManagedThread(name)
        self.threads[name] = new_thread
        new_thread.start()
        logger.info(f"Added and started new thread: {name}")
        return True

    async def remove_thread(self, name):
        if name not in self.threads:
            logger.warning(f"Thread {name} does not exist. Cannot remove.")
            return False
        
        thread = self.threads[name]
        thread.stop()
        await asyncio.to_thread(thread.thread.join)
        del self.threads[name]
        logger.info(f"Removed thread: {name}")
        return True

    def get_thread_names(self):
        return list(self.threads.keys())

    def get_thread_count(self):
        return len(self.threads)
