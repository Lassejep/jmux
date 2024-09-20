import unittest
import subprocess
import pathlib


def create_test_session():
    w1pane1 = {"path": str(pathlib.Path.home()), "is_active": False}
    w1pane2 = {"path": "/tmp", "is_active": True}
    w1pane3 = {"path": "/tmp", "is_active": False}
    w2pane1 = {"path": "/tmp", "is_active": True}
    window1 = {"name": "test_window1", "panes": [w1pane1, w1pane2, w1pane3]}
    window2 = {"name": "test_window2", "panes": [w2pane1]}
    session = {"name": "test_session", "windows": [window1, window2]}
    subprocess.run(["tmux", "new-session", "-d",
                   "-s", session["name"]], check=True)
    subprocess.run(["tmux", "rename-window", "-t",
                   f"{session['name']}:0", window1["name"]], check=True)
    subprocess.run(["tmux", "new-window", "-t",
                   session["name"], "-n", window2["name"]],
                   "-c", w2pane1["path"], check=True)
    subprocess.run(["tmux", "split-window", "-h",
                   "-t", f"{session['name']}:{window1['name']}.1",
                    "-c", w1pane2["path"]], check=True)
    subprocess.run(["tmux", "split-window", "-v",
                   "-t", f"{session['name']}:{window1['name']}.2",
                    "-c", w1pane3["path"], "-d"], check=True)
    return session


def kill_session(session_name: str):
    try:
        subprocess.run(["tmux", "kill-session", "-t", session_name],
                       check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        pass


if __name__ == "__main__":
    unittest.main()
