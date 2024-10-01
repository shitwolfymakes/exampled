import asyncio
import threading
import logging

logger = logging.getLogger(__name__)

class ManagedThread:
    def __init__(self, name):
        self.name = name
        self.should_exit = asyncio.Event()
        self.thread = None
        self.loop = None

    def start(self):
        self.thread = threading.Thread(target=self._run_async_loop)
        self.thread.start()

    def stop(self):
        if self.loop:
            self.loop.call_soon_threadsafe(self.should_exit.set)
        if self.thread:
            self.thread.join()

    def _run_async_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._run())

    async def _run(self):
        logger.info(f"{self.name} is starting")
        try:
            while not self.should_exit.is_set():
                await self.task()
        except Exception as e:
            logger.error(f"{self.name} encountered an error: {e}")
        finally:
            logger.info(f"{self.name} is stopping")

    async def task(self):
        logger.info(f"{self.name} is running")
        await asyncio.sleep(2)
