from enum import Enum
import json
import subprocess
import time


class JmuxError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class TmuxSplit(Enum):
    NONE = 1
    VERTICAL = 2
    HORIZONTAL = 3


class TmuxPane:
    def __init__(self, pane_size: int = 100, is_active: bool = True,
                 split_direction: TmuxSplit = TmuxSplit.NONE,
                 split_id: int = 0, working_dir: str = "~/",
                 command: str = "") -> None:
        self.id: int = 0
        self.size: int = pane_size
        self.is_active: bool = is_active
        self.split_id: int = split_id
        self.split_direction: TmuxSplit = split_direction
        self.working_dir: str = "~/"
        self.command: str = ""

    def __str__(self) -> str:
        string = f"{self.id}:\n"
        string += f"    size: {self.size}\n"
        string += f"    is_active: {self.is_active}\n"
        string += f"    split_id: {self.split_id}\n"
        string += f"    split_direction: {self.split_direction.name}\n"
        string += f"    working_dir: {self.working_dir}\n"
        string += f"    command: {self.command}"
        return string

    def to_dict(self) -> dict:
        return {
            "size": self.size,
            "is_active": self.is_active,
            "split_id": self.split_id,
            "split_direction": self.split_direction.name,
            "working_dir": self.working_dir,
            "command": self.command
        }

    def build(self, session_name: str, window_name: str) -> None:
        window = session_name + ":" + window_name
        if self.split_direction != TmuxSplit.NONE:
            command = "tmux split-window -t"
            target = f"{window}.{str(self.split_id)}"
            match self.split_direction:
                case TmuxSplit.VERTICAL:
                    args = f"-v -l {self.size} -c {self.working_dir}"
                case TmuxSplit.HORIZONTAL:
                    args = f"-h -l {self.size} -c {self.working_dir}"
            err = subprocess.Popen(f"{command} {target} {args}", shell=True,
                                   stderr=subprocess.PIPE)
            if err.communicate()[1].decode("utf-8").strip():
                raise JmuxError(f"Error creating pane {self.id}")
        if self.command:
            time.sleep(0.1)
            command = "tmux send-keys -t"
            target = f"{window}.{str(self.id)}"
            args = f"'{self.command}' C-m"
            err = subprocess.Popen(f"{command} {target} {args}", shell=True,
                                   stderr=subprocess.PIPE)
            if err.communicate()[1].decode("utf-8").strip():
                raise JmuxError(f"Error sending command to pane {self.id}")


class TmuxWindow:
    def __init__(self, window_name: str) -> None:
        self.name: str = window_name
        self.panes: [TmuxPane] = []

    def add_pane(self, pane: TmuxPane) -> None:
        self.panes.append(pane)
        pane.id = len(self.panes)

    def __str__(self) -> str:
        string = ""
        for pane in self.panes:
            pane_str = f"{pane}"
            pane_str = pane_str.replace("\n", "\n    ")
            string += f"    {pane_str}\n"
        return f"{self.name}:\n{string[:-1]}"

    def to_dict(self) -> dict:
        window_dict = {}
        for i, pane in enumerate(self.panes):
            window_dict[str(i)] = pane.to_dict()
        return window_dict

    def build(self, session_name: str) -> None:
        command = f"tmux new-window -t {session_name} -n {self.name}"
        err = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
        if err.communicate()[1].decode("utf-8").strip():
            raise JmuxError(f"Error creating window {self.name}")
        time.sleep(0.1)
        for pane in self.panes:
            pane.build(session_name, self.name)
        time.sleep(0.1)
        for pane in self.panes:
            if pane.is_active:
                target = f"{session_name}:{self.name}.{pane.id}"
                command = f"tmux select-pane -t {target}"
                err = subprocess.Popen(command, shell=True,
                                       stderr=subprocess.PIPE)
                if err.communicate()[1].decode("utf-8").strip():
                    raise JmuxError(f"Error selecting pane {pane.id}")


class TmuxSession:
    def __init__(self, session_name: str) -> None:
        self.name: str = session_name
        self.windows: list[TmuxWindow] = []

    def add_window(self, window: TmuxWindow) -> None:
        self.windows.append(window)

    def __str__(self) -> str:
        string = ""
        for window in self.windows:
            window_str = f"{window}"
            window_str = window_str.replace("\n", "\n    ")
            string += f"    {window_str}\n"
        return f"{self.name}:\n{string[:-1]}"

    def to_dict(self) -> dict:
        session_dict = {}
        for window in self.windows:
            session_dict[window.name] = window.to_dict()
        return session_dict

    def build(self) -> None:
        command = f"tmux has-session -t {self.name}"
        err = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
        err = err.communicate()[1].decode("utf-8").strip()
        if not err:
            raise JmuxError(f"Session {self.name} already exists")
        subprocess.Popen(
            f"tmux new-session -d -s {self.name}", shell=True)
        for window in self.windows:
            window.build(self.name)


def load_tmux_sessions() -> [TmuxSession]:
    with open("tmux_sessions.json", "r") as f:
        data = json.load(f)
    sessions = []
    for session_name, session_data in data.items():
        session = TmuxSession(session_name)
        for window_name, window_data in session_data.items():
            window = TmuxWindow(window_name)
            for pane_data in window_data.values():
                pane = TmuxPane(pane_data["size"], pane_data["is_active"],
                                TmuxSplit[pane_data["split_direction"]],
                                pane_data["split_id"],
                                pane_data["working_dir"], pane_data["command"])
                window.add_pane(pane)
            session.add_window(window)
        sessions.append(session)
    return sessions


def create_tmux_session(session_name: str) -> None:
    sessions = load_tmux_sessions()
    for session in sessions:
        if session.name == session_name:
            session.build()
            return
    raise JmuxError(f"Session {session_name} not found")


def main() -> None:
    sessions = load_tmux_sessions()
    for session in sessions:
        print(session)
    session_name = input("Enter session name: ")
    create_tmux_session(session_name)


if __name__ == "__main__":
    main()
