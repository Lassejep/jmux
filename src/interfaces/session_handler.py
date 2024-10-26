from abc import ABC, abstractmethod
from typing import List

from src.interfaces.model import Model
from src.models import SessionLabel


class SessionHandler(ABC):
    @abstractmethod
    def __init__(self, model: Model) -> None:
        """
        Interface for list annotators.
        """
        self.model: Model
        self.sessions: List[SessionLabel]
        raise NotImplementedError

    @abstractmethod
    def update_sessions(self) -> List[SessionLabel]:
        """
        Update the list of items.
        """
        raise NotImplementedError

    @abstractmethod
    def get_annotated_sessions(self) -> List[str]:
        """
        Annotate a list of items.
        """
        raise NotImplementedError
