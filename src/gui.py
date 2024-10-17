import abc


class View(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def start(self):
        raise NotImplementedError

    @abc.abstractmethod
    def show_menu(self):
        raise NotImplementedError

    @abc.abstractmethod
    def cursor_down(self):
        raise NotImplementedError

    @abc.abstractmethod
    def cursor_up(self):
        raise NotImplementedError


class Presenter(abc.ABC):
    @abc.abstractmethod
    def __init__(self, view: View):
        raise NotImplementedError

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError

    @abc.abstractmethod
    def format_sessions(self):
        raise NotImplementedError

    @abc.abstractmethod
    def handle_input(self, key: int):
        raise NotImplementedError
