from __future__ import absolute_import
from celery import Celery
app = Celery(
    'youtube_crawler',
    broker='amqp://rabbitmq',
    backend='rpc://',
    include=['tasks'])
