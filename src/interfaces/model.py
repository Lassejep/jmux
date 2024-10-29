from abc import ABC, abstractmethod
from typing import List

from src.data_models import SessionLabel
from src.interfaces.file_handler import FileHandler
from src.interfaces.multiplexer import Multiplexer


class Model(ABC):
    @abstractmethod
    def __init__(self, multiplexer: Multiplexer, file_handler: FileHandler) -> None:
        """
        Abstract class for the model of the appllication.
        Responsible for communicating with the presenter.
        """
        raise NotImplementedError

    @abstractmethod
    def create_session(self, session_name: str) -> None:
        """
        Create a new session in the terminal multiplexer with the name `session_name`.
        """
        raise NotImplementedError

    def save_session(self, label: SessionLabel) -> None:
        """
        Save the session with `label` to a file.
        """
        raise NotImplementedError

    @abstractmethod
    def load_session(self, label: SessionLabel) -> None:
        """
        Load the session with `label` from a file.
        """
        raise NotImplementedError

    @abstractmethod
    def kill_session(self, label: SessionLabel) -> None:
        """
        Kills the session with `label` in the terminal multiplexer.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_session(self, label: SessionLabel) -> None:
        """
        Delete the session with `label` from the file system.
        """
        raise NotImplementedError

    @abstractmethod
    def rename_session(self, label: SessionLabel, new_name: str) -> None:
        """
        Rename the session with `label` to `new_name` in the multiplexer
        and in the file system.
        """
        raise NotImplementedError

    @abstractmethod
    def list_saved_sessions(self) -> List[SessionLabel]:
        """
        List all sessions saved in the file system.
        """
        raise NotImplementedError

    def list_running_sessions(self) -> List[SessionLabel]:
        """
        List all sessions currently running in the terminal multiplexer.
        """
        raise NotImplementedError

    @abstractmethod
    def get_active_session(self) -> SessionLabel:
        """
        Get the currently active/focused session in the terminal multiplexer.
        """
        raise NotImplementedError
