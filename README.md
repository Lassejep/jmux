## Jmux
A simple TMUX session manager written in Python.
This project is mainly for me to experiment with doing TDD in Python, but maybe it will be useful for you as well.

## Installation
```bash
git clone "https://github.com/lassejep/jmux.git"
```

### Installing python dependencies
The project dependencies are currently only for testing purposes and therefore not strictly necessary.
However, if you are having trouble getting the program to work you might want to install them.
```bash
pip install -r requirements.txt
```

### Running tests
Before using jmux I recommend you run the tests to make sure everything is working as intended.
```bash
python -m pytest
```

## Usage
### Running the program

Navigate to the jmux directory and run the following command:
```bash
./jmux
```
This will open a TUI where you can manage your tmux sessions.

### Keybinds
- j, k, down, up: Move the cursor up and down
- h, l, left, right: Switches between the two menus
- q, Esc: Quits the program
- Enter: switches to the selected session or loads the session if it isn't running
- o: Creates a new tmux session
- s: Saves the current tmux session
- x: Kills the selected tmux session
- d: Deletes the selected saved session
- r: Renames the selected session


## Dependencies
### Required
- Python 3.11 or newer
- Tmux 3.4 or newer

### Optional
- Pytest 8.3.3 or newer
- Pytest-mock 3.14.0 or newer

## TODO
- [x] Fix bug where the program doesn't recognize already running tmux session.
- [x] Add the ability to delete saved sessions
- [x] Add the ability to rename saved sessions
- [x] Create a small TUI for the program
- [ ] Fix keybinds for the TUI
- [ ] Implement better input field in the TUI
- [ ] Add proper error handling to the TUI
- [ ] Tmux Plugin Manager support
- [ ] Make panes remember their command history
- [ ] Make panes remember their running processes and restart them when loading a session
- [ ] Create a small GUI for the program
