from typing import Optional

from src.file_handler import FileHandler
from src.models import JmuxSession
from src.multiplexer import Multiplexer


class SessionManager:
    """
    Manage terminal multiplexer sessions.
    """

    def __init__(self, file_handler: FileHandler, multiplexer: Multiplexer) -> None:
        if not file_handler or not isinstance(file_handler, FileHandler):
            raise ValueError("Invalid file_handler value")
        self.file_handler = file_handler

        if not multiplexer or not isinstance(multiplexer, Multiplexer):
            raise ValueError("Invalid multiplexer value")
        self.multiplexer = multiplexer

    def save_current_session(self) -> None:
        """
        Save the current session to a file in the specified folder.
        the `sessions_folder` parameter should be a pathlib.Path object and should point
        to a valid directory where the session file will be saved.
        """
        current_session_label = self.multiplexer.get_current_session_id()
        session = self.multiplexer.get_session(current_session_label.id)
        self.file_handler.save_session(session)

    def load_session(self, session_name: str) -> None:
        """
        Load the session with the name `session_name` from the sessions folder.
        """
        session = self.file_handler.load_session(session_name)
        current_sessions = self.multiplexer.list_sessions()
        if session.name in [
            session_label.name for session_label in current_sessions
        ] and session.id in [session_label.id for session_label in current_sessions]:
            raise ValueError("Session already exists")
        self.multiplexer.create_session(session)
        self.file_handler.save_session(session)

    def delete_session(self, session_name: str) -> None:
        """
        Delete the session with name `session_name`.
        """
        self.file_handler.delete_session(session_name)
        session = self._get_session_by_name(session_name)
        if session:
            self.multiplexer.kill_session(session)

    def rename_session(self, session_name: str, new_name: str) -> None:
        """
        Rename the session with the name `session_name` to `new_name`.
        """
        try:
            self.file_handler.load_session(new_name)
            raise ValueError(f"Saved session with name {new_name} already exists")
        except FileNotFoundError:
            pass
        session = self._get_session_by_name(session_name)
        if session:
            self.multiplexer.rename_session(session, new_name)
        else:
            session = self.file_handler.load_session(session_name)
            session.name = new_name
        self.file_handler.save_session(session)
        self.file_handler.delete_session(session_name)

    def _get_session_by_name(self, session_name: str) -> Optional[JmuxSession]:
        session = next(
            (
                self.multiplexer.get_session(session_label.id)
                for session_label in self.multiplexer.list_sessions()
                if session_label.name == session_name
            ),
            None,
        )
        return session
