import json
import pathlib
from dataclasses import asdict
from typing import List

from src.data_models import JmuxPane, JmuxSession, JmuxWindow, SessionLabel
from src.interfaces import FileHandler


class JsonHandler(FileHandler):
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
        session = self._serialize_session(session_data)
        return session

    def delete_session(self, session_name: str) -> None:
        """
        Delete the session with the name `session_name`.
        """
        session_file = self.sessions_folder / f"{session_name}.json"
        if not session_file.exists():
            raise FileNotFoundError(f"Session file {session_name} does not exist")
        session_file.unlink()

    def list_sessions(self) -> List[SessionLabel]:
        """
        Get a list of session labels of all the saved sessions.
        """
        session_files = self.sessions_folder.glob("*.json")
        session_names = [session_file.stem for session_file in session_files]
        labels = []
        for session_name in session_names:
            try:
                session = self.load_session(session_name)
                labels.append(SessionLabel(session.id, session.name))
            except FileNotFoundError:
                pass
        return labels

    def _serialize_window(self, window: dict) -> JmuxWindow:
        window["panes"] = [JmuxPane(**pane_data) for pane_data in window["panes"]]
        return JmuxWindow(**window)

    def _serialize_session(self, session: dict) -> JmuxSession:
        session["windows"] = [
            self._serialize_window(window_data) for window_data in session["windows"]
        ]
        return JmuxSession(**session)
