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
    def render(self, *args, **kwargs) -> None:
        """
        Render view.
        """
        raise NotImplementedError

    @abstractmethod
    def get_command(self) -> EventType:
        """
        Get a command from the user.
        """
        raise NotImplementedError

    @abstractmethod
    def get_input(self, input_prompt: str) -> str:
        """
        Show `input_prompt` and return a string based on user input.
        """
        raise NotImplementedError

    @abstractmethod
    def get_confirmation(self, confirmation_prompt: str) -> bool:
        """
        Show `confirmation_prompt` and return a boolean based on user input.
        """
        raise NotImplementedError

    @abstractmethod
    def show_message(self, message: str) -> None:
        """
        Show a message to the user.
        """
        raise NotImplementedError
