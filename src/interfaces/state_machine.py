from abc import ABC, abstractmethod
from enum import Enum
from typing import Generic, TypeVar

State = TypeVar("State", bound=Enum)


class StateMachine(ABC, Generic[State]):
    @abstractmethod
    def __init__(self) -> None:
        """
        Interface for state machines.
        """
        self.state: State
        raise NotImplementedError

    @abstractmethod
    def get_state(self) -> State:
        """
        Get the current state.
        """
        raise NotImplementedError

    @abstractmethod
    def set_state(self, state: State) -> None:
        """
        Set the current state.
        """
        raise NotImplementedError
