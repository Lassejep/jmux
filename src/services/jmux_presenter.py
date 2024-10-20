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
    CONFIRMATION = 3
    RENAME_SESSION = 4


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
        self.position = -1
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
        self.view.show_menu(session_names)

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
        self.view.show_menu(session_names)

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
            case InputKeys.LOWER_A.value:
                self.create_session()
            case InputKeys.ENTER.value:
                self.load_session()
            case InputKeys.LOWER_D.value:
                state = self.state_stack.get()
                if state == State.RUNNING_SESSIONS_MENU:
                    self.kill_session()
                elif state == State.SAVED_SESSIONS_MENU:
                    self.delete_session()
                self.state_stack.put(state)
            case InputKeys.LOWER_R.value:
                self.rename_session()
            case _:
                error_message = f"Invalid key code: {key}"
                self.view.show_error(error_message)

    def _move_cursor_up(self) -> None:
        if self.position > 0:
            self.position -= 1
            self.view.cursor_up()

    def _move_cursor_down(self) -> None:
        if self.position < len(self.saved_sessions) - 1:
            self.position += 1
            self.view.cursor_down()

    def create_session(self) -> None:
        """
        Create a new session.
        """
        previous_state = self.state_stack.get()
        self.state_stack.put(State.CREATE_SESSION)
        session_name = self.view.create_new_session()
        self.state_stack.get()
        if session_name and not session_name.isspace():
            self.model.create_session(session_name)
        self._return_to_previous_state(previous_state)

    def save_session(self) -> None:
        """
        Save the selected session.
        """
        if self._check_position(self.running_sessions) and self._get_confirmation(
            "Save session? (y/N)", "Session not saved"
        ):
            self.model.save_session(self.running_sessions[self.position])

    def load_session(self) -> None:
        """
        Load the selected session.
        """
        previous_state = self.state_stack.get()
        session_list = (
            self.saved_sessions
            if previous_state == State.SAVED_SESSIONS_MENU
            else self.running_sessions
        )
        if self._check_position(session_list):
            self.model.load_session(session_list[self.position])
        self._return_to_previous_state(previous_state)

    def kill_session(self) -> None:
        """
        Kill the selected session.
        """
        if self._check_position(self.running_sessions) and self._get_confirmation(
            "Kill session? (y/N)", "Session not killed"
        ):
            self.model.kill_session(self.running_sessions[self.position])

    def delete_session(self) -> None:
        """
        Delete the selected session.
        """
        if self._check_position(self.saved_sessions) and self._get_confirmation(
            "Permanently delete session? (y/N)", "Session not deleted"
        ):
            self.model.delete_session(self.saved_sessions[self.position])

    def rename_session(self) -> None:
        """
        Rename the selected session.
        """
        previous_state = self.state_stack.get()
        session_list = (
            self.saved_sessions
            if previous_state == State.SAVED_SESSIONS_MENU
            else self.running_sessions
        )
        if self._check_position(session_list):
            self.state_stack.put(State.RENAME_SESSION)
            new_name = self.view.rename_session(session_list[self.position].name)
            self.state_stack.get()
            if (
                new_name
                and not new_name.isspace()
                and self._get_confirmation(
                    "Rename session? (y/N)", "Session not renamed"
                )
            ):
                self.model.rename_session(session_list[self.position], new_name)
        self._return_to_previous_state(previous_state)

    def _return_to_previous_state(self, return_state: State) -> None:
        match return_state:
            case State.RUNNING_SESSIONS_MENU:
                self.running_sessions_menu()
            case State.SAVED_SESSIONS_MENU:
                self.saved_sessions_menu()
            case State.CREATE_SESSION:
                self.create_session()
            case State.CONFIRMATION:
                self.view.show_error("Could not return to previous state")
                self.running_sessions_menu()
            case _:
                self.view.show_error("Could not return to previous state")
                self.running_sessions_menu()

    def _check_position(self, session_list: list[SessionLabel]) -> bool:
        if self.position < 0 or self.position > len(session_list) - 1:
            self.view.show_error("Invalid session")
            return False
        return True

    def _get_confirmation(self, prompt: str, error_message: str) -> bool:
        self.state_stack.put(State.CONFIRMATION)
        confirmation = self.view.get_confirmation(prompt)
        self.state_stack.get()
        if confirmation not in (InputKeys.LOWER_Y.value, InputKeys.UPPER_Y.value):
            self.view.show_error(error_message)
            return False
        return True
