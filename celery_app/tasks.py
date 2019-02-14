from __future__ import absolute_import
from celery_factory import app

from parser import parser


@app.task
def parse_url_task(url, job_id):
    print('start task')
    parser.parse_url(url, job_id)
    print('end task')
