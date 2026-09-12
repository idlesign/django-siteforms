FROM python:3.10-alpine

ADD . /code
WORKDIR /code

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
