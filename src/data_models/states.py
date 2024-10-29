from enum import Enum


class CursesStates(Enum):
    EXIT = 0
    MULTIPLEXER_MENU = 1
    FILE_MENU = 2
    MESSAGE_WINDOW = 3
