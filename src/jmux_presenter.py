import sys
from enum import Enum

from src.jmux_session import SessionLabel
from src.model import Model
from src.presenter import Presenter
from src.view import View


class InputKeys(Enum):
    ESCAPE = 27
    ENTER = 10
    UP = 259
    DOWN = 258
    LOWER_Q = ord("q")
    LOWER_J = ord("j")
    LOWER_K = ord("k")
    LOWER_D = ord("d")
    LOWER_A = ord("a")
    LOWER_R = ord("r")
    LOWER_S = ord("s")
    LOWER_Y = ord("y")
    LOWER_N = ord("n")

    UPPER_Y = ord("Y")
    UPPER_N = ord("N")


class JmuxPresenter(Presenter):
    def __init__(self, view: View, model: Model):
        """
        Presenter for the GUI.
        """
        self.view = view
        self.model = model
        self.position = 0
        self._update_sessions()

    def run(self) -> None:
        """
        Start the presenter.
        """
        self.view.start()

    def stop(self) -> None:
        self.view.stop()
        sys.exit(0)

    def _update_sessions(self) -> None:
        self.saved_sessions = self.model.list_saved_sessions()
        self.running_sessions = self.model.list_running_sessions()
        self.current_session = self.model.get_active_session()

    def running_sessions_menu(self) -> None:
        """
        get all running sessions from the model and show them in a view menu.
        """
        self._update_sessions()
        session_names = [
            self._annotate_running_session(index, session)
            for index, session in enumerate(self.running_sessions)
        ]
        self.view.show_running_sessions(session_names)

    def _annotate_running_session(self, index: int, session: SessionLabel) -> str:
        name = f"{index + 1}. {session.name}"
        if session == self.current_session:
            name += "*"
        if session in self.saved_sessions:
            name += " (saved)"
        return name

    def saved_sessions_menu(self) -> None:
        """
        Get all saved sessions from the model and show them in a view menu.
        """
        self._update_sessions()
        session_names = [
            self._annotate_saved_session(index, session)
            for index, session in enumerate(self.saved_sessions)
        ]
        self.view.show_saved_sessions(session_names)

    def _annotate_saved_session(self, index: int, session: SessionLabel) -> str:
        name = f"{index + 1}. {session.name}"
        if session == self.current_session:
            name += "*"
        if session in self.running_sessions:
            name += " (running)"
        return name

    def handle_input(self, key: int) -> None:
        """
        Handle user input.
        """
        match key:
            case InputKeys.LOWER_Q.value | InputKeys.ESCAPE.value:
                self.stop()
            case InputKeys.LOWER_K.value | InputKeys.UP.value:
                self._move_cursor_up()
            case InputKeys.LOWER_J.value | InputKeys.DOWN.value:
                self._move_cursor_down()
            case InputKeys.ENTER.value:
                self.load_session()
            case InputKeys.LOWER_D.value:
                self.delete_session()
            case _:
                error_message = f"Invalid key code: {key}"
                self.view.show_error(error_message)

    def _move_cursor_up(self) -> None:
        if self.position > 1:
            self.position -= 1
            self.view.cursor_up()

    def _move_cursor_down(self) -> None:
        if self.position < len(self.saved_sessions):
            self.position += 1
            self.view.cursor_down()

    def create_session(self) -> None:
        """
        Create a new session.
        """
        pass

    def save_session(self) -> None:
        """
        Save the selected session.
        """
        pass

    def load_session(self) -> None:
        """
        Load the selected session.
        """
        pass

    def kill_session(self) -> None:
        """
        Kill the selected session.
        """
        pass

    def delete_session(self) -> None:
        """
        Delete the selected session.
        """
        pass

    def rename_session(self) -> None:
        """
        Rename the selected session.
        """
        pass
