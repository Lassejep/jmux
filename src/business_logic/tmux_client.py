import os
import subprocess
from typing import List

from src.data_models import JmuxPane, JmuxSession, JmuxWindow, SessionLabel
from src.interfaces import Multiplexer


class TmuxClient(Multiplexer):
    def __init__(self) -> None:
        """
        Implementation of the TerminalMultiplexerAPI
        for the Tmux terminal multiplexer.
        """
        self._bin = self._get_binary()
        if not self._bin:
            raise FileNotFoundError("Tmux binary not found")
        self.base_index = self._get_base_index()

    def _get_binary(self) -> str:
        command = ["which", "tmux"]
        response = subprocess.run(command, capture_output=True, text=True, check=True)
        return response.stdout.strip()

    def _get_base_index(self) -> int:
        command = [self._bin, "show-options", "-g", "base-index"]
        response = subprocess.run(command, capture_output=True, text=True, check=True)
        base_index = response.stdout.strip().split(" ")[1]
        return int(base_index)

    def is_running(self) -> bool:
        """
        Check if tmux is running.
        """
        env = os.environ.copy()
        if "TMUX" in env and env["TMUX"] != "":
            return True
        return False

    def list_sessions(self) -> list[SessionLabel]:
        """
        Get a list of all the currently running sessions.
        """
        if not self.is_running():
            return []
        command = [self._bin, "list-sessions", "-F", "#{session_id}:#{session_name}"]
        response = subprocess.run(command, capture_output=True, text=True, check=True)
        sessions = response.stdout.split("\n")
        return [SessionLabel(*session.split(":")) for session in sessions if session]

    def get_session(self, label: SessionLabel) -> JmuxSession:
        """
        Get the data of the tmux session with the id `session_id`.
        """
        sessions = self.list_sessions()
        if label not in sessions:
            raise ValueError(f"Session {label.name} not found")
        jmux_windows = self._get_windows(label.id)
        return JmuxSession(label.id, label.name, jmux_windows)

    def _get_windows(self, session_id: str) -> list[JmuxWindow]:
        command = [
            self._bin,
            "list-windows",
            "-t",
            session_id,
            "-F",
            "#{window_id}:#{window_name}:#{window_layout}:#{window_active}",
        ]
        response = subprocess.run(command, capture_output=True, text=True, check=True)
        windows = response.stdout.split("\n")
        jmux_windows = [
            self._get_window(window_data) for window_data in windows if window_data
        ]
        return jmux_windows

    def _get_window(self, window_data: str) -> JmuxWindow:
        window_id, window_name, window_layout, window_active = window_data.split(":")
        panes: List[JmuxPane] = self._get_panes(window_id)
        return JmuxWindow(
            window_id, window_name, window_layout, window_active == "1", panes
        )

    def _get_panes(self, window_id: str) -> list[JmuxPane]:
        command = [
            self._bin,
            "list-panes",
            "-t",
            window_id,
            "-F",
            "#{pane_id}:#{pane_active}:#{pane_current_path}",
        ]
        response = subprocess.run(command, capture_output=True, text=True, check=True)
        panes = response.stdout.split("\n")
        jmux_panes = [self._get_pane(pane_data) for pane_data in panes if pane_data]
        return jmux_panes

    def _get_pane(self, pane_data: str) -> JmuxPane:
        pane_id, pane_active, pane_current_path = pane_data.split(":")
        return JmuxPane(pane_id, pane_active == "1", pane_current_path)

    def create_session(self, session: JmuxSession) -> None:
        """
        Create a new session in tmux with the data in `session`.
        """
        try:
            command = [
                self._bin,
                "new-session",
                "-ds",
                session.name,
                "-PF",
                "#{session_id}",
            ]
            response = subprocess.run(
                command, capture_output=True, text=True, check=True
            )
            session.id = response.stdout.strip()
            if len(session.windows) == 0:
                raise ValueError("Session must have at least one window")
            for window in session.windows:
                self._create_window(session.id, window)
            command = [
                self._bin,
                "kill-window",
                "-t",
                f"{session.id}:{self.base_index}",
            ]
            subprocess.run(command, check=True)
            command = [self._bin, "switch-client", "-t", session.id]
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as error:
            raise ValueError(error.stderr) from error

    def _create_window(self, session_id: str, window: JmuxWindow) -> None:
        command = [
            self._bin,
            "neww",
            "-t",
            session_id,
            "-n",
            window.name,
            "-PF",
            "#{window_id}",
        ]
        if not window.focus:
            command.append("-d")
        response = subprocess.run(command, capture_output=True, text=True, check=True)
        window.id = response.stdout.strip()
        if len(window.panes) == 0:
            raise ValueError("Window must have at least one pane")
        for pane in window.panes:
            self._create_pane(window.id, pane)
        command = [self._bin, "kill-pane", "-t", f"{window.id}.{self.base_index}"]
        subprocess.run(command, check=True)
        command = [self._bin, "select-layout", "-t", window.id, window.layout]
        subprocess.run(command, check=True)

    def _create_pane(self, window_id: str, pane: JmuxPane) -> None:
        command = [
            self._bin,
            "splitw",
            "-t",
            window_id,
            "-c",
            pane.current_dir,
            "-PF",
            "#{pane_id}",
        ]
        if not pane.focus:
            command.append("-d")
        response = subprocess.run(command, capture_output=True, text=True, check=True)
        pane.id = response.stdout.strip()

    def get_current_session_label(self) -> SessionLabel:
        """
        Get the data of the currently running tmux session.
        """
        if not self.is_running():
            raise ValueError("No session is currently running")
        command = [self._bin, "display-message", "-p", "#{session_id}:#{session_name}"]
        response = subprocess.run(command, capture_output=True, text=True, check=True)
        session_id, session_name = response.stdout.strip().split(":")
        return SessionLabel(session_id, session_name)

    def kill_session(self, label: SessionLabel) -> None:
        """
        Kill the tmux session with the data in `session`.
        """
        if label not in self.list_sessions():
            raise ValueError(f"Session {label.name} not found")
        command = [self._bin, "kill-session", "-t", label.id]
        subprocess.run(command, check=True)

    def rename_session(self, label: SessionLabel, new_name: str) -> None:
        """
        Rename the tmux session with the data in `label` to `new_name`.
        """
        if label not in self.list_sessions():
            raise ValueError(f"Session {label.name} not found")
        label.name = new_name
        command = [self._bin, "rename-session", "-t", label.id, label.name]
        subprocess.run(command, check=True)

    def create_new_session(self, session_name: str) -> None:
        """
        Create a new tmux session with the name `session_name`.
        """
        try:
            command = [self._bin, "new-session", "-ds", session_name]
            subprocess.run(command, check=True)
            command = [self._bin, "switch-client", "-t", session_name]
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as error:
            raise ValueError("Session already exists") from error

    def focus_session(self, label: SessionLabel) -> None:
        """
        Focus the tmux session with the data in `label`.
        """
        if label not in self.list_sessions():
            raise ValueError(f"Session {label.name} not found")
        command = [self._bin, "switch-client", "-t", label.id]
        subprocess.run(command, check=True)
