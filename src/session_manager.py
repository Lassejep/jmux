import pathlib
import json
from typing import List
from dataclasses import asdict

from src.tmuxapi import TMUX
from src.elements import JmuxSession


class TmuxManager:
    def __init__(self) -> None:
        self._sessions_dir = pathlib.Path().home() / ".config" / "jmux"
        if not self._sessions_dir.exists():
            self._sessions_dir.mkdir()

    def save_session(self, session: JmuxSession) -> None:
        with open(self._sessions_dir / f"{session.name}.json", "w") as f:
            json.dump(asdict(session), f, indent=2)

    def load_session(self, session_name: str) -> JmuxSession:
        with open(self._sessions_dir / f"{session_name}.json") as f:
            session = JmuxSession(**json.load(f))
        session.create_in_tmux()
        return session

    def get_current_session(self) -> JmuxSession:
        session_name = TMUX.get("session_name")
        return JmuxSession.build_from_tmux(session_name)

    def save_current_session(self) -> None:
        session = self.get_current_session()
        self.save_session(session)

    def list_sessions(self) -> List[str]:
        return [str(session.stem) for session in self._sessions_dir.iterdir()]
