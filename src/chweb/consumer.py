"""
Sample consumer.
"""
import asyncio
import json
import logging
import time
from typing import Any, Dict, Optional

import aiokafka  # type: ignore
import asyncpg  # type: ignore

from chweb.base import Service
from chweb.models import Check, PostgresConfig


class Consumer(Service):
    @property
    def db(self):
        return Db(self.loop, self.logger, self.config.postgres)

    async def consume(self):
        """
        Consumes messages from a kafka topic and writes them in the database.
        """
        consumer = aiokafka.AIOKafkaConsumer(
            self.config.kafka.topic,
            loop=self.loop,
            bootstrap_servers=self.config.kafka.servers)

        await consumer.start()
        try:
            async with self.db as db:
                await db.setup()
                async for msg in consumer:
                    try:
                        check = Check(**json.loads(msg.value))
                        self.queue.put_nowait(check)
                        self.logger.debug(check)
                        await db.save(check)
                    except Exception as exc:
                        err = "error processing message %s; failed with %s"
                        self.logger.error(err, msg, exc)
        finally:
            await consumer.stop()

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

    async def __aenter__(self):
        self.conn = await asyncpg.connect(
            host=self.conf.dbhost,
            port=self.conf.dbport,
            user=self.conf.dbuser,
            password=self.conf.dbpass,
            database=self.conf.dbname,
            loop=self.loop, timeout=60,
        )
        return self

    async def __aexit__(self, type_, value, traceback):
        await self.conn.close()

    async def setup(self):
        """
        Setup the database, i.e. create the table and set up the indexes.
        """
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
