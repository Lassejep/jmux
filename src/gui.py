import abc


class View(abc.ABC):
    """
    Interface for views.
    """

    @abc.abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def start(self):
        """
        Start the view.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def show_menu(self):
        """
        Show the menu.
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


class Presenter(abc.ABC):
    """
    Interface for presenters.
    """

    @abc.abstractmethod
    def __init__(self, view: View):
        raise NotImplementedError

    @abc.abstractmethod
    def run(self):
        """
        Run the presenter.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def format_sessions(self):
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
