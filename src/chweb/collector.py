"""
Checks status of web servers and sends them to a configured Kafka topic.
"""
import asyncio
import json
import re
from typing import Optional
from urllib.parse import urlparse

import aiokafka #  type: ignore
import requests

from chweb.models import Config, Check


class Collector:
    """
    A class that contains all methods needed to check the statuses of all
    websites present in the config.
    """
    def __init__(self, config: Config,
                 event_loop: asyncio.AbstractEventLoop,
                 queue: asyncio.Queue):
        self.config = config
        self.loop = event_loop
        self.queue = queue

    async def check(self, url: str, regex: Optional[str]) -> Check:
        """
        Checks the status of a website and optionally matches a regex on the
        response body.

        :param url: The URL of the site that needs to be checked.
        :param regex: An optional regex to match on the response body.
        :returns: A dict ready to be sent to the queue for further processing.
        """
        res = await self.loop.run_in_executor(None, requests.get, url)
        matches = None #  The matches value should be None since the regex can
                       #  be ommited from the config.
        if regex is not None:
            matches = re.search(regex, res.text) is not None
        return Check(
            domain=urlparse(res.url).netloc,
            regex=regex,
            response_time=res.elapsed.microseconds,
            regex_matches=matches,
            status=res.status_code,
            url=res.url,
        )

    async def check_forever(self, site):
        """
        A void function that gets the status of a site and sends it to an
        ``asyncio.Queue`` for further processing (sending to a Kafka topic).

        :param site: A site object from the config.
        """
        while True:
            data = await self.check(site.url, site.regex)
            self.queue.put_nowait(data)
            await asyncio.sleep(site.check_interval)

    async def produce(self):
        """
        Creates and starts an ``aiokafka.AIOKafkaProducer`` and runs a loop that
        reads from the ``queue`` and sends the messages to the topic from the
        ``config``.
        """
        producer = aiokafka.AIOKafkaProducer(
            loop=self.loop,
            bootstrap_servers=self.config.kafka.servers)

        await producer.start()
        try:
            while True:
                check = await self.queue.get()
                msg = bytes(check.json().encode("utf-8"))
                await producer.send_and_wait(self.config.kafka.topic, msg)
        finally:
            await producer.stop()

    def run(self):
        """
        Runs all tasks in the event loop.
        """
        def create_task(site) -> asyncio.Task:
            return self.loop.create_task(self.check_forever(site))
        tasks = list(map(create_task, self.config.sites))
        tasks.append(self.loop.create_task(self.produce()))
        self.loop.run_until_complete(asyncio.gather(*tasks))
