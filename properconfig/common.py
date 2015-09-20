"""
Created by @dtheodor at 2015-09-06
"""
from collections import namedtuple

ParseAttempt = namedtuple("ParseAttempt", [
    "success", "value", "option_name", "source", "count"])

failed_attempt = ParseAttempt(success=False,
                              value=None,
                              option_name=None,
                              source=None,
                              count=None)


class sources(object):
    CLI = "cli"
    DEFAULT = "default_value"
    FILE = "file"
    ENV = "environment"


class SourceInfo(object):
    """Holds information on the source from which an option was parsed."""
    __slots__ = ()

    def __repr__(self):
        attrs = ("source",) + self.__slots__
        arg_strings = ['%s=%r' % (attr, getattr(self, attr))
                       for attr in attrs]
        return '%s(%s)' % (type(self).__name__, ', '.join(arg_strings))
