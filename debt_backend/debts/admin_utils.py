from typing import Callable, List, TypeVar, Any

from django.http.request import HttpRequest

OBJ = TypeVar("OBJ")
PREDICT = Callable[[OBJ], bool]
ACTION = Callable[[Any, OBJ, HttpRequest], Any]


class ObjectActionsController:
    def __init__(self) -> None:
        self._controlled = {}

    def show_when(self, predict: PREDICT) -> Callable:
        def decorator(function: ACTION) -> Callable:
            function.predict = predict
            function_name = function.__name__
            self._controlled[function_name] = function
            return function
        return decorator

    def filter_by_object(self, obj: OBJ) -> List[str]:
        return [
            function_name for function_name, function
            in self._controlled.items()
            if function.predict(obj)
        ]

    @property
    def change_actions(self) -> List[str]:
        return list(self._controlled.keys())
