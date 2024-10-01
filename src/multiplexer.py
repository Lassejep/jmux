import abc


class TerminalMultiplexerClient(abc.ABC):
    """
    Abstract class for a terminal multiplexer API.
    Responsible for communicating with the terminal multiplexer.
    """

    @abc.abstractmethod
    def is_running(self) -> bool:
        """
        Check if the terminal multiplexer is running.
        """
        pass

    @abc.abstractmethod
    def get(self, key: list[str], target: str = "") -> dict[str, str]:
        """
        Get the values of `keys` from the `target` pane, window, or session.
        """
        pass

    @abc.abstractmethod
    def create_session(self, session_name: str) -> str:
        """
        Create a new session with the name `session_name`.
        Returns the id of the created session.
        """
        pass

    @abc.abstractmethod
    def create_window(self, window_name: str, target: str) -> str:
        """
        Create a new window with the name `window_name`,
        in the `target` session. Returns the id of the created window.
        """
        pass

    @abc.abstractmethod
    def create_pane(self, target: str) -> str:
        """
        Create a new pane in the `target` window.
        Returns the id of the created pane.
        """
        pass

    @abc.abstractmethod
    def focus_element(self, target: str) -> None:
        """
        Focus on the `target` pane, window, or session.
        """
        pass

    @abc.abstractmethod
    def kill_element(self, target: str) -> None:
        """
        Kill the `target` pane, window, or session.
        """
        pass

    @abc.abstractmethod
    def change_window_layout(self, layout: str, target: str) -> None:
        """
        Change the layout of the `target` window.
        """
        pass

    @abc.abstractmethod
    def change_pane_directory(self, directory: str, target: str) -> None:
        """
        Change the directory of the `target` pane.
        """
        pass
