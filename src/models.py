from dataclasses import dataclass


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
