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
    def __init__(self, id: int) -> None:
        self.id: int = id
        self.name: str = str(id)
        self.layout: str = None
        self.is_active: bool = False
        self.panes: [TmuxPane] = None

    def __get_pane_string_from_tmux(self) -> str:
        try:
            tmux_panes = subprocess.check_output(
                ["tmux", "list-panes", "-t", self.name, "-F",
                 "#P:#{pane_current_path}:#{pane_active}"],
            ).decode("utf-8")
        except subprocess.CalledProcessError as e:
            raise JmuxError(f"Failed to get panes: {e}")
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
