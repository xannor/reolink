""" Model Typings """

from enum import IntEnum


class StreamType(IntEnum):
    """ Stream Types """

    CLEAR = 0
    FLUENT = 1
    BALANCED = 4
