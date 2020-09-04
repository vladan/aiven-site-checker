"""
Sample consumer.
"""
import asyncio
import json
from typing import Any, Dict

import aiokafka #  type: ignore
import asyncpg #  type: ignore

from chweb.models import Check


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
            self.config.kafka.topic,
            loop=self.loop,
            bootstrap_servers=self.config.kafka.servers)

        await consumer.start()
        try:
            # Consume messages
            async for msg in consumer:
                self.queue.put_nowait(Check(**json.loads(msg.value)))
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

    def run(self):
        """
        Runs all tasks in the event loop.
        """
        tasks = [
            self.loop.create_task(self.consume()),
            self.loop.create_task(self.write()),
        ]
        self.loop.run_until_complete(asyncio.gather(*tasks))
