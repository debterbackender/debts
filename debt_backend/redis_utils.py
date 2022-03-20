from typing import NamedTuple, Iterable

from django_redis import get_redis_connection
from rest_framework.renderers import JSONRenderer


class Event(NamedTuple):
    user_id: str
    data: dict

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'data': self.data,
        }

    def send(self):
        SendEventService([self]).send()

    @classmethod
    def multiple_send(cls, events: Iterable['Event']):
        SendEventService(events).send()


class SendEventService:
    connection = get_redis_connection("default")

    def __init__(self, events: Iterable[Event]):
        self._events = events

    def send(self):
        payload = JSONRenderer().render([event.to_dict() for event in self._events])
        self.connection.publish("events", payload)
