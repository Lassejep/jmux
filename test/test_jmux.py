import unittest
import subprocess

from src.session_manager import TmuxBin, JmuxPane


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
                   "-t", "test_session:1.1", "-c", "/tmp"], check=True)
    subprocess.run(["tmux", "split-window", "-v",
                   "-t", "test_session:1.2", "-d"], check=True)
    subprocess.run(["tmux", "split-window", "-v",
                   "-t", "test_session:2.1"], check=True)


def kill_test_session():
    try:
        subprocess.run(["tmux", "kill-session", "-t", "test_session"],
                       check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        pass


class TestTmuxBinMethods(unittest.TestCase):
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

    def test_send_keys(self):
        create_test_session()
        tmux = TmuxBin()
        TEST_PATH = "/tmp"
        tmux.send_keys(f"cd {TEST_PATH}", "test_session:1.1")
        path = subprocess.check_output(["tmux", "display-message", "-t",
                                        "test_session:1.1", "-p",
                                        "#{pane_current_path}"],
                                       text=True).strip()
        self.assertEqual(path, TEST_PATH)


class TestJmuxPaneMethods(unittest.TestCase):
    def setUp(self):
        create_test_session()
        self.TMUX_SESSION_NAME = "test_session"
        self.TMUX_WINDOW_INDEX = 1
        self.TMUX_PANE_INDEX = 2
        self.TMUX_PANE_PATH = "/tmp"
        self.TEST_PANE_INDEX = 4
        self.pane = JmuxPane(self.TEST_PANE_INDEX, self.TMUX_PANE_PATH, True)

    def tearDown(self):
        kill_test_session()

    def test_build_from_tmux_returns_jmux_pane(self):
        pane = JmuxPane.build_from_tmux(self.TMUX_SESSION_NAME,
                                        self.TMUX_WINDOW_INDEX,
                                        self.TMUX_PANE_INDEX)
        self.assertEqual(type(pane), JmuxPane)

    def test_build_from_tmux_correct_index(self):
        pane = JmuxPane.build_from_tmux(self.TMUX_SESSION_NAME,
                                        self.TMUX_WINDOW_INDEX,
                                        self.TMUX_PANE_INDEX)
        self.assertEqual(pane.id, self.TMUX_PANE_INDEX)

    def test_build_from_tmux_correct_path(self):
        pane = JmuxPane.build_from_tmux(self.TMUX_SESSION_NAME,
                                        self.TMUX_WINDOW_INDEX,
                                        self.TMUX_PANE_INDEX)
        self.assertEqual(pane.path, self.TMUX_PANE_PATH)

    def test_build_from_tmux_correct_active_state(self):
        pane = JmuxPane.build_from_tmux(self.TMUX_SESSION_NAME,
                                        self.TMUX_WINDOW_INDEX,
                                        self.TMUX_PANE_INDEX)
        self.assertTrue(pane.is_active)

    def test_create_in_tmux_creates_new_tmux_pane(self):
        self.pane.create_in_tmux(
            self.TMUX_SESSION_NAME, self.TMUX_WINDOW_INDEX)
        panes = subprocess.check_output(
            ["tmux", "list-panes", "-t",
             f"{self.TMUX_SESSION_NAME}:{self.TMUX_WINDOW_INDEX}",
             "-F", "#{pane_index}"], text=True
        ).strip()
        self.assertIn(str(self.TEST_PANE_INDEX), panes)

    def test_create_in_tmux_sets_correct_path(self):
        self.pane.create_in_tmux(
            self.TMUX_SESSION_NAME, self.TMUX_WINDOW_INDEX)
        path = subprocess.check_output(
            ["tmux", "display-message", "-t",
             f"{self.TMUX_SESSION_NAME}:{
                 self.TMUX_WINDOW_INDEX}.{self.TEST_PANE_INDEX}",
             "-p", "#{pane_current_path}"], text=True
        ).strip()
        self.assertEqual(path, self.pane.path)

    def test_create_in_tmux_sets_correct_active_state(self):
        self.pane.create_in_tmux(
            self.TMUX_SESSION_NAME, self.TMUX_WINDOW_INDEX)
        active = subprocess.check_output(
            ["tmux", "display-message", "-t",
             f"{self.TMUX_SESSION_NAME}:{
                 self.TMUX_WINDOW_INDEX}.{self.TEST_PANE_INDEX}",
             "-p", "#{pane_active}"], text=True
        ).strip()
        active = active == "1"
        self.assertEqual(active, self.pane.is_active)
