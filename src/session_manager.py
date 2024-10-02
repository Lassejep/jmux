import pathlib
import json
from dataclasses import asdict

from src.elements import JmuxLoader


class SessionManager:
    """
    Manage terminal multiplexer sessions.
    """

    def __init__(self, jmux_loader: JmuxLoader) -> None:
        self.jmux_loader = jmux_loader
        self._check_jmux_loader()

    def _check_jmux_loader(self) -> None:
        if self.jmux_loader is None or not isinstance(
                self.jmux_loader, JmuxLoader):
            raise ValueError("Invalid JmuxLoader")

    def save_session(self, save_file: pathlib.Path) -> None:
        """
        Save the current session to `file_path`.
        """
        if not isinstance(save_file, pathlib.Path):
            raise TypeError("Invalid file path")

        if not save_file.exists():
            save_file.touch()

        current_session = self.jmux_loader.load()
        session_dict = asdict(current_session)
        with save_file.open("w") as file:
            json.dump(session_dict, file, indent=4)
