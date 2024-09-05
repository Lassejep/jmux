import unittest
import jmux


class TestTmuxPane(unittest.TestCase):
    def setUp(self):
        self.pane_data = {
            "1": {
                "is_active": True,
                "current_path": "~/",
                "processes": [
                    {
                        "pid": 1234,
                        "name": "bash",
                        "command": "bash",
                        "args": []
                    }
                ]
            }
        }

    def tearDown(self):
        pass

    def test_pane_creation(self):
        try:
            jmux.TmuxPane()
        except Exception as e:
            self.fail("TmuxPane creation failed: " + str(e))

    def test_pane_load_from_tmux(self):
        try:
            pane = jmux.TmuxPane()
            pane.load_from_tmux()
        except Exception as e:
            self.fail("TmuxPane load_from_tmux failed: " + str(e))
