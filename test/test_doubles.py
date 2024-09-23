from typing import Any


class SubprocessTestDouble:
    """A test double for Tmux"""

    def returns_response(self, response: Any, stderr: str = "",
                         returncode: int = 0) -> Any:
        """Set the response that run will return"""
        self.response = CompletedProcessTestDouble(
            response, stderr, returncode)

    def run(self, command: list[str], **kwargs) -> Any:
        """A test double for subprocess.run"""
        return self.response(command)


class CompletedProcessTestDouble:
    """A test double for subprocess.CompletedProcess"""

    def __init__(self, stdout: Any, stderr: Any, returncode: Any) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    def __call__(self, args: list[str]) -> Any:
        self.args = args
        if args[0] != "tmux":
            raise ValueError("Only tmux commands are supported")
        if args[1] == "new-session":
            self.stdout += args[4]
        if args[1] == "new-window":
            self.stdout += args[5]
        return self
