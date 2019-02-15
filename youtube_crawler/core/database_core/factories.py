from schematics.models import Model
from schematics.types import StringType, IntType

from .database.schema import (Job as AlchemyJob, Video as AlchemyVideo)


class SQLAlchemyMixin:
    def to_alchemy(self):
        return self.alchemy_model(**self.to_native())

    @classmethod
    def from_alchemy(cls, alchemy_object):
        return cls(alchemy_object.to_dict())


class Base(Model):
    def __repr__(self):
        def filter_properties(obj):
            # this function decides which properties should be exposed through repr
            properties = obj.to_native().keys()
            for prop in properties:
                yield (prop, str(getattr(obj, prop)))
            return

        prop_tuples = filter_properties(self)
        prop_string_tuples = (": ".join(prop) for prop in prop_tuples)
        prop_output_string = " | ".join(prop_string_tuples)
        cls_name = self.__module__ + "." + self.__class__.__name__

        return "<%s('%s')>" % (cls_name, prop_output_string)


class Job(Base, SQLAlchemyMixin):
    alchemy_model = AlchemyJob

    job_id = IntType()
    url = StringType(required=True)
    periodicity = IntType(required=True)


class Video(Base, SQLAlchemyMixin):
    alchemy_model = AlchemyVideo

    video_id = IntType()
    job_id = IntType(required=True)
    video_url = StringType(required=True)
    title = StringType(required=True)
    duration = StringType(required=True)
    views = StringType(required=True)
    thumbnail_image = StringType(required=True)
    original_full_sized_image = StringType(required=True)
    local_thumbnail_image = StringType()
    local_original_full_sized_image = StringType()
