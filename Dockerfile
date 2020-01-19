FROM python:3.6-slim

WORKDIR /app

RUN pip install tox

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY requirements-test.txt /app
RUN pip install -r requirements-test.txt

COPY . /app
