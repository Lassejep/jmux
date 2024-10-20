import abc
from typing import List


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
    def show_running_sessions(self, session_names: List[str]):
        """
        Show a list of running sessions.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def show_saved_sessions(self, session_names: List[str]):
        """
        Show a list of saved sessions.
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

    def create_new_session(self) -> str:
        """
        Show a prompt to create a new session and return the name of the session.
        """
        raise NotImplementedError
