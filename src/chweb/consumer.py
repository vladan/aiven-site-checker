"""
Sample consumer.
"""
import asyncio
import json
import logging
import ssl
from typing import Optional

import aiokafka  # type: ignore
from aiokafka.helpers import create_ssl_context  # type: ignore
import asyncpg  # type: ignore

from chweb.base import Service
from chweb.models import Check, Config


class Consumer(Service):
    """
    Consumes messages from the kafka topic and if they are correct, i.e. if
    they can be serialized in a :class:`chweb.models.Check` object, then they
    are saved in the database.
    """

    def __init__(self, config: Config,
                 logger: logging.Logger,
                 event_loop: asyncio.AbstractEventLoop,
                 queue: asyncio.Queue):
        super().__init__(config, logger, event_loop, queue)
        context = create_ssl_context(
            cafile=self.config.kafka.cafile,
            certfile=self.config.kafka.cert,
            keyfile=self.config.kafka.key,
            password=self.config.kafka.passwd,
        )
        self.consumer = aiokafka.AIOKafkaConsumer(
            self.config.kafka.topic,
            loop=self.loop,
            bootstrap_servers=self.config.kafka.servers,
            security_protocol="SSL",
            ssl_context=context,
        )

    async def consume(self):
        """
        Consumes messages from a kafka topic and writes them in the database.
        """
        await self.consumer.start()
        try:
            async for msg in self.consumer:
                # if anything here fails break the loop and exit since it's
                # something out of our control and we don't want to work
                # with broken data
                check = Check(**json.loads(msg.value))
                self.logger.debug(check)
                self.queue.put_nowait(check)
        except Exception as exc:
            self.logger.exception(exc)
            self.logger.info("Exiting due to previous errors!")
        finally:
            await self.consumer.stop()

    def __call__(self) -> asyncio.Future:
        return self.consume()


class DbWriter(Service):
    """
    Database operations and handy helpers.
    """

    def __init__(self, config: Config,
                 logger: logging.Logger,
                 event_loop: asyncio.AbstractEventLoop,
                 queue: asyncio.Queue):
        super().__init__(config, logger, event_loop, queue)
        self.conn: Optional[asyncpg.Connection] = None

    async def connect(self):
        """
        Connects to the database and stores the connection in ``self.conn``.
        """
        try:
            self.conn = await asyncpg.connect(
                host=self.config.postgres.dbhost,
                port=self.config.postgres.dbport,
                user=self.config.postgres.dbuser,
                password=self.config.postgres.dbpass,
                database=self.config.postgres.dbname,
                loop=self.loop, timeout=60,
                ssl=ssl.create_default_context(
                    cafile=self.config.postgres.dbcert),
            )
        except (OSError, asyncio.TimeoutError, ConnectionError) as exc:
            self.logger.error(exc)
            raise

    async def setup(self):
        """
        Setup the database, i.e. create the table and set up the indexes.
        """
        await self.connect()
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS statuses(
                id SERIAL PRIMARY KEY,
                domain TEXT NOT NULL,
                regex TEXT NULL,
                regex_matches BOOLEAN NULL,
                request_time TIMESTAMP NOT NULL,
                response_time INTEGER NOT NULL,
                status INTEGER NOT NULL,
                url text NOT NULL
            );
            CREATE INDEX IF NOT EXISTS
            statuses_domain ON statuses(domain);
            CREATE INDEX IF NOT EXISTS
            statuses_status ON statuses(status);
            CREATE INDEX IF NOT EXISTS
            statuses_request_time ON statuses(request_time);
            CREATE INDEX IF NOT EXISTS
            statuses_response_time ON statuses(response_time);
            CREATE INDEX IF NOT EXISTS
            statuses_regex_matches ON statuses(regex_matches);
            ''')

    async def write(self):
        """
        Writes a batch of records to the databse. The size in the batch is
        defined in ``chweb.models.PostgresConfig.batch_size``.
        """
        await self.setup()

        batch = []
        while True:
            if len(batch) < self.config.postgres.batch_size:
                check = await self.queue.get()
                batch.append(check)
            else:
                records = [(c.domain, c.regex, c.regex_matches, c.request_time,
                            c.response_time, c.status, c.url) for c in batch]
                columns = ["domain", "regex", "regex_matches", "request_time",
                           "response_time", "status", "url"]
                try:
                    result = await self.conn.copy_records_to_table(
                        "statuses", records=records, columns=columns)
                    self.logger.info(("Inserted %d records in the database "
                                      "with result %s"), len(records), result)
                except Exception as exc:
                    self.logger.error("error in query %s", exc)
                    raise
                batch = []

    def __call__(self) -> asyncio.Future:
        return self.write()
