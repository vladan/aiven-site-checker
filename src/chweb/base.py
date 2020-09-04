"""
Base classes used in multiple modules.
"""
import asyncio
import logging

from chweb.models import Config


class Application:
    """
    A base class for applications / services.
    """
    def __init__(self, config: Config,
                 logger: logging.Logger,
                 event_loop: asyncio.AbstractEventLoop,
                 queue: asyncio.Queue):
        self.config = config
        self.logger = logger
        self.loop = event_loop
        self.queue = queue

    def run(self):
        raise NotImplementedError()
