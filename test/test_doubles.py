from typing import Any


class SubprocessTestDouble:
    """A test double for Tmux"""

    def returns_response(self, response: Any, stderr: str = "",
                         returncode: int = 0) -> Any:
        """Set the response that run will return"""
        self.response = CompletedProcessTestDouble(
            response, stderr, returncode)
        self.tmux = TmuxTestDouble(self.response)

    def run(self, command: list[str], **kwargs) -> Any:
        """A test double for subprocess.run"""
        if command[0] == "tmux":
            return self.tmux(command)
        return self.response(command)


class CompletedProcessTestDouble:
    """A test double for subprocess.CompletedProcess"""

    def __init__(self, stdout: Any, stderr: Any, returncode: Any) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    def __call__(self, args: list[str]) -> Any:
        self.args = args
        return self


class TmuxTestDouble:
    def __init__(self, response: CompletedProcessTestDouble) -> None:
        self.sessions = []
        self.windows = []
        self.response = response

    def __call__(self, args: list[str]) -> CompletedProcessTestDouble:
        tmux_action = args[1]
        match tmux_action:
            case "list-sessions":
                session_names = "\n".join(self.sessions) + "\n"
                self.response.stdout = session_names
            case "list-windows":
                window_names = "\n".join(self.windows) + "\n"
                self.response.stdout = window_names
            case "new-session":
                self.sessions.append(args[3])
            case "new-window":
                self.windows.append(args[5])
            case "switch-client" | "select-window" | "select-pane":
                self.response.stdout = "1"
            case "kill-session":
                self.sessions = []
            case "kill-window":
                self.windows = []
        return self.response(args)
