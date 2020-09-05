import asyncio

import aiokafka
from mock import Mock
import pytest

from chweb.collector import Producer
from chweb.models import Check


@pytest.mark.asyncio
async def test_producer_called(config, event_loop):
    queue = asyncio.Queue()
    producer = Producer(config, Mock(), event_loop, queue)
    check = Check()
    await queue.put(check)

    async def async_patch():
        pass
    Mock.__await__ = lambda x: async_patch().__await__()

    producer.producer = Mock()

    task = event_loop.create_task(producer())
    await asyncio.sleep(0)
    producer.producer.send_and_wait.assert_called_with(
        config.kafka.topic, bytes(check.json().encode('utf-8')))
    task.cancel()


@pytest.mark.asyncio
async def test_producer_called_invalid(config, event_loop):
    queue = asyncio.Queue()
    producer = Producer(config, Mock(), event_loop, queue)
    check = Check()
    await queue.put('')

    async def async_patch():
        pass
    Mock.__await__ = lambda x: async_patch().__await__()

    producer.producer = Mock()

    task = event_loop.create_task(producer())
    await asyncio.sleep(0)
    producer.logger.error.assert_called()
    assert task.done()
