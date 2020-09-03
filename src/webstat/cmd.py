"""
A module containing all console script functions.
"""
import asyncio
import yaml

from webstat.collector import Collector
from webstat.consumer import Consumer


def run(Service):
    """
    A factory kinda that runs both services in an event loop.
    """
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()
    with open('config.yaml', 'r') as conf_file:
        config = yaml.load(conf_file, Loader=yaml.FullLoader)
    tasks = Service(config, loop, queue).tasks()
    loop.run_until_complete(asyncio.gather(*tasks))


def collect():
    """
    Main producer event loop.
    """
    run(Collector)


def consume():
    """
    Main consumer event loop.
    """
    run(Consumer)
