from enum import Enum


class CursesStates(Enum):
    RUNNING_SESSIONS = 0
    SAVED_SESSIONS = 1
    CREATE_SESSION = 2
    CONFIRMATION = 3
    RENAME_SESSION = 4
