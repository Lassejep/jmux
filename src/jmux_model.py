from typing import List

from src.jmux_session import SessionLabel
from src.model import Model


class JmuxModel(Model):
    def __init__(self):
        pass

    def create_session(self, session_name: str) -> None:
        pass

    def save_session(self, session_name: str) -> None:
        pass

    def load_session(self, session_name: str) -> None:
        pass

    def kill_session(self, session_name: str) -> None:
        pass

    def delete_session(self, session_name: str) -> None:
        pass

    def rename_session(self, session_name: str, new_name: str) -> None:
        pass

    def list_saved_sessions(self) -> List[SessionLabel]:
        return []

    def list_running_sessions(self) -> List[SessionLabel]:
        return []

    def get_active_session(self) -> SessionLabel:
        return SessionLabel("", "")
