from database_core.factories import Job, Video
from sqlalchemy import or_, and_, desc
from sqlalchemy.sql import tuple_

# from .database.gateway import session_scope

# from sqlalchemy.orm import with_expression
# from sqlalchemy.types.Comparator import overlaps


class DefaultRepository(object):
    model = None
    model_id_field = None

    def __init__(self, model=None, model_id_field=None):
        if model:
            self.model = model
        if model_id_field:
            self.model_id_field = model_id_field

    def get_or_create(self, gateway, defaults=None, **kwargs):
        with gateway.session_scope() as session:
            obj, created = gateway.get_or_create(
                session, self.model.alchemy_model, defaults=defaults, **kwargs)
            obj = self.model.from_alchemy(obj) if obj else None
        return obj, created

    def get_by_id(self, gateway, ident):
        with gateway.session_scope() as session:
            obj = gateway.get_by_id(
                session, self.model.alchemy_model, ident=ident)
            obj = self.model.from_alchemy(obj) if obj else None
        return obj

    def get(self, gateway, **kwargs):
        with gateway.session_scope() as session:
            obj = gateway.get(session, self.model.alchemy_model, **kwargs)
            obj = self.model.from_alchemy(obj) if obj else None
        return obj

    def filter(self, gateway, **kwargs):
        with gateway.session_scope() as session:
            objs = gateway.filter(session, self.model.alchemy_model, **kwargs)
            objs = list(map(lambda obj: self.model.from_alchemy(obj), objs))
        return objs

    def get_all(self, gateway):
        with gateway.session_scope() as session:
            objs = gateway.get_all(session, self.model.alchemy_model)
            objs = list(map(lambda obj: self.model.from_alchemy(obj), objs))
        return objs

    def update(self, gateway, obj, **kwargs):
        with gateway.session_scope() as session:
            obj = gateway.update(session, self.model.alchemy_model,
                                 getattr(obj, self.model_id_field), **kwargs)
            obj = self.model.from_alchemy(obj) if obj else None
        return obj

    def update_all(self, gateway, criterion, **kwargs):
        with gateway.session_scope() as session:
            ids = gateway.update_all(session, self.model.alchemy_model,
                                     criterion, **kwargs)
            # objs = list(map(lambda obj: self.model.from_alchemy(obj), objs))
        return ids

    def create(self, gateway, **kwargs):
        with gateway.session_scope() as session:
            obj = gateway.create(session, self.model.alchemy_model, **kwargs)
            obj = self.model.from_alchemy(obj)
        return obj


class JobRepository(DefaultRepository):
    model = Job
    model_id_field = 'job_id'

    # def get_or_create(self, gateway, defaults=None, **kwargs):
    #     raise NotImplementedError("TODO: to be implemented")

    def get_all_jobs(self, gateway):
        return self.get_all(gateway)

    # def get_job(self, gateway, user_id):
    #     model = self.model.alchemy_model
    #     with gateway.session_scope() as session:
    #         objs = session.query(model).filter(model.user_id == user_id)
    #         objs = list(map(lambda obj: self.model.from_alchemy(obj), objs))
    #     return objs


class VideoRepository(DefaultRepository):
    model = Video
    model_id_field = 'video_id'

    def create_or_update(self, gateway, video_url, job_id, title, duration,
                         views, thumbnail_image, original_full_sized_image,
                         local_thumbnail_image,
                         local_original_full_sized_image):
        with gateway.session_scope() as session:
            obj, created = gateway.get_for_update_or_create(
                session,
                self.model.alchemy_model,
                video_url=video_url,
                job_id=job_id,
                defaults={
                    'title':
                    title,
                    'duration':
                    duration,
                    'views':
                    views,
                    'thumbnail_image':
                    thumbnail_image,
                    'original_full_sized_image':
                    original_full_sized_image,
                    'local_thumbnail_image':
                    local_thumbnail_image,
                    'local_original_full_sized_image':
                    local_original_full_sized_image
                })

            # if not created:
            #     accounting_period = (
            #         datetime.datetime.now() - obj.billed_at).total_seconds()
            #     obj.total_cost = obj.total_cost + Decimal(
            #         total_price_per_time_unit * accounting_period)
            #     obj.last_observed_storage = last_observed_storage
            obj = self.model.from_alchemy(obj)
            return obj, created
