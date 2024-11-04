## Jmux
A simple TMUX session manager written in Python.
This project is mainly for me to experiment with TDD in Python, but maybe it will be useful for you as well.

## TPM Installation (Recommended)
The easiest way to install jmux is to use [tpm](https://github.com/tmux-plugins/tpm).
Just add the following line to your .tmux.conf file.
```bash
set -g @plugin 'Lassejep/jmux'
```
Then you simply press your prefix key (usually ctrl+b) followed by I to install the plugin.
After that, you should be able to open jmux by pressing your prefix key (usually ctrl+b) followed by o.

## Manual Installation
First, you need to clone the repository to your local machine.
```bash
git clone "https://github.com/Lassejep/jmux.git"
```

Then you simply need to add the following line to your tmux configuration file.
The tmux configuration file is usually located at ~/.tmux.conf.
```tmux
bind-key o display-popup -BEE /path/to/jmux/main.py
```
Change "/path/to/jmux/main.py" to the actual path of the main.py file.
Then you simply need to restart tmux or reload the configuration file.
```bash
tmux source-file ~/.tmux.conf
```
After that, you should be able to open jmux by pressing your prefix key (usually ctrl+b) followed by o.

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

If you have installed the program using TPM you can simply press your prefix key (usually ctrl+b) followed by o.
This will open a TUI where you can manage your tmux sessions.

### Keybinds
- j, k, down, up: Move the cursor up and down
- h, l, left, right: Switches between the two menus
- q, Esc: Quits the program
- Enter: switches to the selected session or loads the session if it isn't running
- o: Creates a new tmux session
- s: Saves the selected session
- d: If in the saved sessions menu, deletes the selected session, if in the running sessions menu, kills the selected session
- r: Renames the selected session


## Dependencies
### Required
- Python 3.11 or newer
- Tmux 3.4 or newer

### Optional
- Pytest 8.3.3 or newer
- Pytest-mock 3.14.0 or newer
- tpm 3.1.0 or newer

## TODO
- [x] Fix bug where the program doesn't recognize already running tmux session.
- [x] Add the ability to delete saved sessions
- [x] Add the ability to rename saved sessions
- [x] Create a small TUI for the program
- [x] Implement better input field in the TUI
- [x] Fix keybinds for the TUI
- [x] Tmux Plugin Manager support
- [x] Add better tests for the curses presenter class
- [x] Remove the presenter deactivate method
- [ ] Add proper error handling to the TUI
- [ ] Fix color scheme for the TUI
- [ ] Implement scrolling in the TUI
- [ ] Fix bug where the program doesn't work if tmux indexing doesn't start at 1
- [ ] Make panes remember their running processes and restart them when loading a session
- [ ] Make panes remember their command history

### Features I might add in the future
- [ ] Create a GUI for the program
- [ ] Add implementation for more terminal multiplexers
- [ ] Add implementation for other tools with panes, windows, and sessions
