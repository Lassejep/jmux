import pathlib
import json
from dataclasses import asdict

from src.elements import JmuxLoader, JmuxBuilder
from src.models import JmuxSession, JmuxWindow, JmuxPane


class SessionManager:
    """
    Manage terminal multiplexer sessions.
    """

    def __init__(self, jmux_loader: JmuxLoader,
                 jmux_builder: JmuxBuilder) -> None:
        self.jmux_loader = jmux_loader
        if self.jmux_loader is None or not isinstance(
                self.jmux_loader, JmuxLoader):
            raise ValueError("Invalid JmuxLoader")

        self.jmux_builder = jmux_builder
        if self.jmux_builder is None or not isinstance(
                self.jmux_builder, JmuxBuilder):
            raise ValueError("Invalid JmuxBuilder")

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

    def load_session(self, load_file: pathlib.Path) -> None:
        """
        Load the session from `file_path`.
        """
        if not isinstance(load_file, pathlib.Path):
            raise TypeError("Invalid file path")

        if not load_file.exists():
            raise FileNotFoundError("File does not exist")

        with load_file.open("r") as file:
            session_data = json.load(file)
        session = self._deserialize_session(session_data)
        self.jmux_builder.build(session)

    def _deserialize_session(self, session_data: dict) -> JmuxSession:
        session_data["windows"] = [self._deserialize_window(
            window) for window in session_data["windows"]]
        session = JmuxSession(**session_data)
        return session

    def _deserialize_window(self, window_data: dict) -> JmuxWindow:
        window_data["panes"] = [JmuxPane(**pane)
                                for pane in window_data["panes"]]
        window = JmuxWindow(**window_data)
        return window
