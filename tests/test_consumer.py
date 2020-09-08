import asyncio
import pytest

from mock import AsyncMock, Mock, patch
from chweb.consumer import Consumer


@pytest.mark.asyncio
@patch('ssl.SSLContext')
async def test_consumer_called(check, config, event_loop):
    consumer = Consumer(config, Mock(), event_loop, Mock())

    consumer.consumer = AsyncMock()

    task = event_loop.create_task(consumer())
    await asyncio.sleep(0)
    consumer.consumer.start.assert_called()
    consumer.consumer.__aiter__.assert_called()
    task.cancel()
