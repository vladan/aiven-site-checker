.. chweb documentation master file, created by
   sphinx-quickstart on Fri Sep  4 19:58:09 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

chweb - Check websites state
============================

CHWEB is a website checking tool.

ATM in its very early stages meant to demo
`aiven <https://aiven.io>`_'s platform, using their `kafka
<https://aiven.io/kafka>`_ and `postgresql <https://aiven.io/postgresql>`_
services.

Features
--------

* Easy and intuitive YAML configuration.
* Command line executables for the checker and the consumer/psql writer:
  ``chweb_collect`` and ``chweb_consume``.
* Environment configuration.


.. toctree::
   :maxdepth: 1

   configuration
   environment
   architecture
   apidocs

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
