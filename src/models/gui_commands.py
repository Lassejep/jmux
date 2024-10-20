from enum import Enum


class Commands(Enum):
    EXIT = 0
    MOVE_UP = 1
    MOVE_DOWN = 2
    CREATE_SESSION = 3
    LOAD_SESSION = 4
    RENAME_SESSION = 5
    DELETE_SESSION = 6
    SAVE_SESSION = 7
    KILL_SESSION = 8
