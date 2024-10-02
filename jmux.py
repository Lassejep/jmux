#!/usr/bin/env python3

import argparse
import subprocess
import pathlib

from src import tmux_client
from src import elements
from src import session_manager


def getfilepath(name):
    jmux_dir = pathlib.Path.home() / ".jmux"
    if not jmux_dir.exists():
        jmux_dir.mkdir()
    path = jmux_dir / f"{name}.json"
    return path


def create_manager():
    tmux = tmux_client.TmuxClient(subprocess)
    loader = elements.JmuxLoader(tmux)
    builder = elements.JmuxBuilder(tmux)
    return session_manager.SessionManager(loader, builder)


def main(action):
    manager = create_manager()
    match action:
        case "save":
            file_path = getfilepath("current")
            manager.save_session(file_path)
        case "load":
            session_name = input("Enter session name: ")
            file_path = getfilepath(session_name)
            manager.load_session(file_path)
        case _:
            raise ValueError(f"Invalid action: {action}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", choices=("save", "load"),
                        help="Action to perform")
    args = parser.parse_args()
    main(args.run)
