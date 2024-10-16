#!/usr/bin/env python3
import argparse
import pathlib

from src import file_handler, session_manager, tmux_client


def create_manager(sessions_dir=None):
    client = tmux_client.TmuxClient()
    file_manager = file_handler.FileHandler(sessions_dir)
    return session_manager.SessionManager(file_manager, client)


def get_sessions(sessions_dir):
    for session_file in sessions_dir.iterdir():
        session_name = session_file.stem
        print(session_name)


def main(action, sessions_dir):
    manager = create_manager(sessions_dir)
    match action:
        case "save":
            manager.save_current_session()
        case "load":
            print("Available sessions:")
            get_sessions(sessions_dir)
            session_name = input("\nEnter session name: ")
            manager.load_session(session_name)
        case "delete":
            print("Available sessions:")
            get_sessions(sessions_dir)
            session_name = input("\nEnter session name: ")
            manager.delete_session_file(session_name)
        case "rename":
            print("Available sessions:")
            get_sessions(sessions_dir)
            session_name = input("\nEnter session name: ")
            new_name = input("\nEnter new session name: ")
            manager.rename_session(session_name, new_name)
        case "ls":
            print("Available sessions:")
            get_sessions(sessions_dir)
        case _:
            raise ValueError(f"Invalid action: {action}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "run",
        choices=("save", "load", "delete", "rename", "ls"),
        help="Action to perform",
    )
    parser.add_argument(
        "-d",
        "--sessions-dir",
        help="Directory to store session files",
        default="~/.jmux/",
    )
    args = parser.parse_args()
    sessions_dir = pathlib.Path(args.sessions_dir).expanduser()
    if not sessions_dir.is_dir():
        raise ValueError(f"Invalid sessions directory {sessions_dir}")
    action = args.run
    main(action, sessions_dir)
