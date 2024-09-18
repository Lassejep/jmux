import subprocess
import abc
from typing import List


class TerminalMultiplexerAPI(abc.ABC):
    @abc.abstractmethod
    def get(self, key: str, target: str = "") -> str:
        """
        Get the value of a `key` from the `target` pane, window, or session.
        """
        pass

    @abc.abstractmethod
    def send_cmd(self, command: str, target: str) -> str:
        """
        Send a `command` to the `target` pane, window, or session.
        Returns the output of the `command`.
        """
        pass

    @abc.abstractmethod
    def create_session(self, session_name: str) -> None:
        """
        Create a new session with the name `session_name`.
        """
        pass

    @abc.abstractmethod
    def create_window(self, window_name: str, session_name: str) -> None:
        """
        Create a new window with the name `window_name`,
        in a session with the name `session_name`.
        """
        pass

    @abc.abstractmethod
    def create_pane(self, target: str) -> None:
        """
        Create a new pane in the `target` window.
        """
        pass

    @abc.abstractmethod
    def focus_session(self, target: str) -> None:
        """
        Focus on the `target` session.
        """
        pass

    @abc.abstractmethod
    def focus_window(self, target: str) -> None:
        """
        Focus on the `target` window.
        """
        pass

    @abc.abstractmethod
    def focus_pane(self, target: str) -> None:
        """
        Focus on the `target` pane.
        """
        pass

    @abc.abstractmethod
    def kill_session(self, target: str) -> None:
        """
        Kill the `target` session.
        """
        pass

    @abc.abstractmethod
    def kill_window(self, target: str) -> None:
        """
        Kill the `target` window.
        """
        pass

    @abc.abstractmethod
    def kill_pane(self, target: str) -> None:
        """
        Kill the `target` pane.
        """
        pass

    @abc.abstractmethod
    def change_window_layout(self, layout: str, target: str) -> None:
        """
        Change the `layout` of the `target` window.
        """
        pass

    @abc.abstractmethod
    def change_pane_directory(self, directory: str, target: str) -> None:
        """
        Change the current `directory` of the `target` pane.
        """
        pass


class TmuxApi(TerminalMultiplexerApi):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TmuxApi, cls).__new__(cls)
            cls._instance.tmux_bin = cls._instance._find_tmux_bin()
        return cls._instance

    class TmuxError(Exception):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    class TmuxNotFoundError(TmuxError):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    def run(self, cmd: List[str]) -> str:
        try:
            cmd.insert(0, self.tmux_bin)
            return subprocess.check_output(cmd, text=True).strip()
        except subprocess.CalledProcessError as err:
            raise self.TmuxError(f"Failed to run {err}")

    def _find_tmux_bin(self) -> str:
        try:
            return subprocess.check_output(["which", "tmux"],
                                           text=True).strip()
        except subprocess.CalledProcessError as err:
            raise self.TmuxNotFoundError("Tmux not found") from err

    def get(self, keys: str | List[str], target: str = "") -> str:
        cmd = ["display-message"]
        if target:
            cmd.extend(["-t", target])
        if type(keys) is not list:
            keys = [keys]
        keystr = ""
        for key in keys:
            keystr += f"#{{{key}}}:"
        cmd.extend(["-p", f"{keystr[:-1]}"])
        output = self.run(cmd).split(":")
        if len(output) == 1:
            return output[0]
        return output

    def send_keys(self, keys: str | List[str], target: str) -> None:
        if type(keys) is not list:
            keys = [keys]
        wait_cmd = f"; {self.tmux_bin} wait-for -S jmux_ready"
        cmd = ["send-keys", "-t", target, *keys, wait_cmd, "C-m", "C-l"]
        confirm_cmd = [self.tmux_bin, "wait-for", "jmux_ready"]
        try:
            confirm_proc = subprocess.Popen(confirm_cmd)
            self.run(cmd)
        except self.TmuxError:
            confirm_proc.kill()
            raise self.TmuxError("Failed to send keys" + keys)
        try:
            confirm_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            confirm_proc.kill()
