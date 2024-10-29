from typing import List

from src.data_models import SessionLabel
from src.interfaces import FileHandler, Model, Multiplexer


class JmuxModel(Model):
    def __init__(self, multiplexer: Multiplexer, file_handler: FileHandler) -> None:
        """
        Class for the model of the jmux application.
        Responsible for communicating with the presenter.
        Implements the Model interface.
        """
        if not multiplexer or not isinstance(multiplexer, Multiplexer):
            raise ValueError("Invalid multiplexer value")
        self.multiplexer = multiplexer
        if not file_handler or not isinstance(file_handler, FileHandler):
            raise ValueError("Invalid file_handler value")
        self.file_handler = file_handler

    def create_session(self, session_name: str) -> None:
        """
        Create a new session in the terminal multiplexer with the name `session_name`.
        """
        self.multiplexer.create_new_session(session_name)

    def save_session(self, label: SessionLabel) -> None:
        """
        Save the session with `label` to a file.
        """
        session = self.multiplexer.get_session(label)
        self.file_handler.save_session(session)

    def load_session(self, label: SessionLabel) -> None:
        """
        Load the session with `label` from a file.
        """
        if label in self.multiplexer.list_sessions():
            self.multiplexer.focus_session(label)
            return
        session = self.file_handler.load_session(label.name)
        self.multiplexer.create_session(session)
        self.file_handler.save_session(session)

    def kill_session(self, label: SessionLabel) -> None:
        """
        Kills the session with `label` in the terminal multiplexer.
        """
        if label not in self.multiplexer.list_sessions():
            raise ValueError("Session does not exist")
        if label == self.multiplexer.get_current_session_label():
            raise ValueError("Cannot kill the active session")
        self.multiplexer.kill_session(label)

    def delete_session(self, label: SessionLabel) -> None:
        """
        Delete the session with `label` from the file system.
        """
        if label not in self.file_handler.list_sessions():
            raise ValueError("Session does not exist")
        self.file_handler.delete_session(label.name)

    def rename_session(self, label: SessionLabel, new_name: str) -> None:
        """
        Rename the session with `label` to `new_name` in the multiplexer
        and in the file system.
        """
        if not new_name or new_name.isspace():
            raise ValueError("Invalid session name")
        if label in self.file_handler.list_sessions():
            session = self.file_handler.load_session(label.name)
            session.name = new_name
            self.file_handler.save_session(session)
            self.file_handler.delete_session(label.name)
        if label in self.multiplexer.list_sessions():
            self.multiplexer.rename_session(label, new_name)

    def list_saved_sessions(self) -> List[SessionLabel]:
        """
        List all sessions saved in the file system.
        """
        return self.file_handler.list_sessions()

    def list_running_sessions(self) -> List[SessionLabel]:
        """
        List all sessions currently running in the terminal multiplexer.
        """
        return self.multiplexer.list_sessions()

    def get_active_session(self) -> SessionLabel:
        """
        Get the active/focused session in the terminal multiplexer.
        """
        return self.multiplexer.get_current_session_label()
