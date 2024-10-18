#!/usr/bin/env python3
import pathlib

from src import curses_gui, file_handler, session_manager, tmux_client


def create_manager(sessions_dir=None):
    client = tmux_client.TmuxClient()
    file_manager = file_handler.FileHandler(sessions_dir)
    return session_manager.SessionManager(file_manager, client)


def main():
    sessions_dir = pathlib.Path.home() / ".jmux"
    manager = create_manager(sessions_dir)
    view = curses_gui.CursesGUI(manager)
    view.presenter.run()


if __name__ == "__main__":
    main()
