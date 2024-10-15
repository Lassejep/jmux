import json
import pathlib
from dataclasses import asdict
from typing import Optional

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
        session = self.multiplexer.get_session(current_session_label.id)
        self.save_session(session)

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
        if not all(
            [
                session_name != session_label.name
                for session_label in self.multiplexer.list_sessions()
            ]
        ):
            raise ValueError(f"Session {session_name} already exists")
        with session_file.open("r") as file:
            session_data = json.load(file)
        session = dict_to_JmuxSession(session_data)
        self.multiplexer.create_session(session)
        return session

    def delete_session(self, session_name: str) -> None:
        """
        Delete the session with the name `session_name`.
        """
        session_file = self.sessions_folder / f"{session_name}.json"
        if not session_file.exists():
            raise FileNotFoundError(f"Session file {session_name} does not exist")
        session_file.unlink()
        session = self._get_session_by_name(session_name)
        if session:
            self.multiplexer.kill_session(session)

    def rename_session(self, session_name: str, new_name: str) -> None:
        """
        Rename the session with the name `session_name` to `new_name`.
        """
        session_file = self.sessions_folder / f"{session_name}.json"
        if not session_file.exists():
            raise FileNotFoundError(f"Session file {session_name} does not exist")
        new_session_file = self.sessions_folder / f"{new_name}.json"
        if new_session_file.exists():
            raise ValueError(f"Session {new_name} already exists")
        session_file.rename(new_session_file)
        session = self._get_session_by_name(session_name)
        if session:
            self.multiplexer.rename_session(session, new_name)

    def _get_session_by_name(self, session_name: str) -> Optional[JmuxSession]:
        session = next(
            (
                self.multiplexer.get_session(session_label.id)
                for session_label in self.multiplexer.list_sessions()
                if session_label.name == session_name
            ),
            None,
        )
        return session
