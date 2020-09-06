import asyncio
import pytest
from chweb.cmd import create_config
from chweb.models import Check

@pytest.fixture()
def config():
    config_dict = {
      'kafka': {
        'servers': ["localhost:9992"],
        'topic': "sample",
      },
      'postgres': {
        'dbhost': "localhost",
        'dbport': 5432,
        'dbname': "chweb",
        'dbuser': "vladan",
        'dbpass': "",
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
      },
      'postgres': {
        'dbhost': "localhost",
        'dbport': 5432,
        'dbname': "chweb",
        'dbuser': "vladan",
        'dbpass': "",
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
