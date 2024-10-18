import abc


class Model(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        """
        Abstract class for the model of the appllication.
        Responsible for communicating with the presenter.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def create_session(self, session_name: str) -> None:
        """
        Create a new session with the name `session_name`.
        """
        raise NotImplementedError

    def save_session(self, session_name: str) -> None:
        """
        Save the session with the name `session_name`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def load_session(self, session_name: str) -> None:
        """
        Load a session with the name `session_name`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def kill_session(self, session_name: str) -> None:
        """
        Kill a session with the name `session_name`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_session(self, session_name: str) -> None:
        """
        Delete a session with the name `session_name`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def rename_session(self, session_name: str, new_name: str) -> None:
        """
        Rename a session with the name `session_name` to `new_name`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list_sessions(self) -> None:
        """
        List all the sessions.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_active_session(self) -> None:
        """
        Get the currently active session.
        """
        raise NotImplementedError
