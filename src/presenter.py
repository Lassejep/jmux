import abc

from src.view import View


class Presenter(abc.ABC):
    @abc.abstractmethod
    def __init__(self, view: View):
        """
        Interface for presenters.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run(self):
        """
        Run the presenter.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self):
        """
        Stop the presenter.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def running_sessions_menu(self):
        """
        Get all running sessions from the model and show them in a view menu.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def saved_sessions_menu(self):
        """
        Get all saved sessions from the model and show them in a view menu.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def handle_input(self, key: int):
        """
        Handle user input.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_session(self):
        """
        Create a session.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def save_session(self):
        """
        Save a session.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def load_session(self):
        """
        Load a session.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def kill_session(self):
        """
        Kill a session.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_session(self):
        """
        Delete a session.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def rename_session(self):
        """
        Rename a session.
        """
        raise NotImplementedError
