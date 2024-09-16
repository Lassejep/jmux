## Unfinished Project
A simple TMUX session manager

## Installation
```bash
git clone "https://github.com/lassejep/jmux.git"
chmod +x jmux.py
sudo ln -s /path/to/jmux.py /usr/local/bin/jmux
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

To list all saved sessions run the following command.
```bash
jmux list
```

## Dependencies
- Python 3.11 or newer
- Tmux 3.4 or newer

## TODO
- [ ] Fix the bug where the bug where the send-keys func is inconsistent
- [ ] Add the ability to delete saved sessions
- [ ] Add the ability to rename saved sessions
- [ ] Create a small GUI for the program
- [ ] Make panes remember their command history
- [ ] Make panes remember their running processes and restart them when loading a session
- [ ] Tmux Plugin Manager support
- [ ] Add more extensive error handling
- [ ] Add logging
- [ ] Add more exhaustive testing
