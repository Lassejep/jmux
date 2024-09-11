import pathlib
import subprocess
import json
from typing import List
from dataclasses import dataclass, asdict


class JmuxError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


@dataclass
class TmuxPane:
    id: int
    path: str
    is_active: bool


@dataclass
class TmuxWindow:
    id: int
    name: str
    is_active: bool
    layout: str
    panes: List[TmuxPane]

    def __post_init__(self) -> None:
        if type(self.panes[0]) is dict:
            self.panes = [TmuxPane(**pane) for pane in self.panes]


@dataclass
class TmuxSession:
    name: str
    windows: List[TmuxWindow]

    def __post_init__(self) -> None:
        if type(self.windows[0]) is dict:
            self.windows = [TmuxWindow(**window) for window in self.windows]


class TmuxManager:
    def __init__(self) -> None:
        self._tmux_bin = self._find_tmux_bin()
        self._sessions_dir = pathlib.Path().home() / ".config" / "jmux"
        if not self._sessions_dir.exists():
            self._sessions_dir.mkdir()

    def _run_cmd(self, cmd: List[str]) -> str:
        try:
            return subprocess.check_output(cmd, text=True).strip()
        except subprocess.CalledProcessError as e:
            raise JmuxError(f"Failed to run command: {e}")

    def _find_tmux_bin(self) -> str:
        return self._run_cmd(["which", "tmux"])

    def _get_pane(self, session_name: str, window_index: int,
                  pane_index: int) -> TmuxPane:
        cmd = [self._tmux_bin, "display-message", "-t",
               f"{session_name}:{window_index}.{pane_index}", "-p",
               "#P:#{pane_current_path}:#{pane_active}"]
        pane_id, path, is_active = self._run_cmd(cmd).split(":")
        return TmuxPane(int(pane_id), path, is_active == "1")

    def _get_window(self, session_name: str, window_index: int) -> TmuxWindow:
        cmd = [self._tmux_bin, "display-message", "-t",
               f"{session_name}:{window_index}", "-p",
               "#W:#{window_active}:#{window_layout}:#{window_panes}"]
        window_name, is_active, layout, window_panes = self._run_cmd(
            cmd).split(":")
        panes = []
        for pane_index in range(1, int(window_panes) + 1):
            panes.append(self._get_pane(
                session_name, window_index, pane_index))
        return TmuxWindow(window_index, window_name, is_active == "1", layout,
                          panes)

    def _get_session(self, session_name: str) -> TmuxSession:
        cmd = [self._tmux_bin, "display-message",
               "-t", f"{session_name}", "-p", "#{session_windows}"]
        session_windows = self._run_cmd(cmd)
        windows = []
        for window_index in range(1, int(session_windows) + 1):
            windows.append(self._get_window(session_name, window_index))
        return TmuxSession(session_name, windows)

    def get_current_session(self) -> TmuxSession:
        cmd = [self._tmux_bin, "display-message", "-p", "#{session_name}"]
        session_name = self._run_cmd(cmd)
        return self._get_session(session_name)

    def _create_pane(self, session_name: str, window_index: int,
                     pane: TmuxPane) -> None:
        if pane.id == 1:
            cmd = [self._tmux_bin, "send-keys", "-t",
                   f"{session_name}:{window_index}.{pane.id}",
                   f"cd {pane.path}", "Enter", "clear", "Enter"]
        else:
            cmd = [self._tmux_bin, "splitw", "-t",
                   f"{session_name}:{window_index}", "-c", pane.path]
            if not pane.is_active:
                cmd.append("-d")
        self._run_cmd(cmd)

    def _create_window(self, session_name: str, window: TmuxWindow) -> None:
        cmd = [self._tmux_bin, "neww", "-t", f"{session_name}:{window.id}",
               "-k", "-n", window.name]
        if not window.is_active:
            cmd.append("-d")
        self._run_cmd(cmd)
        for pane in window.panes:
            self._create_pane(session_name, window.id, pane)
        cmd = [self._tmux_bin, "select-layout", "-t",
               f"{session_name}:{window.id}", window.layout]
        self._run_cmd(cmd)

    def create_session(self, session: TmuxSession) -> None:
        cmd = [self._tmux_bin, "new-session", "-d", "-s", session.name]
        self._run_cmd(cmd)
        for window in session.windows:
            self._create_window(session.name, window)

    def save_session(self, session: TmuxSession) -> None:
        with open(self._sessions_dir / f"{session.name}.json", "w") as f:
            json.dump(asdict(session), f, indent=2)

    def load_session(self, session_name: str) -> TmuxSession:
        with open(self._sessions_dir / f"{session_name}.json") as f:
            session = TmuxSession(**json.load(f))
        self.create_session(session)
        return session
