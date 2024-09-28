import abc
import os
from typing import Optional


class TerminalMultiplexerAPI(abc.ABC):
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


class TmuxAPI(TerminalMultiplexerAPI):
    """
    Implementation of the TerminalMultiplexerAPI
    for the Tmux terminal multiplexer.
    """

    def __init__(self, shell) -> None:
        self.shell = shell
        self._bin = self._get_binary()
        if not self._bin:
            raise EnvironmentError("Tmux not found")

    def _get_binary(self) -> str:
        command = ["which", "tmux"]
        response = self.shell.run(command, capture_output=True, text=True)
        if response.returncode != 0:
            raise self.shell.CalledProcessError(
                response.returncode, "which tmux")
        return response.stdout.strip()

    def is_running(self) -> bool:
        """
        Check if the Tmux terminal multiplexer is running.
        """
        env = os.environ.copy()
        if "TMUX" in env and env["TMUX"] != "":
            return True
        return False

    def get(self, keys: list[str],
            target: Optional[str] = None) -> dict[str, str]:
        """
        Get the values of `keys` from the `target` pane, window, or session.
        """
        command = [self._bin, "display-message"]
        if target:
            if not self._is_valid_target(target):
                raise ValueError("Invalid target")
            command.extend(["-t", target])
        formatted_keys = self._format_keys(keys)
        command.extend(["-p", formatted_keys])
        response = self.shell.run(command, capture_output=True, text=True)
        if response.returncode != 0:
            raise self.shell.CalledProcessError(response.returncode, command)
        return self._format_response(keys, response.stdout)

    def _format_keys(self, keys: list[str]) -> str:
        if not keys:
            raise ValueError("Keys cannot be empty")
        keys = [f"#{{{key}}}:" for key in keys]
        return "".join(keys)

    def _format_response(self, keys: list[str],
                         response: str) -> dict[str, str]:
        responses = response.split(":")[:-1]
        for i, value in enumerate(responses):
            if value.strip() == "":
                raise ValueError(f"Invalid key: {keys[i]}")
        return dict(zip(keys, responses))

    def create_session(self, session_name: str) -> str:
        """
        Create a new session with the name `session_name`.
        Returns the id of the created session.
        """
        if not self._is_valid_name(session_name):
            raise ValueError("Invalid session name")
        command = [self._bin, "new-session", "-ds",
                   session_name, "-PF", "#{session_id}"]
        response = self.shell.run(
            command, capture_output=True, text=True, check=True)
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
        command = [self._bin, "new-window", "-t", target, "-kn", window_name,
                   "-PF", "#{window_id}"]
        response = self.shell.run(
            command, capture_output=True, text=True, check=True)
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
        command = [self._bin, "split-window",
                   "-t", target, "-PF", "#{pane_id}"]
        response = self.shell.run(
            command, capture_output=True, text=True, check=True)
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
        command = [self._bin, action, "-t", target]
        self.shell.run(command)

    def kill_element(self, target: str) -> None:
        """
        Kill the `target` pane, window, or session.
        """
        if not self._is_valid_target(target):
            raise ValueError("Invalid target")
        match target[0]:
            case "$":
                action = "kill-session"
            case "@":
                action = "kill-window"
            case "%":
                action = "kill-pane"
        command = [self._bin, action, "-t", target]
        self.shell.run(command)

    def change_window_layout(self, layout: str, target: str) -> None:
        """
        Change the layout of the `target` window.
        """
        if not layout:
            raise ValueError("Layout cannot be empty")
        if not self._is_valid_target(target):
            raise ValueError("Invalid target")
        command = [self._bin, "select-layout", "-t", target, layout]
        err = self.shell.run(command, capture_output=True, text=True).stderr
        if "invalid layout" in err:
            raise ValueError("Invalid layout")
        elif err != "":
            raise self.shell.CalledProcessError(err)

    def change_pane_directory(self, directory: str, target: str) -> None:
        """
        Change the directory of the `target` pane.
        """
        if not directory:
            raise ValueError("Directory cannot be empty")
        if not self._is_valid_target(target):
            raise ValueError("Invalid target")
        command = [self._bin, "send-keys", "-t",
                   target, f"cd {directory}", "C-m", "C-l"]
        err = self.shell.run(command, capture_output=True, text=True).stderr
        if "can't find pane" in err:
            raise ValueError("Invalid target")
        elif err != "":
            raise self.shell.CalledProcessError(err)

    def _is_valid_target(self, target: str) -> bool:
        if not target:
            return False
        valid_chars = {"$", "@", "%"}
        return any(target.startswith(char) for char in valid_chars)
