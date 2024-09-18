import unittest
import subprocess

from src.tmuxapi import TmuxApi


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


class TestTmuxApiMethods(unittest.TestCase):
    def setUp(self):
        self.tmux = TmuxApi()


if __name__ == "__main__":
    unittest.main()
