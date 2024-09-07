import unittest
import pathlib
import subprocess

import jmux


class TestTmuxPane(unittest.TestCase):
    def test_pane_object_creation(self):
        try:
            pane = jmux.TmuxPane(1)
        except Exception as e:
            self.fail("TmuxPane creation failed: " + str(e))
        self.assertEqual(pane.id, 1)
        self.assertEqual(pane.path, pathlib.Path().home())
        self.assertFalse(pane.is_active)
        self.assertFalse(pane.processes)


class TestTmuxWindow(unittest.TestCase):
    def setUp(self):
        subprocess.run(["tmux", "new-session", "-d",
                       "-s", "jmux_test"], check=True)
        subprocess.run(["tmux", "rename-window", "-t",
                       "jmux_test:0", "1"], check=True)
        subprocess.run(["tmux", "split-window", "-t",
                       "jmux_test:0", "-h"], check=True)
        subprocess.run(["tmux", "split-window", "-t",
                       "jmux_test:0", "-v"], check=True)

    def tearDown(self):
        subprocess.run(["tmux", "kill-session", "-t", "jmux_test"], check=True)

    def test_window_object_creation(self):
        try:
            window = jmux.TmuxWindow(1)
        except Exception as e:
            self.fail("TmuxWindow creation failed: " + str(e))
        self.assertEqual(window.id, 1)
        self.assertEqual(window.name, "1")
        self.assertFalse(window.layout)
        self.assertFalse(window.is_active)
        self.assertFalse(window.panes)

    def test_window_load_panes_from_tmux(self):
        window = jmux.TmuxWindow(1)
        window.load_panes_from_tmux()
        self.assertNotEqual(len(window.panes), 3)
