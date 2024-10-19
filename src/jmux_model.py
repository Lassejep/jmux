from typing import List

from src.file_handler import FileHandler
from src.interfaces import Model, Multiplexer
from src.jmux_session import SessionLabel


class JmuxModel(Model):
    def __init__(self, multiplexer: Multiplexer, file_handler: FileHandler) -> None:
        """
        Class for the model of the jmux application.
        Responsible for communicating with the presenter.
        Implements the Model interface.
        """
        self.multiplexer = multiplexer
        self.file_handler = file_handler

    def create_session(self, session_name: str) -> None:
        """
        Create a new session in the terminal multiplexer with the name `session_name`.
        """
        raise NotImplementedError
        pass

    def save_session(self, label: SessionLabel) -> None:
        """
        Save the session with `label` to a file.
        """
        session = self.multiplexer.get_session(label.id)
        self.file_handler.save_session(session)

    def load_session(self, label: SessionLabel) -> None:
        """
        Load the session with `label` from a file.
        """
        session = self.file_handler.load_session(label.name)
        self.multiplexer.create_session(session)
        self.file_handler.save_session(session)

    def kill_session(self, label: SessionLabel) -> None:
        """
        Kills the session with `label` in the terminal multiplexer.
        """
        session = self.multiplexer.get_session(label.id)
        self.multiplexer.kill_session(session)

    def delete_session(self, label: SessionLabel) -> None:
        """
        Delete the session with `label` from the file system.
        """
        self.file_handler.delete_session(label.name)

    def rename_session(self, label: SessionLabel, new_name: str) -> None:
        """
        Rename the session with `label` to `new_name` in the multiplexer
        and in the file system.
        """
        session = self.multiplexer.get_session(label.id)
        self.multiplexer.rename_session(session, new_name)
        self.file_handler.save_session(session)
        self.file_handler.delete_session(label.name)

    def list_saved_sessions(self) -> List[SessionLabel]:
        """
        List all sessions saved in the file system.
        """
        raise NotImplementedError
        return []

    def list_running_sessions(self) -> List[SessionLabel]:
        """
        List all sessions currently running in the terminal multiplexer.
        """
        return self.multiplexer.list_sessions()

    def get_active_session(self) -> SessionLabel:
        """
        Get the active/focused session in the terminal multiplexer.
        """
        return self.multiplexer.get_current_session_id()
