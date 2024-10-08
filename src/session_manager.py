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

    def __init__(self, sessions_folder: pathlib.Path, multiplexer: Multiplexer) -> None:
        if not sessions_folder or not isinstance(sessions_folder, pathlib.Path):
            raise ValueError("Invalid sessions_folder value")
        if not sessions_folder.exists():
            raise ValueError("The specified folder does not exist")
        self.sessions_folder = sessions_folder

        if not multiplexer or not isinstance(multiplexer, Multiplexer):
            raise ValueError("Invalid multiplexer value")
        self.multiplexer = multiplexer

    def save_current_session(self) -> None:
        """
        Save the current session to a file in the specified folder.
        the `sessions_folder` parameter should be a pathlib.Path object and should point
        to a valid directory where the session file will be saved.
        """
        current_session_label = self.multiplexer.get_current_session_id()
        self.save_session(current_session_label.id)

    def save_session(self, session_id: str) -> None:
        """
        Save the session with the id `session_id` to a file in the sessions folder.
        """
        session = self.multiplexer.get_session(session_id)
        save_file = self.sessions_folder / f"{session.name}.json"
        if not save_file.exists():
            save_file.touch()
        with save_file.open("w") as file:
            json.dump(asdict(session), file, indent=4)

    def load_session(self, session_name: str) -> JmuxSession:
        """
        Load the session with the name `session_name` from the sessions folder.
        """
        session_file = self.sessions_folder / f"{session_name}.json"
        if not session_file.exists():
            raise FileNotFoundError(f"Session file {session_name} does not exist")
        with session_file.open("r") as file:
            session_data = json.load(file, indent=4)
        session = dict_to_JmuxSession(session_data)
        return session
