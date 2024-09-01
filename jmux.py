from enum import Enum


class TmuxSplit(Enum):
    NONE = 1
    VERTICAL = 2
    HORIZONTAL = 3


class TmuxPane:
    def __init__(self, pane_name: str, pane_id: int = 0,
                 pane_size: int = 100, is_active: bool = True,
                 split_direction: TmuxSplit = TmuxSplit.NONE) -> None:
        self.name: str = pane_name
        self.id: int = pane_id
        self.size: int = pane_size
        self.is_active: bool = is_active
        self.split_direction: TmuxSplit = split_direction

    def __str__(self) -> str:
        return self.name


class TmuxWindow:
    def __init__(self, window_name):
        self.name = window_name
        self.panes = []

    def add_pane(self, pane):
        self.panes.append(pane)

    def __str__(self):
        str_panes = "\n".join([f"    {pane}" for pane in self.panes])
        return f"{self.name}:\n{str_panes}"


class TmuxSession:
    def __init__(self, session_name: str) -> None:
        self.name: str = session_name
        self.windows: list[TmuxWindow] = []

    def add_window(self, window: TmuxWindow) -> None:
        self.windows.append(window)

    def __str__(self) -> str:
        str_windows = "\n".join([f"  {window}" for window in self.windows])
        return f"{self.name}:\n{str_windows}"


def parse_tmux_sessions():
    sessions = []
    session = None
    window = None
    with open("tmux.txt") as f:
        for line in f:
            if line.startswith("Session:"):
                if session:
                    sessions.append(session)
                session = TmuxSession(line.split(":")[1].strip())
            elif line.startswith("Window:"):
                if window:
                    session.add_window(window)
                window = TmuxWindow(line.split(":")[1].strip())
            else:
                window.add_pane(TmuxPane(line.strip()))
        if window:
            session.add_window(window)
        if session:
            sessions.append(session)
    return sessions


def main():
    sessions = parse_tmux_sessions()
    for session in sessions:
        print(session)


if __name__ == "__main__":
    main()
