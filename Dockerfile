FROM python:3.7-buster

WORKDIR /www

ADD ./ /www

RUN pip install -i https://pypi.douban.com/simple --default-timeout=100 -r ./requirements.txt

CMD ['sh', '-c', 'scrapy crawl beike']