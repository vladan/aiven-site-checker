"""
A module containing all console script functions.
"""
import argparse
import asyncio
import logging
import logging.config
from logging import Logger
from typing import Tuple
import os
import yaml

from chweb.collector import Collector, Producer
from chweb.consumer import Consumer
from chweb.models import Config


def configure(name) -> Tuple[Config, Logger]:
    """
    Gets the configuration and creates a Pydantic model from the parsed YAML.
    """
    parser = argparse.ArgumentParser(
        description='Website availibility checker.')
    parser.add_argument('-c', '--config', type=str,
                        default="/etc/checker.yaml",
                        help=('The yaml config file. '
                              'Defaults to /etc/checker.yaml'))
    args = parser.parse_args()

    kafka_servers_env = os.getenv('KAFKA_SERVERS')
    if kafka_servers_env is not None:
        kafka_servers = kafka_servers_env.split(',')

    kafka_topic = os.getenv('KAFKA_TOPIC')

    pg_db = os.getenv('POSTGRES_DB')
    pg_host = os.getenv('POSTGRES_HOST')
    pg_port = os.getenv('POSTGRES_PORT')
    pg_user = os.getenv('POSTGRES_USER')
    pg_pass = os.getenv('POSTGRES_PASS')

    with open(args.config, 'r') as conf_file:
        config = yaml.load(conf_file, Loader=yaml.FullLoader)
        logging.config.dictConfig(config['logging'])

        config = Config(**config)
        config.kafka.servers = (kafka_servers if kafka_servers_env
                                              else config.kafka.servers)
        config.kafka.topic = kafka_topic or config.kafka.topic
        config.postgres.dbhost = pg_host or config.postgres.dbhost
        config.postgres.dbname = pg_db or config.postgres.dbname
        config.postgres.dbport = pg_port or config.postgres.dbport
        config.postgres.dbuser = pg_user or config.postgres.dbuser
        config.postgres.dbpass = pg_pass or config.postgres.dbpass

        logger = logging.getLogger("chweb.{}".format(name))
        print(config)
        return (config, logger)


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
