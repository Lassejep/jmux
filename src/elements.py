from dataclasses import dataclass

from src.multiplexer import TerminalMultiplexerClient


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

    def __init__(self, multiplexer: TerminalMultiplexerClient):
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

    def __init__(self, multiplexer: TerminalMultiplexerClient):
        self.multiplexer = multiplexer
        if multiplexer is None:
            raise ValueError("Invalid multiplexer")

    def build(self, session: JmuxSession) -> None:
        """
        Build the JmuxSession object `session` in the terminal multiplexer.
        """
        if not session:
            raise ValueError("Invalid session")
        data = self.multiplexer.get(["session_name"], session.id)
        if session.name in data.values():
            raise ValueError("Session already exists")
        session.id = self.multiplexer.create_session(session.name)
        self._create_windows(session.id, session.windows)
        """
        new sessions create a window by default that is finicky to manage,
        to avoid having to deal with it, we kill it.
        Killing the only window in a session will also kill the session,
        so we have to kill the default window after creating our own windows.
        """
        self.multiplexer.kill_element(f"{session.id}:1")

    def _create_windows(self, session_id: str,
                        windows: list[JmuxWindow]) -> None:
        if not windows:
            raise ValueError("Session must have at least one window")
        for window in windows:
            window.id = self.multiplexer.create_window(window.name, session_id)
            self._create_panes(window.id, window.panes)
            """
            new windows start with a pane already created,
            to avoid having to manage it, we kill it.
            Killing the only pane in a window will also kill the window,
            so we have to kill the starting pane after creating our own panes.
            """
            self.multiplexer.kill_element(f"{window.id}.1")
            self.multiplexer.change_window_layout(window.layout, window.id)
            if window.focus:
                self.multiplexer.focus_element(window.id)

    def _create_panes(self, window_id: str, panes: list[JmuxPane]) -> None:
        if not panes:
            raise ValueError("Window must have at least one pane")
        for pane in panes:
            pane.id = self.multiplexer.create_pane(window_id)
            if pane.focus:
                self.multiplexer.focus_element(pane.id)
            self.multiplexer.change_pane_directory(pane.current_dir, pane.id)
