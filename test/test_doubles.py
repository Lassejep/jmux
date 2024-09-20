from typing import Any


class SubprocessTestDouble:
    """A test double for Tmux"""

    def returns_response(self, response: Any) -> Any:
        """Set the response that run will return"""
        self.response = response

    def run(self, command: list[str], **kwargs) -> Any:
        """A test double for subprocess.run"""
        return CompletedProcessTestDouble(command, 0, self.response, "")


class CompletedProcessTestDouble:
    """A test double for subprocess.CompletedProcess"""

    def __init__(self, args: list[str], returncode: int,
                 stdout: Any, stderr: Any) -> None:
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
