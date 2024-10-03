import os
import subprocess
from typing import List

from src.models import JmuxPane, JmuxSession, JmuxWindow, SessionLabel
from src.multiplexer import Multiplexer


class TmuxClient(Multiplexer):
    """
    Implementation of the TerminalMultiplexerAPI
    for the Tmux terminal multiplexer.
    """

    def __init__(self) -> None:
        self._bin = self._get_binary()
        if not self._bin:
            raise FileNotFoundError("Tmux binary not found")

    def _get_binary(self) -> str:
        command = ["which", "tmux"]
        response = subprocess.run(command, capture_output=True, text=True, check=True)
        return response.stdout.strip()

    def is_running(self) -> bool:
        """
        Check if the Tmux terminal multiplexer is running.
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

    def get_session(self, session_id: str) -> JmuxSession:
        """
        Get the data of the session with the id `session_id`.
        """
        sessions = self.list_sessions()
        for session_label in sessions:
            if session_label.id == session_id:
                jmux_windows = self._get_windows(session_id)
                return JmuxSession(session_label.id, session_label.name, jmux_windows)
        raise ValueError(f"Session with id {session_id} not found")

    def _get_windows(self, session_id: str) -> list[JmuxWindow]:
        command = [
            self._bin,
            f"list-windows -t {session_id}",
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
            f"list-panes -t {window_id}",
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
        Create a new session with the data in `session`.
        """
        command = [
            self._bin,
            f"new-session -ds {session.name}",
            "-PF",
            "#{session_id}",
        ]
        response = subprocess.run(command, capture_output=True, text=True, check=True)
        session.id = response.stdout.strip()
        if len(session.windows) == 0:
            raise ValueError("Session must have at least one window")
        for window in session.windows:
            self._create_window(session.id, window)
        command = [self._bin, f"kill-window -t {session.id}.1"]
        subprocess.run(command, check=True)
        command = [self._bin, f"switch-client -t {session.id}"]
        subprocess.run(command, check=True)

    def _create_window(self, session_id: str, window: JmuxWindow) -> None:
        command = [
            self._bin,
            f"neww -t {session_id} -n {window.name}",
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
        command = [self._bin, f"kill-pane -t {window.id}.1"]
        subprocess.run(command, check=True)
        command = [self._bin, f"select-layout -t {window.id}", window.layout]
        subprocess.run(command, check=True)

    def _create_pane(self, window_id: str, pane: JmuxPane) -> None:
        command = [
            self._bin,
            f"splitw -t {window_id} -c {pane.current_dir}",
            "-PF",
            "#{pane_id}",
        ]
        if not pane.focus:
            command.append("-d")
        response = subprocess.run(command, capture_output=True, text=True, check=True)
        pane.id = response.stdout.strip()
