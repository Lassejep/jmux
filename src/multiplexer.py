import abc
from typing import List

from src.models import JmuxSession, SessionLabel


class Multiplexer(abc.ABC):
    """
    Abstract class for a terminal multiplexer API.
    Responsible for communicating with the terminal multiplexer.
    """

    @abc.abstractmethod
    def is_running(self) -> bool:
        """
        Check if the terminal multiplexer is running.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list_sessions(self) -> List[SessionLabel]:
        """
        Get a list of all the currently running sessions.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_current_session_id(self) -> SessionLabel:
        """
        Get the name and id of the currently running session.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_session(self, session_id: str) -> JmuxSession:
        """
        Get the data of the session with the id `session_id`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_session(self, session: JmuxSession) -> None:
        """
        Create a new session with the data in `session`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def kill_session(self, session_id: str) -> None:
        """
        Kill the session with the id `session_id`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def rename_session(self, session: JmuxSession, new_name: str) -> None:
        """
        Rename the sessions name to `new_name` and update the session object.
        """
        raise NotImplementedError
