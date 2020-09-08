import asyncio

import pytest
from mock import AsyncMock, Mock

import chweb.consumer
from chweb.consumer import DbWriter


@pytest.mark.asyncio
async def test_db_setup(three_checks, config, event_loop):
    queue = asyncio.Queue()
    db_writer = DbWriter(config, Mock(), event_loop, queue)
    assert db_writer.conn is None

    chweb.consumer.asyncpg = AsyncMock()
    await db_writer.connect()
    chweb.consumer.asyncpg.connect.assert_called()

    db_writer.conn = AsyncMock()
    await db_writer.setup()
    db_writer.conn.execute.assert_called()

    for check in three_checks:
        await queue.put(check)
    print("&&&&&&&&&&")
    print("&&&&&&&&&&")
    print("&&&&&&&&&&")
    print(queue.qsize())
    print(config.postgres.batch_size)
    print("&&&&&&&&&&")
    print("&&&&&&&&&&")
    print("&&&&&&&&&&")
    task = event_loop.create_task(db_writer())
    await asyncio.sleep(0.5)
    db_writer.conn.copy_records_to_table.assert_called()
    task.cancel()
