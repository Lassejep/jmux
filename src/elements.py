import abc
from typing import List, Self
from dataclasses import dataclass

from src.tmuxapi import TMUX


class IJmuxElement(abc.ABC):
    @abc.abstractmethod
    def build_from_tmux(self) -> None:
        pass

    @abc.abstractmethod
    def create_in_tmux(self) -> None:
        pass


@dataclass
class JmuxPane(IJmuxElement):
    id: int
    path: str
    is_active: bool

    def build_from_tmux(session_name: str, window_index: int,
                        pane_index: int) -> Self:
        keys = ["pane_index", "pane_current_path", "pane_active"]
        target = f"{session_name}:{window_index}.{pane_index}"
        pane_id, path, is_active = TMUX.get(keys, target)
        return JmuxPane(int(pane_id), path, is_active == "1")

    def create_in_tmux(self, session_name: str, window_index: int) -> None:
        if self._pane_exists(session_name, window_index, self.id):
            keys = ["cd ", self.path]
            target = f"{session_name}:{window_index}.{self.id}"
            TMUX.send_keys(keys, target)
            if self.is_active:
                focus_cmd = ["select-pane", "-t",
                             f"{session_name}:{window_index}.{self.id}"]
                TMUX.run(focus_cmd)
        else:
            cmd = ["splitw", "-t",
                   f"{session_name}:{window_index}.{self.id - 1}",
                   "-c", self.path]
            if not self.is_active:
                cmd.append("-d")
            TMUX.run(cmd)

    def _pane_exists(self, session_name: str, window_index: int,
                     pane_index: int) -> bool:
        pane = TMUX.run(["list-panes", "-t", f"{session_name}:{window_index}",
                        "-F", "#{pane_index}"]).split("\n")
        if str(pane_index) not in pane:
            return False
        return True


@dataclass
class JmuxWindow(IJmuxElement):
    id: int
    name: str
    is_active: bool
    layout: str
    panes: List[JmuxPane]

    def __post_init__(self) -> None:
        if type(self.panes[0]) is dict:
            self.panes = [JmuxPane(**pane) for pane in self.panes]

    def build_from_tmux(session_name: str, window_index: int) -> Self:
        keys = ["window_name", "window_active",
                "window_layout", "window_panes"]
        target = f"{session_name}:{window_index}"
        window_name, is_active, layout, window_panes = TMUX.get(keys, target)
        panes = []
        for pane_index in range(1, int(window_panes) + 1):
            panes.append(JmuxPane.build_from_tmux(
                session_name, window_index, pane_index))
        return JmuxWindow(window_index, window_name, is_active == "1",
                          layout, panes)

    def create_in_tmux(self, session_name: str) -> None:
        cmd = ["neww", "-t", f"{session_name}:{self.id}",
               "-k", "-n", self.name]
        if not self.is_active:
            cmd.append("-d")
        TMUX.run(cmd)
        for pane in self.panes:
            pane.create_in_tmux(session_name, self.id)
        cmd = ["select-layout", "-t",
               f"{session_name}:{self.id}", self.layout]
        TMUX.run(cmd)


@dataclass
class JmuxSession(IJmuxElement):
    name: str
    windows: List[JmuxWindow]

    def __post_init__(self) -> None:
        if type(self.windows[0]) is dict:
            self.windows = [JmuxWindow(**window) for window in self.windows]

    def build_from_tmux(session_name: str) -> Self:
        keys = ["session_windows"]
        target = f"{session_name}"
        session_windows = TMUX.get(keys, target)
        windows = []
        for window_index in range(1, int(session_windows) + 1):
            windows.append(JmuxWindow.build_from_tmux(
                session_name, window_index))
        return JmuxSession(session_name, windows)

    def create_in_tmux(self) -> None:
        cmd = ["new-session", "-d", "-s", self.name]
        TMUX.run(cmd)
        for window in self.windows:
            window.create_in_tmux(self.name)
