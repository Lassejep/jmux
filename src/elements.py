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
        session = self._load_session()
        return session

    def _load_session(self) -> JmuxSession:
        session_data = self.multiplexer.get(
            ["session_name", "session_id", "windows"])
        windows = self._load_windows(session_data["session_id"],
                                     session_data["windows"])
        return JmuxSession(name=session_data["session_name"],
                           id=session_data["session_id"], windows=windows)

    def _load_windows(self, session_id: str,
                      num_windows: int) -> list[JmuxWindow]:
        windows = []
        for i in range(int(num_windows)):
            window_data = self.multiplexer.get(["window_name", "window_id",
                                                "layout", "window_focus",
                                                "panes"], f"{session_id}:{i}")
            panes = self._load_panes(window_data["window_id"],
                                     window_data["panes"])
            windows.append(JmuxWindow(name=window_data["window_name"],
                                      id=window_data["window_id"],
                                      layout=window_data["layout"],
                                      focus=window_data["window_focus"],
                                      panes=panes))
        return windows

    def _load_panes(self, window_id: str, num_panes: int) -> list[JmuxPane]:
        panes = []
        for i in range(int(num_panes)):
            keys = ["pane_id", "pane_focus", "pane_current_dir"]
            pane_data = self.multiplexer.get(keys, f"{window_id}.{i}")
            pane = JmuxPane(id=pane_data["pane_id"],
                            focus=int(pane_data["pane_focus"]) == 1,
                            current_dir=pane_data["pane_current_dir"])
            panes.append(pane)
        return panes


class JmuxBuilder:
    """
    Build terminal multiplexer sessions, windows, and panes
    from Jmux objects.
    """

    def __init__(self, multiplexer: TerminalMultiplexerAPI):
        self.multiplexer = multiplexer
