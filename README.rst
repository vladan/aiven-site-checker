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


Install and run the application with::

    pip install .
    chweb_collect -c config.yaml &
    chweb_consume -c config.yaml &
