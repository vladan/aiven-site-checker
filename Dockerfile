FROM python:3.8-slim

USER root

RUN mkdir /tmp/build
WORKDIR /tmp/build
COPY . .
RUN SETUPTOOLS_SCM_PRETEND_VERSION=0 pip install .

WORKDIR /tmp
RUN rm -rf /tmp/build

RUN useradd --system checker
USER checker
