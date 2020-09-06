====================
Website checker demo
====================

.. image:: https://github.com/vladan/aiven-site-checker/workflows/build/badge.svg
   :target: https://github.com/vladan/aiven-site-checker/actions?query=workflow%3Abuild+branch%3Amaster

.. image:: https://github.com/vladan/aiven-site-checker/workflows/documentation/badge.svg
   :target: https://github.com/vladan/aiven-site-checker/actions?query=workflow%3Adocumentation+branch%3Amaster

CHWEB is a website checking tool.

ATM in its very early stages meant to demo `aiven <https://aiven.io>`_'s
platform, using their `kafka <https://aiven.io/kafka>`_ and `postgresql
<https://aiven.io/postgresql>`_ services.


Quickstart
==========

Easiest way to start the application is to clone it, install it and run the
console scripts via the command line::

    pip install .
    chweb_collect -c config.yaml &
    chweb_consume -c config.yaml &

Sites
-----

You can specify the sites you want checked in the yaml config file. They are
stored in the ``sites`` key and are represented as a list of objects with
``url`` and ``check_interval`` as mandatory fields, and regex as an optional
field that can freely omitted which checks the body of the response against the
regex expression::

  - url: "https://example.com"
    regex: "domain" # a regex matching the body of the response
    check_interval: 5
  - url: "https://example.com"
    regex: "aaaaaaaa" # a regex not matching the body of the response
    check_interval: 8
  - url: "https://example.com/404"
    check_interval: 13

Logging configuration
---------------------

.. highlight:: yaml

The ``logging`` section must be present. A simple example of a console logger
as seen in ``config.yaml``::

    logging:
      version: 1
      formatters:
        standard:
          format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        error:
          format: "%(levelname)s <PID %(process)d:%(processName)s> %(name)s.%(funcName)s(): %(message)s"
      handlers:
        console:
          class: logging.StreamHandler
          level: DEBUG
          formatter: standard
          stream: ext://sys.stdout
      root:
        level: DEBUG
        handlers: [console]
        propogate: yes

Postgres
--------

Postgres settings with aivens certs, passwords, etc. You'll get them once you
setup the postgres service on https://console.aiven.io/. My postgres section
in the config looks like this::

    postgres:
      dbhost: "pg-2e0f365c-vladanovic-4654.aivencloud.com"
      dbport: 23700
      dbname: "defaultdb"
      dbuser: "avnadmin"
      dbpass: ""
      dbcert: "./certs/pg.pem"

* ``dbhost`` and ``dbport``, ``dbuser`` and ``dbpass`` are straightforward.
* ``defaultdb`` is the database present by default, when the service is
  created. You can create another database if it rocks your boat.
* ``dbcert`` is the cert which opens in a modal popup in the console. You need
  to copy it manually to a file on a path you later state in the config.

Kafka
-----

Kafka is also a service easily provisioned through aivens console. After it's
set up you get a config section similar to this one::

    kafka:
      servers:
      - "kafka-f7ae38e-vladanovic-4654.aivencloud.com:23702"
      topic: "sitestats"
      cafile: "./certs/ca.pem"
      cert: "./certs/service.cert"
      key: "./certs/service.key"
      passwd: ""

* ``servers`` is a list because that's how the library is initialized, which
  makes sense if you have multiple brokers.
* ``topic`` is the kafka topic messages are sent to. You need to define it in
  aivens console as well.
* ``cafile``, ``cert`` and ``key`` are the ssl certificates you get when aivens
  kafka service is ready.
* ``password`` is not needed afaik, but you can give it a go.

Full config file
================

while reading about the config values might be good, here's a better
all-in-one config file, which ofc you'd need to update with your own values::

    kafka:
      servers:
      - "kafka-f7ae38e-vladanovic-4654.aivencloud.com:23702"
      topic: "sitestats"
      cafile: "./certs/ca.pem"
      cert: "./certs/service.cert"
      key: "./certs/service.key"
      passwd: ""
    postgres:
      dbhost: "pg-2e0f365c-vladanovic-4654.aivencloud.com"
      dbport: 23700
      dbname: "defaultdb"
      dbuser: "avnadmin"
      dbpass: ""
      dbcert: "./certs/pg.pem"
    sites:
    - url: "https://dsadakjhkjsahkjh.com"
      regex: "domain"
      check_interval: 5
    - url: "https://example.com"
      regex: "aaaaaaaaaaaaa"
      check_interval: 8
    - url: "https://example.com/404"
      check_interval: 13
    logging:
      version: 1
      formatters:
        standard:
          format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        error:
          format: "%(levelname)s <PID %(process)d:%(processName)s> %(name)s.%(funcName)s(): %(message)s"
      handlers:
        console:
          class: logging.StreamHandler
          level: DEBUG
          formatter: standard
          stream: ext://sys.stdout
      root:
        level: DEBUG
        handlers: [console]
        propogate: yes
