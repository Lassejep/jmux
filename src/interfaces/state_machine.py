import abc
from enum import Enum
from typing import Generic, TypeVar

State = TypeVar("State", bound=Enum)


class StateMachine(abc.ABC, Generic[State]):
    @abc.abstractmethod
    def __init__(self) -> None:
        """
        Interface for state machines.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_state(self) -> State:
        """
        Get the current state.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set_state(self, state: State) -> None:
        """
        Set the current state.
        """
        raise NotImplementedError
