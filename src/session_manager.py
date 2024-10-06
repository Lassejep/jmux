import json
import pathlib
from dataclasses import asdict

from src.models import JmuxSession
from src.multiplexer import Multiplexer
from src.serialization import dict_to_JmuxSession


class SessionManager:
    """
    Manage terminal multiplexer sessions.
    """

    def __init__(self, save_folder: pathlib.Path, multiplexer: Multiplexer) -> None:
        if not save_folder or not isinstance(save_folder, pathlib.Path):
            raise ValueError("Invalid save_folder value")
        if not save_folder.exists():
            raise ValueError("The specified folder does not exist")
        self.save_folder = save_folder

        if not multiplexer or not isinstance(multiplexer, Multiplexer):
            raise ValueError("Invalid multiplexer value")
        self.multiplexer = multiplexer

    def save_current_session(self) -> None:
        """
        Save the current session to a file in the specified folder.
        the `save_folder` parameter should be a pathlib.Path object and should point to
        a valid directory where the session file will be saved.
        """
        current_session_label = self.multiplexer.get_current_session_id()
        self.save_session(current_session_label.id)

    def save_session(self, session_id: str) -> None:
        """
        Save the session with the id `session_id` to a file in the specified folder.
        """
        session = self.multiplexer.get_session(session_id)
        save_file = self._create_save_file(session.name)
        with save_file.open("w") as file:
            json.dump(asdict(session), file, indent=4)

    def _create_save_file(self, session_name: str) -> pathlib.Path:
        """
        Create a file path for the session.
        """
        save_file = self.save_folder / session_name
        if not save_file.exists():
            save_file.touch()
        return save_file

    def load_session(self, file_path: pathlib.Path) -> JmuxSession:
        """
        Load a session from a file.
        """
        return JmuxSession("test", "test", [])
