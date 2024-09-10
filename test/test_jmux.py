import unittest
import pathlib
import subprocess

import jmux


class TestTmuxPane(unittest.TestCase):
    def test_object_creation(self):
        try:
            pane = jmux.TmuxPane(1)
        except Exception as e:
            self.fail("TmuxPane creation failed: " + str(e))
        self.assertEqual(pane.id, 1)
        self.assertEqual(pane.path, pathlib.Path().home())
        self.assertFalse(pane.is_active)


class TestTmuxWindow(unittest.TestCase):
    def setUp(self):
        subprocess.run(["tmux", "new-session", "-d",
                       "-s", "jmux_test"], check=True)
        subprocess.run(["tmux", "rename-window", "-t",
                       "jmux_test:1", "1"], check=True)
        subprocess.run(["tmux", "split-window", "-t",
                       "jmux_test:1", "-h"], check=True)
        subprocess.run(["tmux", "split-window", "-t",
                       "jmux_test:1", "-v"], check=True)
        out = subprocess.run(["tmux", "list-sessions", "-F",
                             "#{session_name}:#{session_id}"],
                             capture_output=True)
        for line in out.stdout.decode("utf-8").split("\n"):
            if "jmux_test" in line:
                self.session_id = line.split(":")[1]

        out = subprocess.run(["tmux", "list-windows", "-t", "jmux_test",
                              "-F", "#{window_name}"], capture_output=True)
        self.window_name = out.stdout.decode("utf-8").strip()

        self.window_dict = {
            "session": self.session_id,
            "name": "test_window",
            "layout": "91ed,172x38,0,0{86x38,0,0,1,85x38,87,0[85x29,87,0,2,85x8,87,30,294]}",
            "is_active": True,
            "panes": [
                {"id": 1, "path": "/home/user",
                    "is_active": True},
                {"id": 2, "path": "/home/user",
                    "is_active": False},
                {"id": 3, "path": "/home/user",
                    "is_active": False},
            ],
        }

    def tearDown(self):
        subprocess.run(["tmux", "kill-session", "-t", "jmux_test"], check=True)

    def test_object_creation(self):
        try:
            window = jmux.TmuxWindow(self.session_id, self.window_name)
        except Exception as e:
            self.fail("TmuxWindow creation failed: " + str(e))
        self.assertEqual(window.session, self.session_id)
        self.assertEqual(window.name, self.window_name)
        self.assertFalse(window.layout)
        self.assertFalse(window.is_active)
        self.assertFalse(window.panes)

    def test_load_panes_from_tmux(self):
        window = jmux.TmuxWindow(self.session_id, self.window_name)
        window.load_panes_from_tmux()
        self.assertEqual(len(window.panes), 3)

    def test_to_dict(self):
        window = jmux.TmuxWindow(self.session_id, self.window_name)
        window.load_panes_from_tmux()
        window_dict = window.to_dict()
        self.assertEqual(window_dict["name"], self.window_name)
        self.assertEqual(window_dict["panes"][0]["id"], 1)

    def test_load_panes_from_dict(self):
        window = jmux.TmuxWindow(self.session_id, self.window_name)
        window.load_panes_from_tmux()
        window_dict = window.to_dict()
        window = jmux.TmuxWindow(self.session_id, self.window_name)
        window.load_panes_from_dict(window_dict["panes"])
        self.assertEqual(len(window.panes), 3)
        self.assertEqual(window.panes[0].id, 1)

    def test_create_window(self):
        window = jmux.TmuxWindow(self.window_dict["session"],
                                 self.window_dict["name"])
        window.load_panes_from_dict(self.window_dict["panes"])
        window.create_window()
        out = subprocess.run(["tmux", "list-windows", "-t",
                              "jmux_test", "-F", "#{window_name}"],
                             capture_output=True)
        self.assertIn(window.name, out.stdout.decode("utf-8"))


class TestTmuxSession(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        err = subprocess.run(["tmux", "kill-session", "-t",
                              "jmux_test"], stderr=subprocess.PIPE)
        if err.stderr:
            pass

    def create_test_session(self):
        subprocess.run(["tmux", "new-session", "-d",
                       "-s", "jmux_test"], check=True)
        out = subprocess.run(["tmux", "list-sessions", "-F",
                             "#{session_name}:#{session_id}"],
                             capture_output=True)
        for line in out.stdout.decode("utf-8").split("\n"):
            if "jmux_test" in line:
                self.session_id = line.split(":")[1]

    def test_object_creation(self):
        try:
            session = jmux.TmuxSession("jmux_test")
        except Exception as e:
            self.fail("TmuxSession creation failed: " + str(e))
        self.assertEqual(session.name, "jmux_test")
        self.assertFalse(session.windows)

    def test_load_from_tmux(self):
        self.create_test_session()
        session = jmux.TmuxSession("jmux_test")
        session.load_from_tmux()
        self.assertTrue(session.windows)
