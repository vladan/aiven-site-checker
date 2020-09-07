==================
Environment config
==================

The kafka and postgres settings can be overriden via the environment.
These are the env variables accepted by the applications with example values::

    KAFKA_SERVERS=kafkaserver.one.com:9092,kfk02.server.two.com
    KAFKA_TOPIC=status_checker

    POSTGRES_DB=chweb
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_USER=vladan
    POSTGRES_PASS=secret
