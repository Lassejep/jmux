import unittest
import subprocess
import json

from src.session_manager import TmuxManager, TmuxSession, TmuxWindow, TmuxPane


class TestTmuxManager(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        try:
            subprocess.run(["tmux", "kill-session", "-t", "test_session"],
                           check=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            pass

    def create_test_session(self):
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

    def test_get_current_session(self):
        self.create_test_session()
        tm = TmuxManager()
        try:
            session = tm._get_session("test_session")
        except Exception:
            self.fail("Failed to get current session")
        self.assertEqual(session.name, "test_session")
        self.assertEqual(len(session.windows), 3)
        self.assertEqual(session.windows[0].name, "test_window1")
        self.assertEqual(len(session.windows[0].panes), 3)
        self.assertEqual(session.windows[1].name, "test_window2")
        self.assertEqual(len(session.windows[1].panes), 2)
        self.assertEqual(session.windows[2].name, "test_window2")
        self.assertEqual(len(session.windows[2].panes), 1)

    def test_create_session(self):
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
        tm.create_session(session)
        sessions = subprocess.check_output(["tmux", "list-sessions"],
                                           text=True).strip()
        self.assertIn("test_session", sessions)
        windows = subprocess.check_output(["tmux", "list-windows", "-t",
                                          "test_session"], text=True).strip()
        self.assertIn("test_window1", windows)
        self.assertIn("test_window2", windows)
        self.assertEqual(windows.count("\n") + 1, 3)
        panes = subprocess.check_output(["tmux", "list-panes", "-t",
                                        "test_session:1"], text=True).strip()
        self.assertEqual(panes.count("\n") + 1, 3)
        panes = subprocess.check_output(["tmux", "list-panes", "-t",
                                        "test_session:2"], text=True).strip()
        self.assertEqual(panes.count("\n") + 1, 2)
        panes = subprocess.check_output(["tmux", "list-panes", "-t",
                                        "test_session:3"], text=True).strip()
        self.assertEqual(panes.count("\n") + 1, 1)

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
