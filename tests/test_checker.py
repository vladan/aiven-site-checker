"""
All tests fot the ``chweb.checker`` module.
"""
import asyncio
from mock import Mock

import pytest
import requests

from chweb.collector import Collector


@pytest.mark.asyncio
async def test_valid_site_200(config, event_loop):
    queue = asyncio.Queue()
    coll = Collector(config, Mock(), event_loop, queue)
    check = await coll.check('https://example.com', None)
    assert check.domain == 'example.com'
    assert check.regex_matches is None
    assert check.status == 200
    assert check.response_time > 0


@pytest.mark.asyncio
async def test_valid_site_404(config, event_loop):
    queue = asyncio.Queue()
    coll = Collector(config, Mock(), event_loop, queue)
    check = await coll.check('https://example.com/404', None)
    assert check.domain == 'example.com'
    assert check.regex_matches is None
    assert check.status == 404
    assert check.response_time > 0


@pytest.mark.asyncio
async def test_invalid_site(config, event_loop):
    queue = asyncio.Queue()
    coll = Collector(config, Mock(), event_loop, queue)
    with pytest.raises(requests.exceptions.ConnectionError):
        _ = await coll.check('https://non.existant.domain.noooo', None)


@pytest.mark.asyncio
async def test_check_forever_valid(config, event_loop):
    """
    The :meth:`chweb.collector.Collector.check_forever` method runs an infinite
    loop, so we'll test if it's running for 2s and assume it's ok.
    """
    queue = asyncio.Queue()
    coll = Collector(config, Mock(), event_loop, queue)
    task = event_loop.create_task(coll.check_forever(config.sites[0]))
    await asyncio.sleep(2)
    assert not task.done()
    task.cancel()


@pytest.mark.asyncio
async def test_check_forever_invalid(config_invalid, event_loop):
    """
    The :meth:`chweb.collector.Collector.check_forever` method cancels the Task
    on error, so if we get an invalid site, the task should be done.
    """
    queue = asyncio.Queue()
    coll = Collector(config_invalid, Mock(), event_loop, queue)
    task = event_loop.create_task(coll.check_forever(config_invalid.sites[0]))
    await asyncio.sleep(1)
    assert task.done()
