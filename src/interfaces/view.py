import abc
from typing import List

from src.models import Commands


class View(abc.ABC):
    @abc.abstractmethod
    def __init__(self) -> None:
        """
        Interface for views.
        """
        self.running: bool
        raise NotImplementedError

    @abc.abstractmethod
    def start(self) -> None:
        """
        Start the view.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self) -> None:
        """
        Stop the view.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_input(self) -> Commands:
        """
        Get user input.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def show_menu(self, sessions: List[str]) -> None:
        """
        Show a menu with `sessions`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_confirmation(self, message: str) -> bool:
        """
        Show a confirmation `message` and return the user's key input as an int.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def show_error(self, message: str) -> None:
        """
        Show an error message.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def cursor_down(self) -> None:
        """
        Move the cursor down.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def cursor_up(self) -> None:
        """
        Move the cursor up.
        """
        raise NotImplementedError

    def create_new_session(self) -> str:
        """
        Show a prompt to create a new session and return the name of the session.
        """
        raise NotImplementedError

    def rename_session(self, session_name: str) -> str:
        """
        Show a prompt to rename a session and return the new name.
        """
        raise NotImplementedError
