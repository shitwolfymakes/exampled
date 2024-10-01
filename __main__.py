import asyncio
import signal

from exampled import Daemon

def main():
    daemon = Daemon()

    # Set up signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(sig, daemon.signal_handler)

    try:
        asyncio.get_event_loop().run_until_complete(daemon.run())
    finally:
        asyncio.get_event_loop().close()

if __name__ == "__main__":
    main()