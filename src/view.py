import abc
from typing import List, Tuple


class View(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        """
        Interface for views.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def start(self):
        """
        Start the view.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self):
        """
        Stop the view.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def show_menu(self, sessions: List[Tuple[int, int, str]]):
        """
        Show the menu.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_confirmation(self, message: str) -> int:
        """
        Show a confirmation `message` and return the user's key input as an int.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def show_error(self, message: str):
        """
        Show an error message.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def cursor_down(self):
        """
        Move the cursor down.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def cursor_up(self):
        """
        Move the cursor up.
        """
        raise NotImplementedError
