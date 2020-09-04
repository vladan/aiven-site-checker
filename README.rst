============================
Website stats collector demo
============================

CHWEB is a website checking tool.

ATM in its very early stages meant to demo `aiven <https://aiven.io>`_'s
platform, using their `kafka <https://aiven.io/kafka>`_ and `postgresql
<https://aiven.io/postgresql>`_ services.


Install and run the application with::

    pip install https://github.com/vladan/aiven-status-checker/releases/...
    chweb_collect -c config.yaml &
    chweb_consume -c config.yaml &

or run in docker with::

    docker-compose up
