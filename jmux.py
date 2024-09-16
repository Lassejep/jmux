#!/usr/bin/env python3

import argparse
from src import session_manager


def main(args):
    tm = session_manager.TmuxManager()
    if args.run == "save":
        tm.save_current_session()
    elif args.run == "load":
        session_name = input("Enter session name: ")
        tm.load_session(session_name)
    elif args.run == "list":
        for session in tm.list_sessions():
            print(session)
    else:
        raise ValueError(f"Invalid action: {args.run}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", choices=("save", "load", "list"),
                        help="Action to perform")
    args = parser.parse_args()
    main(args)
