import curses
from typing import Tuple


class InputBox:
    def __init__(self, location: Tuple[int, int], size: Tuple[int, int], init_str: str):
        self.location = location
        self.size = size
        self.text = init_str
        self.running = False
        self.text_field = curses.newpad(1, 999)
        self.text_field.keypad(True)

    def _do_action(self, key):
        curs_pos = self.text_field.getyx()
        match key:
            case 27:
                self.running = False
                return None
            case 10:
                self.running = False
                return self.gather()
            case curses.KEY_BACKSPACE:
                if curs_pos[1] > 0:
                    if curs_pos[1] < len(self.text):
                        self.text = (
                            self.text[: curs_pos[1] - 1] + self.text[curs_pos[1] :]
                        )
                    else:
                        self.text = self.text[:-1]
                    self.text_field.delch(curs_pos[0], curs_pos[1] - 1)
                if self.view_loc[1] > 0:
                    self.view_loc = (
                        self.view_loc[0],
                        self.view_loc[1] - 1,
                        self.view_loc[2],
                        self.view_loc[3],
                        self.view_loc[4],
                        self.view_loc[5],
                    )
            case curses.KEY_LEFT:
                if curs_pos[1] > 0:
                    self.text_field.move(curs_pos[0], curs_pos[1] - 1)
                if self.view_loc[1] > 0:
                    self.view_loc = (
                        self.view_loc[0],
                        self.view_loc[1] - 1,
                        self.view_loc[2],
                        self.view_loc[3],
                        self.view_loc[4],
                        self.view_loc[5],
                    )
            case curses.KEY_RIGHT:
                if curs_pos[1] < len(self.text):
                    self.text_field.move(curs_pos[0], curs_pos[1] + 1)
                if curs_pos[1] > (
                    self.widget.size[1] - len(self.prompt) - 2
                ) and curs_pos[1] < len(self.text):
                    self.view_loc = (
                        self.view_loc[0],
                        self.view_loc[1] + 1,
                        self.view_loc[2],
                        self.view_loc[3],
                        self.view_loc[4],
                        self.view_loc[5],
                    )
            case _:
                try:
                    if key < 32 or key > 126:
                        raise ValueError
                    if curs_pos[1] < len(self.text):
                        self.text = (
                            self.text[: curs_pos[1]]
                            + chr(key)
                            + self.text[curs_pos[1] :]
                        )
                    else:
                        self.text += chr(key)
                    if self.secret:
                        self.text_field.insch("*")
                    else:
                        self.text_field.insch(key)
                    self.text_field.move(curs_pos[0], curs_pos[1] + 1)
                    if curs_pos[1] > (self.widget.size[1] - len(self.prompt) - 2):
                        self.view_loc = (
                            self.view_loc[0],
                            self.view_loc[1] + 1,
                            self.view_loc[2],
                            self.view_loc[3],
                            self.view_loc[4],
                            self.view_loc[5],
                        )
                except ValueError:
                    return self.gather()
        return self.gather()
