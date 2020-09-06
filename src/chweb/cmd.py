"""
A module containing all console script functions.
"""
import asyncio

from chweb.collector import Collector, Producer
from chweb.consumer import Consumer
from chweb.config import configure


def collect():
    """
    Main producer event loop.
    """
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    config, logger = configure("collector")
    logger.info("Starting collector for %d sites.", len(config.sites))
    collector = Collector(config, logger, loop, queue)
    logger.info(("Starting kafka producer on kafka [cluster]/topic: "
                 "%s/%s"), config.kafka.servers, config.kafka.topic)
    producer = Producer(config, logger, loop, queue)
    loop.run_until_complete(asyncio.gather(collector(), producer()))


def consume():
    """
    Main consumer event loop.
    """
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    config, logger = configure("consumer")
    logger.info(("Starting kafka consumer on kafka [cluster]/topic: "
                 "%s/%s"), config.kafka.servers, config.kafka.topic)
    consumer = Consumer(config, logger, loop, queue)
    loop.run_until_complete(consumer())
