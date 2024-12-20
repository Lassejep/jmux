from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from src.data_models import JmuxSession, SessionLabel


class FileHandler(ABC):
    @abstractmethod
    def __init__(self, sessions_folder: Path) -> None:
        """
        Abstract class for a file handler.
        Responsible for reading and writing sessions to files.
        """
        raise NotImplementedError

    @abstractmethod
    def save_session(self, session: JmuxSession) -> None:
        """
        Save the session to a file with the name of the session in the sessions folder.
        """
        raise NotImplementedError

    @abstractmethod
    def load_session(self, session_name: str) -> JmuxSession:
        """
        Load the session with the name `session_name` from the sessions folder.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_session(self, session_name: str) -> None:
        """
        Delete the session file with the name `session_name`.
        """
        raise NotImplementedError

    @abstractmethod
    def list_sessions(self) -> List[SessionLabel]:
        """
        Get a list of session labels of all the saved sessions.
        """
        raise NotImplementedError
