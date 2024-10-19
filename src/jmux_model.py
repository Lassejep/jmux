from typing import List

from src.file_handler import FileHandler
from src.jmux_session import SessionLabel
from src.model import Model
from src.multiplexer import Multiplexer


class JmuxModel(Model):
    def __init__(self, multiplexer: Multiplexer, file_handler: FileHandler) -> None:
        self.multiplexer = multiplexer
        self.file_handler = file_handler

    def create_session(self, session_name: str) -> None:
        pass

    def save_session(self, label: SessionLabel) -> None:
        pass

    def load_session(self, label: SessionLabel) -> None:
        pass

    def kill_session(self, label: SessionLabel) -> None:
        pass

    def delete_session(self, label: SessionLabel) -> None:
        pass

    def rename_session(self, label: SessionLabel, new_name: str) -> None:
        pass

    def list_saved_sessions(self) -> List[SessionLabel]:
        return []

    def list_running_sessions(self) -> List[SessionLabel]:
        return []

    def get_active_session(self) -> SessionLabel:
        return SessionLabel("", "")
