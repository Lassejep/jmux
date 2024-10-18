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
    def exit_program(self):
        """
        Exit the program.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def show_session_menu(self):
        """
        Format the sessions for display.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def handle_input(self, key: int):
        """
        Handle key input.
        """
        raise NotImplementedError

    def load_session(self):
        """
        Load a session.
        """
        raise NotImplementedError

    def delete_session(self):
        """
        Delete a session.
        """
        raise NotImplementedError
