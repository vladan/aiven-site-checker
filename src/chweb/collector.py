"""
Checks status of web servers and sends them to a configured Kafka topic.
"""
import asyncio
import logging
import re
from typing import Optional
from urllib.parse import urlparse

import aiokafka  # type: ignore
import requests
from requests import exceptions as rqexc

from chweb.base import Service
from chweb.models import Check, Config, SiteConfig


class Collector(Service):
    """
    A class that contains all methods needed to check the statuses of all
    websites present in the config.
    """
    async def check(self, url: str, regex: Optional[str]) -> Check:
        """
        Checks the status of a website and optionally matches a regex on the
        response body.

        :param url: The URL of the site that needs to be checked.
        :param regex: An optional regex to match on the response body.
        :returns: ``chweb.models.Check``, sent to a queue in
                  ``chweb.collector.Collector.check_forever``.
        """
        res = await self.loop.run_in_executor(None, requests.get, url)
        # Should be treated as nullable since the regex can be ommited from the
        # config.
        matches = None
        if regex is not None:
            matches = re.search(regex, res.text) is not None
        return Check(
            domain=urlparse(res.url).netloc,
            regex=regex,
            response_time=res.elapsed.microseconds,
            regex_matches=matches,
            status=res.status_code,
            url=url,
        )

    async def check_forever(self, site: SiteConfig):
        """
        A void function that checks the status of a site and sends the result
        in an :class:`asyncio.Queue` for further processing, i.e. the check
        info is sent to a Kafka topic in
        :meth:`chweb.collector.Producer.produce` (as in produce data for the
        Kafka consumers, defined in :class:`chweb.consumer.Consumer.consume`.

        :param site: A :py:class:`chweb.models.SiteConfig` object from the
                     config.
        """
        while True:
            try:
                data = await self.check(site.url, site.regex)
            except rqexc.ConnectionError as exc:
                errmsg = "{}; {}".format(site.url, exc)
                self.logger.error(errmsg)
                break  # Break the loop and destroy the Task.
            self.queue.put_nowait(data)
            await asyncio.sleep(site.check_interval)

    def __call__(self) -> asyncio.Future:
        def create_task(site) -> asyncio.Task:
            return self.loop.create_task(self.check_forever(site))
        tasks = map(create_task, self.config.sites)
        return asyncio.gather(*tasks)


class Producer(Service):
    """
    Kafka producer.

    Reads checks from the queue written by :class:`chweb.collector.Collector`
    and sends all messages in a kafka topic.
    """

    def __init__(self, config: Config,
                 logger: logging.Logger,
                 event_loop: asyncio.AbstractEventLoop,
                 queue: asyncio.Queue):
        super().__init__(config, logger, event_loop, queue)
        self.producer = aiokafka.AIOKafkaProducer(
            loop=self.loop,
            bootstrap_servers=self.config.kafka.servers)

    async def produce(self):
        """
        Creates and starts an ``aiokafka.AIOKafkaProducer`` and runs a loop
        that reads from the queue and sends the messages to the topic defined
        in the config.
        """
        await self.producer.start()
        try:
            while True:
                check = await self.queue.get()
                msg = bytes(check.json().encode("utf-8"))
                self.logger.debug(check)
                await self.producer.send_and_wait(self.config.kafka.topic, msg)
        except Exception as exc:
            self.logger.error(exc)
        finally:
            self.logger.warning("Kafka producer destroyed!")
            await self.producer.stop()

    def __call__(self) -> asyncio.Future:
        return self.produce()
