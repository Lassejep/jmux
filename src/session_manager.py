import pathlib
import subprocess
import json
import abc
from typing import List, Self
from dataclasses import dataclass, asdict


class JmuxError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class TmuxBin():
    def __init__(self) -> None:
        self.tmux_bin = self._find_tmux_bin()

    def run(self, cmd: List[str]) -> str:
        try:
            cmd.insert(0, self.tmux_bin)
            return subprocess.check_output(cmd, text=True).strip()
        except subprocess.CalledProcessError as e:
            raise JmuxError(f"Failed to run command: {e}")

    def _find_tmux_bin(self) -> str:
        try:
            return subprocess.check_output(["which", "tmux"],
                                           text=True).strip()
        except subprocess.CalledProcessError as e:
            raise JmuxError(f"Failed to find tmux binary: {e}")

    def get(self, keys: str | List[str], target: str = "") -> str:
        cmd = ["display-message"]
        if target:
            cmd.extend(["-t", target])
        if type(keys) is not list:
            keys = [keys]
        keystr = ""
        for key in keys:
            keystr += f"#{{{key}}}:"
        cmd.extend(["-p", f"{keystr[:-1]}"])
        output = self.run(cmd).split(":")
        if len(output) == 1:
            return output[0]
        return output


class ITmuxElement(abc.ABC):
    def __init__(self) -> None:
        self.tmux = TmuxBin()

    @abc.abstractmethod
    def build_from_tmux(self) -> None:
        pass

    @abc.abstractmethod
    def create_in_tmux(self) -> None:
        pass


@dataclass
class TmuxPane(ITmuxElement):
    id: int
    path: str
    is_active: bool
    tmux: TmuxBin = TmuxBin()

    def build_from_tmux(self, session_name: str, window_index: int,
                        pane_index: int) -> Self:
        keys = ["pane_index", "pane_current_path", "pane_active"]
        target = f"{session_name}:{window_index}.{pane_index}"
        pane_id, path, is_active = self.tmux.get(keys, target)
        return TmuxPane(int(pane_id), path, is_active == "1")

    def create_in_tmux(self, session_name: str, window_index: int) -> None:
        if self.id == 1:
            cmd = ["send-keys", "-t",
                   f"{session_name}:{window_index}.{self.id}",
                   f"cd {self.path}", "Enter", "clear", "Enter"]
        else:
            cmd = ["splitw", "-t",
                   f"{session_name}:{window_index}", "-c", self.path]
            if not self.is_active:
                cmd.append("-d")
        self.tmux.run(cmd)


@dataclass
class TmuxWindow(ITmuxElement):
    id: int
    name: str
    is_active: bool
    layout: str
    panes: List[TmuxPane]
    tmux: TmuxBin = TmuxBin()

    def __post_init__(self) -> None:
        if type(self.panes[0]) is dict:
            self.panes = [TmuxPane(**pane) for pane in self.panes]

    def build_from_tmux(self, session_name: str, window_index: int) -> Self:
        keys = ["window_name", "window_active",
                "window_layout", "window_panes"]
        target = f"{session_name}:{window_index}"
        window_name, is_active, layout, window_panes = self.tmux.get(
            keys, target)
        panes = []
        for pane_index in range(1, int(window_panes) + 1):
            panes.append(TmuxPane.build_from_tmux(
                session_name, window_index, pane_index))
        return TmuxWindow(window_index, window_name, is_active == "1", layout, panes)

    def create_in_tmux(self, session_name: str) -> None:
        cmd = ["neww", "-t", f"{session_name}:{self.id}",
               "-k", "-n", self.name]
        if not self.is_active:
            cmd.append("-d")
        self.tmux.run(cmd)
        for pane in self.panes:
            pane.create_in_tmux(session_name, self.id, pane)
        cmd = ["select-layout", "-t",
               f"{session_name}:{self.id}", self.layout]
        self.tmux.run(cmd)


@dataclass
class TmuxSession(ITmuxElement):
    name: str
    windows: List[TmuxWindow]

    def __post_init__(self) -> None:
        if type(self.windows[0]) is dict:
            self.windows = [TmuxWindow(**window) for window in self.windows]

    def build_from_tmux(self, session_name: str) -> Self:
        keys = ["session_windows"]
        target = f"{session_name}"
        session_windows = self.tmux.get(keys, target)
        windows = []
        for window_index in range(1, int(session_windows) + 1):
            windows.append(TmuxWindow.build_from_tmux(
                session_name, window_index))
        return TmuxSession(session_name, windows)

    def create_in_tmux(self) -> None:
        cmd = ["new-session", "-d", "-s", self.name]
        self.tmux.run(cmd)
        for window in self.windows:
            window.create_in_tmux(self.name, window)


class TmuxManager:
    def __init__(self) -> None:
        self.tmux = TmuxBin()
        self._sessions_dir = pathlib.Path().home() / ".config" / "jmux"
        if not self._sessions_dir.exists():
            self._sessions_dir.mkdir()

    def save_session(self, session: TmuxSession) -> None:
        with open(self._sessions_dir / f"{session.name}.json", "w") as f:
            json.dump(asdict(session), f, indent=2)

    def load_session(self, session_name: str) -> TmuxSession:
        with open(self._sessions_dir / f"{session_name}.json") as f:
            session = TmuxSession(**json.load(f))
        session.create_in_tmux()
        return session

    def get_current_session(self) -> TmuxSession:
        session_name = self.tmux.get("session_name")
        return TmuxSession.build_from_tmux(session_name)

    def save_current_session(self) -> None:
        session = self.get_current_session()
        self.save_session(session)
