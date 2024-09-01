class TmuxSession:
    def __init__(self, session_name):
        self.session_name = session_name
        self.windows = []

    def add_window(self, window):
        self.windows.append(window)

    def __str__(self):
        return f"{self.session_name}: {self.windows}"


class TmuxWindow:
    def __init__(self, window_name):
        self.window_name = window_name
        self.panes = []

    def add_pane(self, pane):
        self.panes.append(pane)

    def __str__(self):
        return f"{self.window_name}: {self.panes}"


class TmuxPane:
    def __init__(self, pane_name):
        self.pane_name = pane_name

    def __str__(self):
        return self.pane_name


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
