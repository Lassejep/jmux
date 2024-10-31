from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Generic, TypeVar

from src.interfaces.model import Model
from src.interfaces.view import View

ReturnType = TypeVar("ReturnType")
EventType = TypeVar("EventType", bound=Enum)


class Presenter(ABC, Generic[EventType, ReturnType]):
    @abstractmethod
    def __init__(self, view: View, model: Model) -> None:
        """
        Interface for presenters.
        """
        self.view: View
        self.model: Model
        self.active: bool
        raise NotImplementedError

    @abstractmethod
    def activate(self) -> None:
        """
        Activate the presenter.
        """
        raise NotImplementedError

    @abstractmethod
    def update_view(self) -> None:
        """
        Get data from the model and update the view.
        """
        raise NotImplementedError

    @abstractmethod
    def get_event(self) -> EventType:
        """
        Get event from the view.
        """
        raise NotImplementedError

    @abstractmethod
    def handle_event(self, event: EventType, *args: Any) -> ReturnType:
        """
        Handle a given `event`.
        """
        raise NotImplementedError
