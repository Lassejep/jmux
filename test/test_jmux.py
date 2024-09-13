import unittest
import subprocess
import json

from src.session_manager import TmuxManager
from src.session_manager import TmuxPane, TmuxWindow, TmuxSession, TmuxBin


def create_test_session():
    subprocess.run(["tmux", "new-session", "-d",
                   "-s", "test_session"], check=True)
    subprocess.run(["tmux", "rename-window", "-t",
                   "test_session:1", "test_window1"], check=True)
    subprocess.run(["tmux", "new-window", "-t",
                   "test_session", "-n", "test_window2"], check=True)
    subprocess.run(["tmux", "new-window", "-t",
                   "test_session", "-n", "test_window2"], check=True)
    subprocess.run(["tmux", "split-window", "-h",
                   "-t", "test_session:1", "-c", "/tmp"], check=True)
    subprocess.run(["tmux", "split-window", "-v",
                   "-t", "test_session:1.1"], check=True)
    subprocess.run(["tmux", "split-window", "-v",
                   "-t", "test_session:2.1"], check=True)


def kill_test_session():
    try:
        subprocess.run(["tmux", "kill-session", "-t", "test_session"],
                       check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        pass


class TestTmuxBin(unittest.TestCase):
    def tearDown(self):
        kill_test_session()

    def test_get(self):
        create_test_session()
        tmux = TmuxBin()
        keys = ["session_windows"]
        target = "test_session"
        result = tmux.get(keys, target)
        self.assertEqual(result, "3")

    def test_get_multiple_keys(self):
        create_test_session()
        tmux = TmuxBin()
        keys = ["session_windows", "session_name"]
        target = "test_session"
        session_windows, session_name = tmux.get(keys, target)
        self.assertEqual(session_name, "test_session")
        self.assertEqual(session_windows, "3")

    def test_run(self):
        tmux = TmuxBin()
        cmd = ["new-session", "-d", "-s", "test_session"]
        tmux.run(cmd)
        sessions = subprocess.check_output(["tmux", "list-sessions"],
                                           text=True).strip()
        self.assertIn("test_session", sessions)


class TestTmuxPane(unittest.TestCase):
    def tearDown(self):
        kill_test_session()

    def test_build_from_tmux(self):
        create_test_session()
        pane = TmuxPane(1, "/tmp", True)
        pane.build_from_tmux("test_session", 1, 1)
        self.assertEqual(pane.id, 1)
        self.assertEqual(pane.path, "/tmp")
        self.assertEqual(pane.is_active, True)

    def test_create_in_tmux(self):
        create_test_session()
        pane = TmuxPane(1, "/tmp", True)
        pane.create_in_tmux("test_session", 2)
        result = subprocess.check_output(["tmux", "display-message", "-t",
                                          "test_session:2.1", "-p",
                                          "#{pane_index}:#{pane_current_path}:#{pane_active}:#{session_name}:#{window_index}"
                                          ], text=True).strip()
        print(result)
        self.assertIn("/tmp", result)


class TestTmuxManager(unittest.TestCase):
    def tearDown(self):
        kill_test_session()

    def test_save_session(self):
        panes = [
            TmuxPane(1, "/tmp", True),
            TmuxPane(2, "/tmp", False),
            TmuxPane(3, "/tmp", False),
        ]
        window1 = TmuxWindow(1, "test_window1", True, "tiled", panes)
        panes = [
            TmuxPane(1, "/tmp", True),
            TmuxPane(2, "/tmp", False),
        ]
        window2 = TmuxWindow(2, "test_window2", False, "tiled", panes)
        panes = [
            TmuxPane(1, "/tmp", True),
        ]
        window3 = TmuxWindow(3, "test_window2", False, "tiled", panes)
        session = TmuxSession("test_session", [window1, window2, window3])
        tm = TmuxManager()
        tm.save_session(session)
        session_file = tm._sessions_dir / "test_session.json"
        if not session_file.exists():
            self.fail("Failed to save session")
        with session_file.open() as f:
            saved_session = json.load(f)
        self.assertEqual(saved_session["name"], "test_session")
        self.assertEqual(len(saved_session["windows"]), 3)
        self.assertEqual(saved_session["windows"][0]["name"], "test_window1")
        self.assertEqual(saved_session["windows"][0]["is_active"], True)

    def test_load_session(self):
        tm = TmuxManager()
        session = tm.load_session("test_session")
        self.assertEqual(session.name, "test_session")
        self.assertEqual(len(session.windows), 3)
        self.assertEqual(session.windows[0].name, "test_window1")
        self.assertEqual(len(session.windows[0].panes), 3)
        self.assertEqual(session.windows[1].name, "test_window2")
        self.assertEqual(len(session.windows[1].panes), 2)
        self.assertEqual(session.windows[2].name, "test_window2")
        self.assertEqual(len(session.windows[2].panes), 1)
