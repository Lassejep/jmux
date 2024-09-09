import pathlib
import subprocess
from typing import Optional
from dataclasses import dataclass


class JmuxError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


@dataclass
class TmuxPane:
    id: int
    path: pathlib.Path = pathlib.Path().home()
    is_active: bool = False
    processes: Optional[dict] = None


class TmuxWindow:
    def __init__(self, session_id: str, window_name: str) -> None:
        self.session: str = session_id
        self.name: str = window_name
        self.layout: Optional[str] = None
        self.is_active: bool = False
        self.panes: Optional[TmuxPane] = None

    def _run_process(self, args: [str]) -> None:
        try:
            out = subprocess.run(args, check=True, stdout=subprocess.PIPE)
            return out.stdout.decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise JmuxError(f"Failed to run process: {e}")

    def __get_pane_string_from_tmux(self) -> str:
        args = ["tmux", "list-panes", "-t", self.session, "-F",
                "#P:#{pane_current_path}:#{pane_active}"]
        tmux_panes = self._run_process(args)
        return tmux_panes

    def __create_pane_from_string(self, pane_string: str) -> TmuxPane:
        pane_id, pane_path, pane_active = pane_string.split(":")
        pane_id = int(pane_id)
        pane_path = pathlib.Path(pane_path)
        pane_active = pane_active == "1"
        return TmuxPane(pane_id, pane_path, pane_active)

    def __convert_pane_string_to_pane_struct(self, tmux_panes: str) -> [str]:
        panes = []
        for line in tmux_panes.split("\n"):
            if not line:
                continue
            pane = self.__create_pane_from_string(line)
            panes.append(pane)
        return panes

    def load_panes_from_tmux(self) -> None:
        tmux_panes = self.__get_pane_string_from_tmux()
        self.panes = self.__convert_pane_string_to_pane_struct(tmux_panes)

    def to_dict(self) -> dict:
        return {
            "session": self.session,
            "name": self.name,
            "layout": self.layout,
            "is_active": self.is_active,
            "panes": [pane.__dict__ for pane in self.panes],
        }

    def load_panes_from_dict(self, panes: [dict]) -> None:
        self.panes = [TmuxPane(**pane) for pane in panes]

    def _create_panes(self):
        if not self.panes:
            return
        for pane in self.panes:
            args = ["tmux", "split-window", "-t",
                    f"{self.session}:{self.name}"]
            if pane.path:
                args.extend(["-c", str(pane.path)])
            if not pane.is_active:
                args.append("-d")
            self._run_process(args)

    def create_window(self) -> None:
        args = ["tmux", "new-window", "-t", self.session, "-n", self.name]
        if not self.is_active:
            args.append("-d")
        self._run_process(args)
        self._create_panes()
        if self.layout:
            args = ["tmux", "select-layout", "-t",
                    f"{self.session}:{self.name}", self.layout]
            self._run_process(args)


class TmuxSession:
    def __init__(self, session_name: str) -> None:
        self.name: str = session_name
        self.id: Optional[str] = None
        self.windows: Optional[TmuxWindow] = None

    def _run_process(self, args: [str]) -> None:
        try:
            out = subprocess.run(args, check=True, stdout=subprocess.PIPE)
            return out.stdout.decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise JmuxError(f"Failed to run process: {e}")

    def _load_windows_from_tmux(self) -> None:
        pass
