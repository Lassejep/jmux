from enum import Enum


class Event(Enum):
    EXIT = 0
    MOVE_UP = 1
    MOVE_DOWN = 2
    MOVE_LEFT = 3
    MOVE_RIGHT = 4
    CREATE_SESSION = 5
    LOAD_SESSION = 6
    RENAME_SESSION = 7
    DELETE_SESSION = 8
    SAVE_SESSION = 9
    KILL_SESSION = 10
    UNKNOWN = 11
    NOOP = 12
    GET_SESSION = 13
    SHOW_MESSAGE = 14
    CONFIRM = 15
    INPUT = 16
