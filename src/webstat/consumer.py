"""
Sample consumer.
"""
import asyncio
import json
from typing import Any, Dict, List

import aiokafka #  type: ignore
import asyncpg #  type: ignore


class Consumer:
    def __init__(self, config: Dict[str, Any],
                 event_loop: asyncio.AbstractEventLoop,
                 queue: asyncio.Queue):
        self.config = config
        self.loop = event_loop
        self.queue = queue

    async def consume(self):
        """
        Consumes messages from a Kafka topic.
        """
        consumer = aiokafka.AIOKafkaConsumer(
            self.config['kafka_topic'],
            loop=self.loop,
            bootstrap_servers=self.config['kafka_servers'])

        await consumer.start()
        try:
            # Consume messages
            async for msg in consumer:
                self.queue.put_nowait(json.loads(msg.value))
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            await consumer.stop()


    async def save(self, pool, data):
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")

    async def write(self):
        try:
            while True:
                status = await self.queue.get()
                print(status)
        finally:
            print("EXITED!")

    def tasks(self) -> List[asyncio.Task]:
        """
        Creates tasks for reading from the Kafka topic and writing in
        PostgreSQL.
        """
        kafka_consumer = self.loop.create_task(self.consume())
        psql_writer = self.loop.create_task(self.write())
        return [kafka_consumer, psql_writer]
