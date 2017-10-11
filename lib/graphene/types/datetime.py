from __future__ import absolute_import

import datetime

from graphql.language import ast

from .scalars import Scalar

try:
    import iso8601
except:
    raise ImportError(
        "iso8601 package is required for DateTime Scalar.\n"
        "You can install it using: pip install iso8601."
    )


class DateTime(Scalar):
    '''
    The `DateTime` scalar type represents a DateTime
    value as specified by
    [iso8601](https://en.wikipedia.org/wiki/ISO_8601).
    '''

    @staticmethod
    def serialize(dt):
        assert isinstance(dt, (datetime.datetime, datetime.date)), (
            'Received not compatible datetime "{}"'.format(repr(dt))
        )
        return dt.isoformat()

    @classmethod
    def parse_literal(cls, node):
        if isinstance(node, ast.StringValue):
            return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        return iso8601.parse_date(value)


class Time(Scalar):
    '''
    The `Time` scalar type represents a Time value as
    specified by
    [iso8601](https://en.wikipedia.org/wiki/ISO_8601).
    '''
    epoch_date = '1970-01-01'

    @staticmethod
    def serialize(time):
        assert isinstance(time, datetime.time), (
            'Received not compatible time "{}"'.format(repr(time))
        )
        return time.isoformat()

    @classmethod
    def parse_literal(cls, node):
        if isinstance(node, ast.StringValue):
            return cls.parse_value(node.value)

    @classmethod
    def parse_value(cls, value):
        dt = iso8601.parse_date('{}T{}'.format(cls.epoch_date, value))
        return datetime.time(dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)
