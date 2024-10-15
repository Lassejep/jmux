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
To save the current Tmux session run the following command while inside the tmux session you want to save.
```bash
jmux save
```

To load a saved session run the following command.
```bash
jmux load
```
It will prompt you for the name of the session you want to load.
Simply type the name of the session and press enter.
You will have to manually switch to the tmux session after loading it.

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
- [ ] Add the ability to rename saved sessions
- [ ] Create a small GUI for the program
- [ ] Make panes remember their command history
- [ ] Make panes remember their running processes and restart them when loading a session
- [ ] Tmux Plugin Manager support
