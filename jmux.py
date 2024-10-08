#!/usr/bin/env python3
import argparse
import pathlib

from src import session_manager, tmux_client


def create_manager(sessions_dir=None):
    client = tmux_client.TmuxClient()
    return session_manager.SessionManager(sessions_dir, client)


def main(action, sessions_dir):
    manager = create_manager(sessions_dir)
    match action:
        case "save":
            manager.save_current_session()
        case "load":
            session_name = input("Enter session name: ")
            manager.load_session(session_name)
        case _:
            raise ValueError(f"Invalid action: {action}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", choices=("save", "load"), help="Action to perform")
    parser.add_argument(
        "-d",
        "--sessions-dir",
        help="Directory to store session files",
        default="~/.jmux/",
    )
    args = parser.parse_args()
    sessions_dir = pathlib.Path(args.sessions_dir).expanduser()
    action = args.run
    main(action, sessions_dir)
