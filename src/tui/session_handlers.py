from typing import List

from src.data_models import SessionLabel
from src.interfaces import Model, SessionHandler


class MultiplexerSessions(SessionHandler):
    def __init__(self, model: Model) -> None:
        """
        Annotator for session labels.
        """
        self.model = model
        self.sessions = self.update_sessions()

    def update_sessions(self) -> List[SessionLabel]:
        """
        Update the list of items.
        """
        self.sessions = self.model.list_running_sessions()
        return self.sessions

    def get_annotated_sessions(self) -> List[str]:
        """
        Annotate a list of items.
        """
        annotated_sessions = [
            self._annotate_session(index, session)
            for index, session in enumerate(self.sessions)
        ]
        return annotated_sessions

    def _annotate_session(self, index: int, session: SessionLabel) -> str:
        name = f"{index + 1}. {session.name}"
        if session == self.model.get_active_session():
            name += "*"
        if (
            session in self.model.list_running_sessions()
            and session in self.model.list_saved_sessions()
        ):
            name += " (saved)"
        return name


class FileSessions(SessionHandler):
    def __init__(self, model: Model) -> None:
        """
        Annotator for session labels.
        """
        self.model = model
        self.sessions = self.update_sessions()

    def update_sessions(self) -> List[SessionLabel]:
        """
        Update the list of items.
        """
        self.sessions = self.model.list_saved_sessions()
        return self.sessions

    def get_annotated_sessions(self) -> List[str]:
        """
        Annotate a list of items.
        """
        annotated_sessions = [
            self._annotate_session(index, session)
            for index, session in enumerate(self.sessions)
        ]
        return annotated_sessions

    def _annotate_session(self, index: int, session: SessionLabel) -> str:
        name = f"{index + 1}. {session.name}"
        if session == self.model.get_active_session():
            name += "*"
        if (
            session in self.model.list_running_sessions()
            and session in self.model.list_saved_sessions()
        ):
            name += " (running)"
        return name
