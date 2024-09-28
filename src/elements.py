from dataclasses import dataclass

from src.multiplexer import TerminalMultiplexerAPI


@dataclass
class JmuxPane:
    id: str
    focus: bool
    current_dir: str


@dataclass
class JmuxWindow:
    name: str
    id: str
    layout: str
    focus: bool
    panes: list[JmuxPane]


@dataclass
class JmuxSession:
    name: str
    id: str
    windows: list[JmuxWindow]


class JmuxLoader:
    """
    Load terminal multiplexer sessions, windows, and panes into Jmux objects.
    """

    def __init__(self, multiplexer: TerminalMultiplexerAPI):
        self.multiplexer = multiplexer
        if multiplexer is None:
            raise ValueError("Invalid multiplexer")

    def load(self) -> JmuxSession:
        """
        Load the current session into a JmuxSession object.
        """
        if not self.multiplexer.is_running():
            raise EnvironmentError("Not in a session")
        return self._load_session()

    def _load_session(self) -> JmuxSession:
        keys = ["session_name", "session_id", "windows"]
        session_data = self.multiplexer.get(keys)
        windows = self._load_windows(session_data["session_id"],
                                     int(session_data["windows"]))
        return JmuxSession(session_data["session_name"],
                           session_data["session_id"], windows)

    def _load_windows(self, session_id: str,
                      num_windows: int) -> list[JmuxWindow]:
        return [self._load_window(f"{session_id}:{i}")
                for i in range(num_windows)]

    def _load_window(self, target_window: str) -> JmuxWindow:
        keys = ["window_name", "window_id", "layout", "window_focus", "panes"]
        window_data = self.multiplexer.get(keys, target_window)
        panes = self._load_panes(window_data["window_id"],
                                 int(window_data["panes"]))
        return JmuxWindow(window_data["window_name"], window_data["window_id"],
                          window_data["layout"],
                          int(window_data["window_focus"]) == 1, panes)

    def _load_panes(self, window_id: str, num_panes: int) -> list[JmuxPane]:
        return [self._load_pane(f"{window_id}.{i}") for i in range(num_panes)]

    def _load_pane(self, target_pane: str) -> JmuxPane:
        keys = ["pane_id", "pane_focus", "pane_current_dir"]
        pane_data = self.multiplexer.get(keys, target_pane)
        return JmuxPane(pane_data["pane_id"],
                        int(pane_data["pane_focus"]) == 1,
                        pane_data["pane_current_dir"])


class JmuxBuilder:
    """
    Build terminal multiplexer sessions, windows, and panes
    from Jmux objects.
    """

    def __init__(self, multiplexer: TerminalMultiplexerAPI):
        self.multiplexer = multiplexer
        if multiplexer is None:
            raise ValueError("Invalid multiplexer")

    def build(self, session: JmuxSession) -> None:
        if not session:
            raise ValueError("Invalid session")
        data = self.multiplexer.get(["session_name"], session.id)
        if session.name in data.values():
            raise ValueError("Session already exists")
        new_id = self.multiplexer.create_session(session.name)
        session.id = new_id
