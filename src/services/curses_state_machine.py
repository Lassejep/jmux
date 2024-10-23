from src.interfaces import StateMachine
from src.models import CursesStates


class CursesStateMachine(StateMachine[CursesStates]):
    def __init__(self) -> None:
        self.state = CursesStates.MAIN

    def get_state(self) -> CursesStates:
        return self.state

    def set_state(self, state: CursesStates) -> None:
        self.state = state
