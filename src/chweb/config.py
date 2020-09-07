"""
A module containing all console script functions.
"""
import argparse
import logging
import logging.config
from logging import Logger
from typing import Any, Dict, Tuple
import os
import yaml

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

    with open(args.config, 'r') as conf_file:
        conf = yaml.load(conf_file, Loader=yaml.FullLoader)
        logging.config.dictConfig(conf['logging'])

        config = create_config(conf)
        logger = logging.getLogger("chweb.{}".format(name))
        return (config, logger)


def create_config(conf: Dict[str, Any]):
    kafka_servers_env = os.getenv('KAFKA_SERVERS')
    if kafka_servers_env is not None:
        kafka_servers = kafka_servers_env.split(',')

    kafka_topic = os.getenv('KAFKA_TOPIC')
    kafka_cafile = os.getenv('KAFKA_CA_FILE')
    kafka_cert = os.getenv('KAFKA_CERT')
    kafka_key = os.getenv('KAFKA_KEY')
    kafka_pass = os.getenv('KAFKA_PASS')

    pg_db = os.getenv('POSTGRES_DB')
    pg_host = os.getenv('POSTGRES_HOST')
    pg_port = os.getenv('POSTGRES_PORT')
    pg_user = os.getenv('POSTGRES_USER')
    pg_pass = os.getenv('POSTGRES_PASS')
    pg_cert = os.getenv('POSTGRES_CERT')

    config = Config(**conf)
    config.kafka.servers = (kafka_servers if kafka_servers_env
                            else config.kafka.servers)
    config.kafka.topic = kafka_topic or config.kafka.topic
    config.kafka.cafile = kafka_cafile or config.kafka.cafile
    config.kafka.cert = kafka_cert or config.kafka.cert
    config.kafka.key = kafka_key or config.kafka.key
    config.kafka.passwd = kafka_pass or config.kafka.passwd

    config.postgres.dbhost = pg_host or config.postgres.dbhost
    config.postgres.dbname = pg_db or config.postgres.dbname
    config.postgres.dbport = (int(pg_port) if pg_port is not None
                              else config.postgres.dbport)
    config.postgres.dbuser = pg_user or config.postgres.dbuser
    config.postgres.dbpass = pg_pass or config.postgres.dbpass
    config.postgres.dbcert = pg_cert or config.postgres.dbcert

    return config
