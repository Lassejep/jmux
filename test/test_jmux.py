import unittest
import subprocess
import pathlib

from src.session_manager import TmuxBin, JmuxPane, JmuxWindow, JmuxSession
from src.session_manager import TmuxManager


def create_test_session():
    subprocess.run(["tmux", "new-session", "-d",
                   "-s", "test_session"], check=True)
    subprocess.run(["tmux", "rename-window", "-t",
                   "test_session:1", "test_window1"], check=True)
    subprocess.run(["tmux", "new-window", "-t",
                   "test_session", "-n", "test_window2"], check=True)
    subprocess.run(["tmux", "split-window", "-h",
                   "-t", "test_session:1.1", "-c", "/tmp"], check=True)
    subprocess.run(["tmux", "split-window", "-v",
                   "-t", "test_session:1.2", "-d"], check=True)


def kill_session(session_name: str):
    try:
        subprocess.run(["tmux", "kill-session", "-t", session_name],
                       check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        pass


class TestTmuxBinMethods(unittest.TestCase):
    def tearDown(self):
        kill_session("test_session")

    def test_get(self):
        create_test_session()
        tmux = TmuxBin()
        keys = ["session_windows"]
        target = "test_session"
        result = tmux.get(keys, target)
        self.assertEqual(result, "2")

    def test_get_multiple_keys(self):
        create_test_session()
        tmux = TmuxBin()
        keys = ["session_windows", "session_name"]
        target = "test_session"
        session_windows, session_name = tmux.get(keys, target)
        self.assertEqual(session_name, "test_session")
        self.assertEqual(session_windows, "2")

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
        kill_session("test_session")

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


class TestJmuxWindowMethods(unittest.TestCase):
    def setUp(self):
        create_test_session()
        self.TMUX_SESSION_NAME = "test_session"
        self.TMUX_WINDOW_INDEX = 1
        self.TMUX_WINDOW_NAME = "test_window1"
        self.TEST_WINDOW_NAME = "test_window2"
        self.TEST_WINDOW_INDEX = 3
        self.TEST_LAYOUT = "3455,172x38,0,0{106x38,0,0,113,65x38,107,0,1936}"
        self.test_pane1 = JmuxPane(1, "/tmp", True)
        self.test_pane2 = JmuxPane(2, "/tmp", False)
        self.window = JmuxWindow(self.TEST_WINDOW_INDEX, self.TEST_WINDOW_NAME,
                                 False, self.TEST_LAYOUT, [self.test_pane1,
                                                           self.test_pane2])

    def tearDown(self):
        kill_session("test_session")

    def test_build_from_tmux_returns_jmux_window(self):
        window = JmuxWindow.build_from_tmux(self.TMUX_SESSION_NAME,
                                            self.TMUX_WINDOW_INDEX)
        self.assertEqual(type(window), JmuxWindow)

    def test_build_from_tmux_correct_index(self):
        window = JmuxWindow.build_from_tmux(self.TMUX_SESSION_NAME,
                                            self.TMUX_WINDOW_INDEX)
        self.assertEqual(window.id, self.TMUX_WINDOW_INDEX)

    def test_build_from_tmux_correct_name(self):
        window = JmuxWindow.build_from_tmux(self.TMUX_SESSION_NAME,
                                            self.TMUX_WINDOW_INDEX)
        self.assertEqual(window.name, self.TMUX_WINDOW_NAME)

    def test_build_from_tmux_correct_active_state(self):
        window = JmuxWindow.build_from_tmux(self.TMUX_SESSION_NAME,
                                            self.TMUX_WINDOW_INDEX)
        self.assertFalse(window.is_active)

    def test_build_from_tmux_correct_layout(self):
        window = JmuxWindow.build_from_tmux(self.TMUX_SESSION_NAME,
                                            self.TMUX_WINDOW_INDEX)
        layout = subprocess.check_output(
            ["tmux", "display-message", "-t",
             f"{self.TMUX_SESSION_NAME}:{self.TMUX_WINDOW_INDEX}",
             "-p", "#{window_layout}"], text=True
        ).strip()
        self.assertEqual(window.layout, layout)

    def test_create_in_tmux_creates_new_tmux_window(self):
        self.window.create_in_tmux(self.TMUX_SESSION_NAME)
        windows = subprocess.check_output(
            ["tmux", "list-windows", "-t", self.TMUX_SESSION_NAME,
             "-F", "#{window_index}"], text=True
        ).strip()
        self.assertIn(str(self.TEST_WINDOW_INDEX), windows)

    def test_create_in_tmux_sets_correct_name(self):
        self.window.create_in_tmux(self.TMUX_SESSION_NAME)
        name = subprocess.check_output(
            ["tmux", "display-message", "-t",
             f"{self.TMUX_SESSION_NAME}:{self.TEST_WINDOW_INDEX}",
             "-p", "#{window_name}"], text=True
        ).strip()
        self.assertEqual(name, self.window.name)

    def test_create_in_tmux_sets_correct_active_state(self):
        self.window.create_in_tmux(self.TMUX_SESSION_NAME)
        active = subprocess.check_output(
            ["tmux", "display-message", "-t",
             f"{self.TMUX_SESSION_NAME}:{self.TEST_WINDOW_INDEX}",
             "-p", "#{window_active}"], text=True
        ).strip()
        active = active == "1"
        self.assertEqual(active, self.window.is_active)

    def test_create_in_tmux_creates_correct_number_of_panes(self):
        self.window.create_in_tmux(self.TMUX_SESSION_NAME)
        panes = subprocess.check_output(
            ["tmux", "list-panes", "-t",
             f"{self.TMUX_SESSION_NAME}:{self.TEST_WINDOW_INDEX}",
             "-F", "#{pane_index}"], text=True
        ).strip().split("\n")
        self.assertEqual(len(panes), len(self.window.panes))


class TestJmuxSessionMethods(unittest.TestCase):
    def setUp(self):
        create_test_session()
        self.TMUX_SESSION_NAME = "test_session"
        self.TEST_SESSION_NAME = "test_session2"
        self.TEST_SESSION_WINDOWS = 3
        self.test_window1 = JmuxWindow(
            1, "test_window1", True,
            "3455,172x38,0,0{106x38,0,0,113,65x38,107,0,1936}",
            [JmuxPane(1, "/tmp", True)]
        )
        self.test_window2 = JmuxWindow(
            2, "test_window2", False,
            "3455,172x38,0,0{106x38,0,0,113,65x38,107,0,1936}",
            [JmuxPane(1, "/tmp", True)]
        )
        self.test_window3 = JmuxWindow(
            3, "test_window3", False,
            "3455,172x38,0,0{106x38,0,0,113,65x38,107,0,1936}",
            [JmuxPane(1, "/tmp", True)]
        )
        self.session = JmuxSession(self.TEST_SESSION_NAME,
                                   [self.test_window1, self.test_window2,
                                    self.test_window3])

    def tearDown(self):
        kill_session("test_session")
        kill_session("test_session2")

    def test_build_from_tmux_returns_jmux_session(self):
        session = JmuxSession.build_from_tmux(self.TMUX_SESSION_NAME)
        self.assertEqual(type(session), JmuxSession)

    def test_build_from_tmux_correct_name(self):
        session = JmuxSession.build_from_tmux(self.TMUX_SESSION_NAME)
        self.assertEqual(session.name, self.TMUX_SESSION_NAME)

    def test_build_from_tmux_correct_number_of_windows(self):
        session = JmuxSession.build_from_tmux(self.TMUX_SESSION_NAME)
        windows = subprocess.check_output(
            ["tmux", "list-windows", "-t", self.TMUX_SESSION_NAME,
             "-F", "#{window_index}"], text=True
        ).strip().split("\n")
        self.assertEqual(len(session.windows), len(windows))

    def test_create_in_tmux_creates_new_tmux_session(self):
        self.session.create_in_tmux()
        sessions = subprocess.check_output(
            ["tmux", "list-sessions", "-F", "#{session_name}"], text=True
        ).strip().split("\n")
        self.assertIn(self.TEST_SESSION_NAME, sessions)

    def test_create_in_tmux_creates_correct_number_of_windows(self):
        self.session.create_in_tmux()
        windows = subprocess.check_output(
            ["tmux", "list-windows", "-t", self.TEST_SESSION_NAME,
             "-F", "#{window_index}"], text=True
        ).strip().split("\n")
        self.assertEqual(len(windows), len(self.session.windows))


class TestTmuxManagerMethods(unittest.TestCase):
    def setUp(self):
        create_test_session()
        self.TMUX_SESSION_NAME = "test_session"
        self.TEST_SESSION_NAME = "test_session2"
        self.TEST_SESSION_WINDOWS = 3
        self.test_window1 = JmuxWindow(
            1, "test_window1", True,
            "3455,172x38,0,0{106x38,0,0,113,65x38,107,0,1936}",
            [JmuxPane(1, "/tmp", True)]
        )
        self.test_window2 = JmuxWindow(
            2, "test_window2", False,
            "3455,172x38,0,0{106x38,0,0,113,65x38,107,0,1936}",
            [JmuxPane(1, "/tmp", True)]
        )
        self.test_window3 = JmuxWindow(
            3, "test_window3", False,
            "3455,172x38,0,0{106x38,0,0,113,65x38,107,0,1936}",
            [JmuxPane(1, "/tmp", True)]
        )
        self.session = JmuxSession(self.TEST_SESSION_NAME,
                                   [self.test_window1, self.test_window2,
                                    self.test_window3])
        self.manager = TmuxManager()
        self.session_path = pathlib.Path().home() / ".config" / "jmux" / \
            f"{self.TEST_SESSION_NAME}.json"

    def tearDown(self):
        kill_session("test_session")
        kill_session("test_session2")
        if self.session_path.exists():
            self.session_path.unlink()

    def test_save_session(self):
        self.manager.save_session(self.session)
        self.assertTrue(self.session_path.exists())

    def test_load_session(self):
        self.manager.save_session(self.session)
        loaded_session = self.manager.load_session(self.TEST_SESSION_NAME)
        self.assertEqual(loaded_session.name, self.TEST_SESSION_NAME)
        self.assertEqual(loaded_session.windows[0].name, "test_window1")
        self.assertEqual(loaded_session.windows[1].name, "test_window2")
        self.assertEqual(loaded_session.windows[2].name, "test_window3")


if __name__ == "__main__":
    unittest.main()
