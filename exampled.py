import asyncio
import signal
import logging
from .thread_manager import ThreadManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Daemon:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.should_exit = asyncio.Event()
        self.thread_manager = ThreadManager()

    async def run(self):
        # Start asyncio tasks
        tasks = [
            self.loop.create_task(self.async_task("Async Task 1")),
            self.loop.create_task(self.async_task("Async Task 2")),
        ]

        # Add initial threads
        self.thread_manager.add_thread("Thread 1")
        self.thread_manager.add_thread("Thread 2")

        # Start dynamic thread management
        dynamic_management_task = self.loop.create_task(self.dynamic_thread_management())

        # Wait for shutdown signal
        await self.should_exit.wait()

        # Cancel asyncio tasks
        for task in tasks + [dynamic_management_task]:
            task.cancel()
        await asyncio.gather(*tasks, dynamic_management_task, return_exceptions=True)

        # Stop threads asynchronously
        await self.thread_manager.stop_threads()

        logger.info("Daemon shutdown complete")

    async def dynamic_thread_management(self):
        try:
            while not self.should_exit.is_set():
                # Log current thread status
                logger.info(f"Current threads: {self.thread_manager.get_thread_names()}")
                logger.info(f"Thread count: {self.thread_manager.get_thread_count()}")

                # Add a new thread
                if self.thread_manager.get_thread_count() < 4:
                    new_thread_name = f"Dynamic Thread {self.thread_manager.get_thread_count() + 1}"
                    self.thread_manager.add_thread(new_thread_name)
                    logger.info(f"Added new thread: {new_thread_name}")
                
                # Remove a thread if we have more than 2
                elif self.thread_manager.get_thread_count() > 2:
                    thread_to_remove = self.thread_manager.get_thread_names()[-1]
                    await self.thread_manager.remove_thread(thread_to_remove)
                    logger.info(f"Removed thread: {thread_to_remove}")

                # Wait before next management cycle
                await asyncio.sleep(10)
        except asyncio.CancelledError:
            logger.info("Dynamic thread management cancelled")

    async def async_task(self, name):
        try:
            while not self.should_exit.is_set():
                logger.info(f"{name} is running")
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info(f"{name} was cancelled")

    def signal_handler(self):
        logger.info("Received shutdown signal")
        self.should_exit.set()
        self.thread_manager.signal_stop_all()

if __name__ == "__main__":
    daemon = Daemon()
    for sig in (signal.SIGINT, signal.SIGTERM):
        daemon.loop.add_signal_handler(sig, daemon.signal_handler)
    daemon.loop.run_until_complete(daemon.run())
