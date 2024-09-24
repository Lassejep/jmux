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
    def create_session(self, session_name: str) -> str:
        pass

    @abc.abstractmethod
    def create_window(self, window_name: str, target: str) -> str:
        pass

    @abc.abstractmethod
    def create_pane(self, target: str) -> str:
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
        response = self.shell.run(
            command, capture_output=True, text=True).stdout
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

    def create_session(self, session_name: str) -> str:
        """
        Create a new session with the name `session_name`.
        Returns the id of the created session.
        """
        if not self._is_valid_name(session_name):
            raise ValueError("Invalid session name")
        command = ["tmux", "new-session", "-ds",
                   session_name, "-PF", "#{session_id}"]
        response = self.shell.run(command, capture_output=True, text=True)
        if response.returncode != 0:
            raise self.shell.CalledProcessError(response.returncode, command)
        return response.stdout.strip()

    def create_window(self, window_name: str, target: str) -> str:
        """
        Create a new window with the name `window_name`,
        in the `target` session.
        Returns the id of the created window.
        """
        if not self._is_valid_name(window_name):
            raise ValueError("Invalid window name")
        if not self._is_valid_target(target):
            raise ValueError("Invalid target")
        command = ["tmux", "new-window", "-t", target, "-n", window_name,
                   "-PF", "#{window_id}"]
        response = self.shell.run(command, capture_output=True)
        if response.returncode != 0:
            raise ValueError("Invalid target")
        return response.stdout.strip()

    def _is_valid_name(self, name: str) -> bool:
        illegal_chars = {".", ":", "\t", "\n", "$", "@", "%"}
        if name.isspace() or not name:
            return False
        return all(char not in name for char in illegal_chars)

    def create_pane(self, target: str) -> str:
        """
        Create a new pane in the `target` window.
        Returns the id of the created pane.
        """
        if not self._is_valid_target(target):
            raise ValueError("Invalid target")
        command = ["tmux", "split-window", "-t", target, "-PF", "#{pane_id}"]
        response = self.shell.run(command, capture_output=True)
        if response.returncode != 0:
            raise ValueError("Invalid target")
        return response.stdout.strip()

    def focus_element(self, target: str) -> None:
        """
        Focus on the `target` pane, window, or session.
        """
        if not self._is_valid_target(target):
            raise ValueError("Invalid target")
        match target[0]:
            case "$":
                action = "switch"
            case "@":
                action = "select-window"
            case "%":
                action = "select-pane"
        command = ["tmux", action, "-t", target]
        self.shell.run(command)

    def kill_element(self, target: str) -> None:
        pass

    def change_window_layout(self, layout: str, target: str) -> None:
        pass

    def change_pane_directory(self, directory: str, target: str) -> None:
        pass

    def _is_valid_target(self, target: str) -> bool:
        valid_chars = {"$", "@", "%"}
        return any(target.startswith(char) for char in valid_chars)
