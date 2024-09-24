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
    Load terminal multiplexer sessions, windows, and panes
    into Jmux objects.
    """

    def __init__(self, multiplexer: TerminalMultiplexerAPI):
        self.multiplexer = multiplexer
        if multiplexer is None:
            raise ValueError("Invalid multiplexer")

    def load_panes(self, target: str) -> list[JmuxPane]:
        if not target:
            raise ValueError("Invalid target")
        panes = []
        pane_ids = self.multiplexer.get(["pane_id"], target)
        print(pane_ids)
        return panes


class JmuxBuilder:
    """
    Build terminal multiplexer sessions, windows, and panes
    from Jmux objects.
    """

    def __init__(self, multiplexer: TerminalMultiplexerAPI):
        self.multiplexer = multiplexer
