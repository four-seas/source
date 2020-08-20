FROM python:3.7-buster

WORKDIR /www

ADD requirements.txt /www

RUN cd /www && pip install -r ./requirements.txt