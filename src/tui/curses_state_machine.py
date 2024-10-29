from src.data_models import CursesStates
from src.interfaces import StateMachine


class CursesStateMachine(StateMachine[CursesStates]):
    def __init__(self) -> None:
        self.state: CursesStates = CursesStates.MULTIPLEXER_MENU

    def get_state(self) -> CursesStates:
        return self.state

    def set_state(self, state: CursesStates) -> None:
        self.state = state
