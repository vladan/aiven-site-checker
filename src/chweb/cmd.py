"""
A module containing all console script functions.
"""
import argparse
import asyncio
import yaml

from chweb.collector import Collector
from chweb.consumer import Consumer
from chweb.models import Config


def configure() -> Config:
    """
    Gets the configuration and creates a Pydantic model from the parsed YAML.
    """
    parser = argparse.ArgumentParser(
        description='Website availibility checker.')
    parser.add_argument('--config', type=str,
                        default="/etc/checker.yaml",
                        help=('The yaml config file. '
                              'Defaults to /etc/checker.yaml'))
    args = parser.parse_args()
    with open(args.config, 'r') as conf_file:
        config = yaml.load(conf_file, Loader=yaml.FullLoader)
        return Config(**config)


def run(Service):
    """
    Runs a service in an event loop.
    """
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()
    config = configure()
    service = Service(config, loop, queue)
    service.run()


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
