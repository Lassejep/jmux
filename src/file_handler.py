import json
import pathlib
from dataclasses import asdict

from src.jmux_session import JmuxSession
from src.serialization import dict_to_JmuxSession


class FileHandler:
    def __init__(self, sessions_folder: pathlib.Path) -> None:
        """
        Handle file operations.
        """
        if not sessions_folder or not isinstance(sessions_folder, pathlib.Path):
            raise ValueError("Invalid sessions_folder value")
        if not sessions_folder.exists():
            raise ValueError("The specified folder does not exist")
        self.sessions_folder = sessions_folder

    def save_session(self, session: JmuxSession) -> None:
        """
        Save the session to a file with the name of the session in the sessions folder.
        """
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
            session_data = json.load(file)
        session = dict_to_JmuxSession(session_data)
        return session

    def delete_session(self, session_name: str) -> None:
        """
        Delete the session with the name `session_name`.
        """
        session_file = self.sessions_folder / f"{session_name}.json"
        if not session_file.exists():
            raise FileNotFoundError(f"Session file {session_name} does not exist")
        session_file.unlink()
