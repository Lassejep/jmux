import abc

from src.interfaces.model import Model
from src.interfaces.view import View
from src.models import Commands


class Presenter(abc.ABC):
    @abc.abstractmethod
    def __init__(self, view: View, model: Model) -> None:
        """
        Interface for presenters.
        """
        self.view: View
        self.model: Model
        self.position: int
        raise NotImplementedError

    @abc.abstractmethod
    def run(self) -> None:
        """
        Run the presenter.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self) -> None:
        """
        Stop the presenter.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def handle_input(self, command: Commands) -> None:
        """
        Handle user input.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def running_sessions_menu(self) -> None:
        """
        Get all running sessions from the model and show them in a view menu.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def saved_sessions_menu(self) -> None:
        """
        Get all saved sessions from the model and show them in a view menu.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_session(self) -> None:
        """
        Create a session.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def save_session(self) -> None:
        """
        Save a session.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def load_session(self) -> None:
        """
        Load a session.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def kill_session(self) -> None:
        """
        Kill a session.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_session(self) -> None:
        """
        Delete a session.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def rename_session(self) -> None:
        """
        Rename a session.
        """
        raise NotImplementedError
