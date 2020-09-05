"""
Sample consumer.
"""
import asyncio
import json
import logging
from typing import Optional

import aiokafka  # type: ignore
import asyncpg  # type: ignore

from chweb.base import Service
from chweb.models import Check, Config, PostgresConfig


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
        self.db = Db(self.loop, self.logger, self.config.postgres)
        self.consumer = aiokafka.AIOKafkaConsumer(
            self.config.kafka.topic,
            loop=self.loop,
            bootstrap_servers=self.config.kafka.servers)

    async def consume(self):
        """
        Consumes messages from a kafka topic and writes them in the database.
        """
        await self.consumer.start()
        try:
            await self.db.setup()
            async for msg in self.consumer:
                # if anything here fails break the loop and exit since it's
                # something out of our control and we don't want to work
                # with broken data
                check = Check(**json.loads(msg.value))
                self.logger.debug(check)
                await self.db.save(check)
        except Exception as exc:
            self.logger.error(exc)
            self.logger.info("Exiting due to previous errors!")
        finally:
            await self.consumer.stop()

    def __call__(self) -> asyncio.Future:
        return self.consume()


class Db:
    """
    Database operations and handy helpers.
    """

    def __init__(self, loop: asyncio.AbstractEventLoop, logger: logging.Logger,
                 pgconf: PostgresConfig):
        self.loop = loop
        self.logger = logger
        # Do a side effect here since without this there's not any point for
        # the application to start. Applies for tests as well.
        self.conn: Optional[asyncpg.Connection] = None
        self.conf = pgconf

    async def setup(self):
        """
        Setup the database, i.e. create the table and set up the indexes.
        """
        self.conn = await asyncpg.connect(
            host=self.conf.dbhost,
            port=self.conf.dbport,
            user=self.conf.dbuser,
            password=self.conf.dbpass,
            database=self.conf.dbname,
            loop=self.loop, timeout=60,
        )
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

    async def save(self, data: Check):
        """
        Writes a single record in the database. This is not very optimal, a
        better way would be to write a batch of status checks at once.
        """
        if self.conn is not None:
            try:
                await self.conn.execute('''
                    INSERT INTO statuses (domain, regex, regex_matches,
                                          request_time, response_time,
                                          status, url)
                    VALUES($1, $2, $3, $4, $5, $6, $7)
                    ''', data.domain, data.regex, data.regex_matches,
                         data.request_time, data.response_time, data.status,
                         data.url)
            except asyncpg.PostgresError as exc:
                self.logger.error("error in query %s", exc)
                raise
