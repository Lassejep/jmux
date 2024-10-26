from enum import Enum


class CursesStates(Enum):
    EXIT = 0
    MULTIPLEXER_MENU = 1
    FILE_MENU = 2
    CREATE_SESSION = 3
    SAVE_SESSION = 4
    DELETE_SESSION = 5
    KILL_SESSION = 6
    RENAME_SESSION = 7
