from dataclasses import dataclass


@dataclass
class JmuxPane:
    """
    Represents a pane in a window.
    """

    id: str
    focus: bool
    current_dir: str


@dataclass
class JmuxWindow:
    """
    Represents a window in a session.
    """

    id: str
    name: str
    layout: str
    focus: bool
    panes: list[JmuxPane]


@dataclass
class JmuxSession:
    """
    Represents a session in a Tmux terminal multiplexer.
    """

    id: str
    name: str
    windows: list[JmuxWindow]


@dataclass
class SessionLabel:
    """
    A dataclass to store the id and name of a session.
    """

    id: str
    name: str
