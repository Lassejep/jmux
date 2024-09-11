#!/usr/bin/env python3

import argparse
from src import session_manager


def main(args):
    tm = session_manager.TmuxManager()
    if args.run == "save":
        sess = tm.get_current_session()
        tm.save_session(sess)
    elif args.run == "load":
        session_name = input("Enter session name: ")
        tm.load_session(session_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run", choices=("save", "load"),
                        help="Action to perform")
    args = parser.parse_args()
    main(args)
