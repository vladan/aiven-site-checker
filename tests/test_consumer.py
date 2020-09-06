import asyncio

import aiokafka
from mock import AsyncMock, Mock, patch
import pytest

from chweb.consumer import Consumer


@pytest.mark.asyncio
@patch('ssl.SSLContext')
async def test_consumer_called(check, config, event_loop):
    consumer = Consumer(config, Mock(), event_loop, Mock())

    consumer.consumer = AsyncMock()
    consumer.db = AsyncMock()

    task = event_loop.create_task(consumer())
    await asyncio.sleep(0)
    consumer.db.setup.assert_called()
    consumer.consumer.start.assert_called()
    task.cancel()
