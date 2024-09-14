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
            raise JmuxError(f"Failed to run {e}")

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

    # FIXME: This method is unreliable and fails sometimes
    def send_keys(self, keys: str | List[str], target: str) -> None:
        if type(keys) is not list:
            keys = [keys]
        cmd = ["send-keys", "-t", target, *keys, "C-m"]
        wait_cmd = ["send-keys", "-t", target, self.tmux_bin,
                    " wait-for", " -S", " jmux_ready", "C-m"]
        confirm_cmd = [self.tmux_bin, "wait-for", "jmux_ready"]
        try:
            self.run(cmd)
        except JmuxError:
            raise JmuxError("Failed to send keys" + keys)
        proc = subprocess.Popen(confirm_cmd)
        self.run(wait_cmd)
        proc.wait(timeout=5)


TMUX = TmuxBin()


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
                   f"{session_name}:{window_index}", "-c", self.path]
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

    def build_from_tmux(self, session_name: str, window_index: int) -> Self:
        keys = ["window_name", "window_active",
                "window_layout", "window_panes"]
        target = f"{session_name}:{window_index}"
        window_name, is_active, layout, window_panes = self.tmux.get(
            keys, target)
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
        self.tmux.run(cmd)
        for pane in self.panes:
            pane.create_in_tmux(session_name, self.id, pane)
        cmd = ["select-layout", "-t",
               f"{session_name}:{self.id}", self.layout]
        self.tmux.run(cmd)


@dataclass
class JmuxSession(IJmuxElement):
    name: str
    windows: List[JmuxWindow]

    def __post_init__(self) -> None:
        if type(self.windows[0]) is dict:
            self.windows = [JmuxWindow(**window) for window in self.windows]

    def build_from_tmux(self, session_name: str) -> Self:
        keys = ["session_windows"]
        target = f"{session_name}"
        session_windows = self.tmux.get(keys, target)
        windows = []
        for window_index in range(1, int(session_windows) + 1):
            windows.append(JmuxWindow.build_from_tmux(
                session_name, window_index))
        return JmuxSession(session_name, windows)

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

    def save_session(self, session: JmuxSession) -> None:
        with open(self._sessions_dir / f"{session.name}.json", "w") as f:
            json.dump(asdict(session), f, indent=2)

    def load_session(self, session_name: str) -> JmuxSession:
        with open(self._sessions_dir / f"{session_name}.json") as f:
            session = JmuxSession(**json.load(f))
        session.create_in_tmux()
        return session

    def get_current_session(self) -> JmuxSession:
        session_name = self.tmux.get("session_name")
        return JmuxSession.build_from_tmux(session_name)

    def save_current_session(self) -> None:
        session = self.get_current_session()
        self.save_session(session)
