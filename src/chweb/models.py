# pylint: disable=too-few-public-methods
"""
Schemas that are used in all modules. This module contains classes for:

- Configuring the :class:`chweb.collector.Collector`.
- Configuring the :class:`chweb.consumer.Consumer`.
- The schema for the stats being sent in the Kafka topic.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Check(BaseModel):
    """
    Information for a website check request.
    """
    domain: str
    regex: Optional[str] = None
    regex_matches: Optional[bool] = None
    request_time: datetime = datetime.now()
    response_time: int
    status: int
    url: str

    class Config:
        extra = "forbid"


class KafkaConfig(BaseModel):
    """
    Kafka broker configuration.
    """
    servers: List[str] = []
    topic: str
    cafile: str
    cert: str
    key: str
    passwd: str


class PostgresConfig(BaseModel):
    """
    PostgreSQL server configuration.
    """
    dbhost: str = "localhost"
    dbport: int = 5432
    dbname: str = "chweb"
    dbuser: str = "vladan"
    dbpass: str = ""
    dbcert: str = ""


class SiteConfig(BaseModel):
    """
    Single website configuration.
    """
    url: str = "https://example.com"
    regex: Optional[str] = None
    check_interval: int


class Config(BaseModel):
    """
    Main application configuration. Same for the checker and the kafka
    consumer / postgres writer for simplicity while deploying.
    """
    kafka: KafkaConfig
    postgres: PostgresConfig
    sites: List[SiteConfig] = []
