import asyncio
import pytest
from chweb.config import create_config
from chweb.models import Check


@pytest.fixture()
def config():
    config_dict = {
        'kafka': {
            'servers': ["localhost:9992"],
            'topic': "sample",
            'cafile': "/dev/null",
            'cert': "/dev/null",
            'key': "/dev/null",
            'passwd': "",
        },
        'postgres': {
            'dbhost': "localhost",
            'dbport': 5432,
            'dbname': "chweb",
            'dbuser': "vladan",
            'dbpass': "",
            'batch_size': 3,
        },
        'sites': [{
            'url': "https://example.com",
            'regex': "aaaaaaaaaaaaa",
            'check_interval': 8,
        },
        ]
    }
    return create_config(config_dict)


@pytest.fixture
def config_invalid():
    config_dict = {
        'kafka': {
            'servers': ["localhost:9992"],
            'topic': "sample",
            'cafile': "",
            'cert': "",
            'key': "",
            'passwd': "",
        },
        'postgres': {
            'dbhost': "localhost",
            'dbport': 5432,
            'dbname': "chweb",
            'dbuser': "vladan",
            'dbpass': "",
            'dbcert': "",
        },
        'sites': [{
            'url': "https://dsadakjhkjsahkjh.com",
            'regex': "domain",
            'check_interval': 5,
        },
        ]
    }
    return create_config(config_dict)


@pytest.fixture
def check():
    return Check(
        domain="example.com",
        response_time=3265,
        status=200,
        url="https://example.com",
    )


@pytest.fixture
def three_checks():
    return [
        Check(
            domain="example.com",
            response_time=51,
            status=200,
            url="https://example.com",
        ),
        Check(
            domain="example.com/200",
            response_time=65,
            status=200,
            url="https://example.com",
        ),
        Check(
            domain="example.com/404",
            response_time=35,
            status=404,
            url="https://example.com",
        ),
    ]
