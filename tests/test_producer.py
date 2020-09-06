import asyncio

import aiokafka
from mock import Mock, AsyncMock
import pytest

from chweb.collector import Producer


@pytest.mark.asyncio
async def test_producer_called(check, config, event_loop):
    queue = asyncio.Queue()
    producer = Producer(config, Mock(), event_loop, queue)
    await queue.put(check)

    producer.producer = AsyncMock()

    task = event_loop.create_task(producer())
    await asyncio.sleep(0)
    producer.producer.send_and_wait.assert_called_with(
        config.kafka.topic, bytes(check.json().encode('utf-8')))
    task.cancel()


@pytest.mark.asyncio
async def test_producer_called_invalid(config, event_loop):
    queue = asyncio.Queue()
    producer = Producer(config, Mock(), event_loop, queue)
    await queue.put('')

    producer.producer = AsyncMock()

    task = event_loop.create_task(producer())
    await asyncio.sleep(0)
    producer.logger.error.assert_called()
    assert task.done()
