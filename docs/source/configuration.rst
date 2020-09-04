Running the services
====================

When you install the package you get two commad-line applications:
``chweb_collect`` and ``chweb_consume``.

Both of them need a configuration file to start, e.g.::

    chweb_consume --help
    usage: chweb_consume [-h] [-c CONFIG]

    Website availibility checker.

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG, --config CONFIG
                            The yaml config file. Defaults to /etc/checker.yaml


Configuration
-------------

Both cli scripts use the same config file to simplify deployment. You only set
it up once and supply it to the scripts on their locations.

The config file is somewhat straightforward, as it can be seen in this example::

    kafka:
      servers:
      - "localhost:9992"
      topic: "sample"
    postgres:
      dbhost: "localhost"
      dbport: 5432
      dbname: "chweb"
      dbuser: "vladan"
      dbpass: ""
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
