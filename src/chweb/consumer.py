"""
Sample consumer.
"""
import asyncio
import json
import logging
from typing import Any, Dict

import aiokafka #  type: ignore
import asyncpg #  type: ignore

from chweb.base import Service
from chweb.models import Check


class Consumer(Service):
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
            # Consume messages from the kafka topic.
            async for msg in consumer:
                check_info = Check(**json.loads(msg.value))
                self.queue.put_nowait(check_info)
                self.logger.info(check_info)
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await consumer.stop()

    def __call__(self) -> asyncio.Future:
        return self.consume()


class Db:
    async def consume_and_save(self):
        try:
            while True:
                status = await self.queue.get()
                yield status
        finally:
            self.logger.info("Queue reader stopped.")
