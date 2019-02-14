# coding=utf-8

from sqlalchemy import (Column, ForeignKey, String, Integer)
from sqlalchemy.ext.declarative import declarative_base, declared_attr


class Base(object):
    """
    a base class for all of our models, this defines:
    1) the table name to be the lower-cased version of the class name
    2) generic __init__ and __repr__ functions
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __init__(self, **kwargs):
        for key in kwargs:
            if key not in self.attr_accessor:
                raise Exception('Invalid Prop: {key}'.format(key=key))
            setattr(self, key, kwargs[key])

    def to_dict(self):
        return {
            k: v
            for k, v in self.__dict__.items() if not k.startswith('_')
        }

    def __repr__(self):
        def filter_properties(obj):
            # this function decides which properties should be exposed through repr
            properties = obj.__dict__.keys()
            for prop in properties:
                if prop[0] != "_" and not callable(prop):
                    yield (prop, str(getattr(obj, prop)))
            return

        prop_tuples = filter_properties(self)
        prop_string_tuples = (": ".join(prop) for prop in prop_tuples)
        prop_output_string = " | ".join(prop_string_tuples)
        cls_name = self.__module__ + "." + self.__class__.__name__

        return "<%s('%s')>" % (cls_name, prop_output_string)


Base = declarative_base(cls=Base)


class Job(Base):
    __tablename__ = '_job'
    job_id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    periodicity = Column(Integer)


class Video(Base):
    video_id = Column(Integer, primary_key=True)
    job_id = Column(
        Integer,
        ForeignKey("_job.job_id", ondelete='RESTRICT'),
        nullable=False)

    video_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    views = Column(String, nullable=False)
    thumbnail_image = Column(String, nullable=False)
    original_full_sized_image = Column(String, nullable=False)
    local_thumbnail_image = Column(String)
    local_original_full_sized_image = Column(String)
