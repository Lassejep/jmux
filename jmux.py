#!/usr/bin/env python3
import pathlib

from src.services import CursesGui, JmuxModel, JsonHandler, TmuxClient


def create_manager(sessions_dir=None):
    client = TmuxClient()
    file_manager = JsonHandler(sessions_dir)
    return JmuxModel(client, file_manager)


def main():
    sessions_dir = pathlib.Path.home() / ".jmux"
    manager = create_manager(sessions_dir)
    view = CursesGui(manager)
    view.start()


if __name__ == "__main__":
    main()
