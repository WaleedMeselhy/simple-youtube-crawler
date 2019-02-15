from __future__ import absolute_import
from celery_factory import app as celery_app
import time
import schedule
import thread
from flask_restplus import Api, Resource, fields
from flask import Flask, send_file
from database_core.database.gateway import DBGateway
from database_core.repositories import JobRepository, VideoRepository
from database_core.factories import Video as VideoModel, Job as JobModel


def run_periodic():
    while True:
        schedule.run_pending()
        time.sleep(1)


def run_task(url, job_id):
    # parse_url_task.delay(url, job_id)
    celery_app.send_task(
        'parse_url_task', kwargs={
            'url': url,
            'job_id': job_id
        })


flask_app = Flask(__name__)
job_repository = JobRepository()
video_repository = VideoRepository()
api = Api(
    flask_app,
    version='1.0',
    title='YoutubeCrawler API',
    description='A simple YoutubeCrawler API',
)

ns = api.namespace('crawel_jobs', description='Job operations')

crawel_job = api.model(
    'crawel_job', {
        'job_id':
        fields.Integer(readOnly=True, description='The job unique identifier'),
        'url':
        fields.String(
            required=True,
            description='The youtube url',
            example='https://www.youtube.com/user/AsapSCIENCE/videos'),
        'periodicity':
        fields.Integer(required=True, description='The periodicity of job')
    })

video = api.model(
    'video', {
        'video_id':
        fields.Integer(
            readOnly=True, description='The video unique identifier'),
        'job_id':
        fields.Integer(required=True, description='The job unique identifier'),
        'video_url':
        fields.String(required=True, description='The video url'),
        'title':
        fields.String(required=True, description='The video title'),
        'duration':
        fields.String(required=True, description='The video duration'),
        'views':
        fields.String(required=True, description='The video views'),
        'thumbnail_image':
        fields.String(required=True, description='The video thumbnail_image'),
        'original_full_sized_image':
        fields.String(
            required=True, description='The video original_full_sized_image'),
        'local_thumbnail_image':
        fields.String(
            required=True, description='The video local_thumbnail_image'),
        'local_original_full_sized_image':
        fields.String(
            required=True,
            description='The video local_original_full_sized_image')
    })


@ns.route('/')
class JobList(Resource):
    '''Shows a list of all crawl jobs, and lets you POST to add new job'''

    @ns.doc('list_jobs')
    @ns.marshal_list_with(crawel_job)
    def get(self):
        '''List all jobs'''
        jobs = job_repository.get_all_jobs(DBGateway)
        jobs = [job.to_native() for job in jobs]
        return jobs
        # return DAO.todos

    @ns.doc('create_todo')
    @ns.expect(crawel_job)
    @ns.marshal_with(crawel_job, code=201)
    @ns.response(409, 'URL {} already exist')
    def post(self):
        '''Create a new job'''
        job = JobModel(api.payload)
        job.validate()
        job.periodicity = 1 if job.periodicity == 0 else job.periodicity
        data = job.to_native()
        data.pop('job_id')
        obj, created = job_repository.get_or_create(DBGateway, data)
        print(obj)
        if created:
            run_task(obj.url, obj.job_id)
            schedule.every(job.periodicity).hour.do(run_task, obj.url,
                                                    obj.job_id)
            return obj.to_native(), 201
        else:
            api.abort(409, "URL {} already exist".format(job.url))


@ns.route('/<int:id>/videos')
@ns.param('id', 'The Job identifier')
class Videos(Resource):
    '''Show list of videos in crawel job'''

    @ns.doc('get_videos')
    @ns.marshal_list_with(video)
    def get(self, id):
        videos = video_repository.filter(DBGateway, job_id=id)
        videos = [video.to_native() for video in videos]
        return videos


@ns.route('/<int:id>/videos/<int:video_id>/full.jpg')
@ns.param('id', 'The Job identifier')
@ns.param('video_id', 'The Video identifier')
class FullImage(Resource):
    @ns.doc('get full image')
    @ns.response(200, description='return full image.')
    @ns.produces(['image/jpg'])
    def get(self, id, video_id):
        video = video_repository.get(DBGateway, job_id=id, video_id=video_id)
        return send_file(
            video.local_original_full_sized_image, mimetype='image/jpg')


@ns.route('/<int:id>/videos/<int:video_id>/thumbnail.jpg')
@ns.param('id', 'The Job identifier')
@ns.param('video_id', 'The Video identifier')
class ThumbnailImage(Resource):
    @ns.doc('get thumbnail image')
    @ns.response(200, description='return thumbnail image.')
    @ns.produces(['image/jpg'])
    def get(self, id, video_id):
        video = video_repository.get(DBGateway, job_id=id, video_id=video_id)
        return send_file(video.local_thumbnail_image, mimetype='image/jpg')


@flask_app.before_request
def before_request():
    jobs = job_repository.get_all_jobs(DBGateway)
    print('init function')
    for job in jobs:
        schedule.every(job.periodicity).hour.do(run_task, job.url, job.job_id)
        run_task(job.url, job.job_id)
    thread.start_new_thread(run_periodic, ())


if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', debug=True)
