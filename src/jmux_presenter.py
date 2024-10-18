import sys
from enum import Enum

from src.presenter import Presenter
from src.session_manager import SessionManager
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
    """
    Presenter for the GUI.
    """

    def __init__(self, view: View, session_manager: SessionManager):
        self.view = view
        self.session_manager = session_manager
        self.position = 0
        self._update_saved_sessions()

    def run(self) -> None:
        """
        Start the presenter.
        """
        self.view.start()

    def _update_saved_sessions(self):
        sessions_dir = self.session_manager.file_handler.sessions_folder
        self.saved_sessions = [
            session_file.stem for session_file in sessions_dir.iterdir()
        ]

    def show_session_menu(self):
        """
        Format the sessions for display.
        """
        self._update_saved_sessions()
        if len(self.saved_sessions) > 0:
            self.position = 1
        sessions = [
            (index + 1, 0, f"{index + 1}. {session}")
            for index, session in enumerate(self.saved_sessions)
        ]
        self.view.show_menu(sessions)

    def handle_input(self, key: int) -> None:
        """
        Handle user input.
        """
        match key:
            case InputKeys.LOWER_Q.value | InputKeys.ESCAPE.value:
                self.exit_program()
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

    def exit_program(self) -> None:
        self.view.stop()
        sys.exit(0)

    def _move_cursor_up(self) -> None:
        if self.position > 1:
            self.position -= 1
            self.view.cursor_up()

    def _move_cursor_down(self) -> None:
        if self.position < len(self.saved_sessions):
            self.position += 1
            self.view.cursor_down()

    def load_session(self) -> None:
        """
        Load the selected session.
        """
        self.saved_sessions
        if len(self.saved_sessions) == 0:
            self.view.show_error("No sessions to load")
            return
        session_name = self.saved_sessions[self.position - 1]
        try:
            self.session_manager.load_session(session_name)
            self.exit_program()
        except ValueError as e:
            self.view.show_error(str(e))

    def delete_session(self) -> None:
        """
        Delete the selected session.
        """
        if len(self.saved_sessions) == 0:
            self.view.show_error("No sessions to delete")
            return
        session_name = self.saved_sessions[self.position - 1]
        confirmation_response = self.view.get_confirmation(
            f"Delete session {session_name}? (y/N)"
        )
        if confirmation_response in (InputKeys.LOWER_Y.value, InputKeys.UPPER_Y.value):
            try:
                self.session_manager.delete_session(session_name)
                self.show_session_menu()
            except ValueError as e:
                self.view.show_error(str(e))
        else:
            self.show_session_menu()
            self.view.show_error("Session not deleted")
