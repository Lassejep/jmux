import sys
from enum import Enum
from queue import LifoQueue

from src.interfaces import Model, Presenter, View
from src.models import SessionLabel


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


class State(Enum):
    RUNNING_SESSIONS_MENU = 0
    SAVED_SESSIONS_MENU = 1
    CREATE_SESSION = 2


class JmuxPresenter(Presenter):
    def __init__(self, view: View, model: Model):
        """
        Presenter for the GUI.
        """
        if not view or not isinstance(view, View):
            raise TypeError("view must be an instance of View")
        if not model or not isinstance(model, Model):
            raise TypeError("model must be an instance of Model")
        self.view = view
        self.model = model
        self.position = 0
        self.state_stack: LifoQueue = LifoQueue()
        self._update_sessions()

    def run(self) -> None:
        """
        Start the presenter.
        """
        self.view.start()

    def stop(self) -> None:
        """
        Stop the presenter.
        """
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
        self.state_stack.put(State.RUNNING_SESSIONS_MENU)
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
        self.state_stack.put(State.SAVED_SESSIONS_MENU)
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
        self.state_stack.put(State.CREATE_SESSION)
        session_name = self.view.create_new_session()
        self.state_stack.get()
        if session_name and not session_name.isspace():
            self.model.create_session(session_name)
        return_state = self.state_stack.get()
        if return_state == State.RUNNING_SESSIONS_MENU:
            self.running_sessions_menu()
        elif return_state == State.SAVED_SESSIONS_MENU:
            self.saved_sessions_menu()

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
