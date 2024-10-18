from src.jmux_session import JmuxPane, JmuxSession, JmuxWindow


def dict_to_JmuxSession(session_data: dict) -> JmuxSession:
    session_data["windows"] = [
        dict_to_JmuxWindow(window) for window in session_data["windows"]
    ]
    session = JmuxSession(**session_data)
    return session


def dict_to_JmuxWindow(window_data: dict) -> JmuxWindow:
    window_data["panes"] = [dict_to_JmuxPane(pane) for pane in window_data["panes"]]
    window = JmuxWindow(**window_data)
    return window


def dict_to_JmuxPane(pane_data: dict) -> JmuxPane:
    pane = JmuxPane(**pane_data)
    return pane
