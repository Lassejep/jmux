import abc
from typing import Optional


class TerminalMultiplexerAPI(abc.ABC):
    """
    Abstract class for a terminal multiplexer API.
    Responsible for communicating with the terminal multiplexer.
    """

    @abc.abstractmethod
    def get(self, key: str, target: str = "") -> str:
        pass

    @abc.abstractmethod
    def create_session(self, session_name: str) -> None:
        pass

    @abc.abstractmethod
    def create_window(self, window_name: str, target: str) -> None:
        pass

    @abc.abstractmethod
    def create_pane(self, target: str) -> None:
        pass

    @abc.abstractmethod
    def focus_element(self, target: str) -> None:
        pass

    @abc.abstractmethod
    def kill_element(self, target: str) -> None:
        pass

    @abc.abstractmethod
    def change_window_layout(self, layout: str, target: str) -> None:
        pass

    @abc.abstractmethod
    def change_pane_directory(self, directory: str, target: str) -> None:
        pass


class TmuxAPI(TerminalMultiplexerAPI):
    """
    Implementation of the TerminalMultiplexerAPI
    for the Tmux terminal multiplexer.
    """

    def __init__(self, shell) -> None:
        self.shell = shell

    def get(self, keys: list[str],
            target: Optional[str] = None) -> dict[str, str]:
        """
        Get the values of `keys` from the `target` pane, window, or session.
        """
        formatted_keys = self._format_keys(keys)
        command = ["tmux", "display-message",
                   "-t", target, "-p", formatted_keys]
        response = self.shell.run(command, capture_output=True).stdout
        return self._format_response(keys, response)

    def _format_keys(self, keys: list[str]) -> str:
        if not keys:
            raise ValueError("Keys cannot be empty")
        keys = [f"#{{{key}}}" for key in keys]
        return "".join(keys)

    def _format_response(self, keys: list[str],
                         response: str) -> dict[str, str]:
        if response == "":
            raise ValueError("Invalid key")
        response = response.split(":")
        for i, value in enumerate(response):
            if value == "":
                raise ValueError(f"Invalid key: {keys[i]}")
        return dict(zip(keys, response))

    def create_session(self, session_name: str) -> None:
        """
        Create a new session with the name `session_name`.
        """
        if not self._is_valid_name(session_name):
            raise ValueError("Session name cannot be empty")
        command = ["tmux", "new-session", "-d", "-s", session_name]
        self.shell.run(command)

    def _is_valid_name(self, name: str) -> bool:
        illegal_chars = [".", ":", "\t", "\n"]
        if name.isspace() or not name:
            return False
        return all(char not in name for char in illegal_chars)

    def create_window(self, window_name: str, target: str) -> None:
        pass

    def create_pane(self, target: str) -> None:
        pass

    def focus_element(self, target: str) -> None:
        pass

    def kill_element(self, target: str) -> None:
        pass

    def change_window_layout(self, layout: str, target: str) -> None:
        pass

    def change_pane_directory(self, directory: str, target: str) -> None:
        pass
