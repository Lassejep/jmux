from abc import ABC, abstractmethod
from enum import Enum
from typing import Generic, TypeVar

EventType = TypeVar("EventType", bound=Enum)


class View(ABC, Generic[EventType]):
    @abstractmethod
    def __init__(self) -> None:
        """
        Interface for views.
        """
        raise NotImplementedError

    @abstractmethod
    def get_event(self) -> EventType:
        """
        Get a command from the user.
        """
        raise NotImplementedError

    @abstractmethod
    def render(self, *args, **kwargs) -> None:
        """
        Render view.
        """
        raise NotImplementedError
