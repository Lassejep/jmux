#!/usr/bin/env python3
import pathlib

from src import CursesGui, JmuxModel, JsonHandler, TmuxClient

if __name__ == "__main__":
    sessions_dir = pathlib.Path.home() / ".jmux"
    file_handler = JsonHandler(sessions_dir)
    multiplexer = TmuxClient()
    model = JmuxModel(multiplexer, file_handler)
    gui = CursesGui(model)
    gui.run()
