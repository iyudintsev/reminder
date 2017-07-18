import re
import functools
from enum import Enum
from datetime import datetime


class State(Enum):
    more = 1
    equal = 0
    less = -1


class ServiceError(Exception):
    pass


def catch_exc(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except (ValueError, IndexError):
            raise ServiceError()
    return inner


class Service(object):
    pattern = re.compile(r'^([\d]{2})[:\-]([\d]{2})')

    @staticmethod
    def copy_time(time_: datetime):
        return datetime(year=time_.year, month=time_.month, day=time_.day, hour=time_.hour, minute=time_.minute)

    def create_time(self, message_text: str):
        search = Service.pattern.findall(message_text)
        hour, minute = search[0]
        hour, minute = int(hour), int(minute)
        now = datetime.now()
        time_ = datetime(year=now.year, month=now.month, day=now.day, hour=hour, minute=minute)

        if self.compare_time(now, time_) == State.more:
            time_ = datetime(year=now.year, month=now.month, day=now.day+1, hour=hour, minute=minute)

        return time_

    @staticmethod
    def create_text(message_text: str):
        return message_text.split(maxsplit=1)[1]

    def compare_time(self, t1, t2):
        t1_, t2_ = self.copy_time(t1), self.copy_time(t2)
        if t1_ > t2_:
            return State.more
        elif t1_ < t2_:
            return State.less
        else:
            return State.equal

    @catch_exc
    def parse(self, message_text: str):
        message_text = message_text.strip()
        time_ = self.create_time(message_text)
        text = self.create_text(message_text)
        return time_, text
