from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from src.data_models import Event
from src.interfaces.model import Model
from src.interfaces.view import View

ReturnType = TypeVar("ReturnType")


class Presenter(ABC, Generic[ReturnType]):
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
    def deactivate(self) -> None:
        """
        Deactivate the presenter.
        """
        raise NotImplementedError

    @abstractmethod
    def update_view(self) -> None:
        """
        Get data from the model and update the view.
        """
        raise NotImplementedError

    @abstractmethod
    def get_event(self) -> Event:
        """
        Get event from the view.
        """
        raise NotImplementedError

    @abstractmethod
    def handle_event(self, event: Event, *args: Any) -> ReturnType:
        """
        Handle a given `event`.
        """
        raise NotImplementedError
