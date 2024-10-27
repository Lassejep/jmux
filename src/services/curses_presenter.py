from typing import Any, Optional, Union

from src.interfaces import Model, Presenter, SessionHandler, StateMachine, View
from src.models import CursesStates, Event, SessionLabel


class CursesPresenter(Presenter[None]):
    def __init__(
        self,
        view: View,
        model: Model,
        statemachine: StateMachine[CursesStates],
        multiplexer_menu: Presenter[Optional[SessionLabel]],
        file_menu: Presenter[Optional[SessionLabel]],
        message_window: Presenter[Optional[Union[bool, str]]],
    ) -> None:
        """
        Main presenter for the Curses GUI.
        """
        if not view or not isinstance(view, View):
            raise TypeError("View must implement the View interface")
        if not model or not isinstance(model, Model):
            raise TypeError("Model must implement the Model interface")
        if not statemachine or not isinstance(statemachine, StateMachine):
            raise TypeError("Statemachine must be an instance of StateMachine")
        self.view = view
        self.model = model
        self.statemachine = statemachine
        self.multiplexer_menu = multiplexer_menu
        self.file_menu = file_menu
        self.message_window = message_window
        self.view.render()

    def update_view(self) -> None:
        """
        Update views based on the current state.
        """
        match self.statemachine.get_state():
            case CursesStates.MULTIPLEXER_MENU:
                self.multiplexer_menu.update_view()
            case CursesStates.FILE_MENU:
                self.file_menu.update_view()
            case CursesStates.MESSAGE_WINDOW:
                self.message_window.update_view()

    def get_event(self) -> Event:
        """
        Get an event from the presenter based on the current state.
        """
        match self.statemachine.get_state():
            case CursesStates.MULTIPLEXER_MENU:
                return self.multiplexer_menu.get_event()
            case CursesStates.FILE_MENU:
                return self.file_menu.get_event()
            case CursesStates.MESSAGE_WINDOW:
                return self.message_window.get_event()
            case _:
                return Event.EXIT

    def handle_event(self, event: Event, *args: Any) -> None:
        """
        Handle a given `event`.
        """
        current_menu = self.multiplexer_menu
        if self.statemachine.get_state() == CursesStates.FILE_MENU:
            current_menu = self.file_menu
        match event:
            case Event.EXIT:
                self.statemachine.set_state(CursesStates.EXIT)
            case Event.MOVE_LEFT:
                self.statemachine.set_state(CursesStates.MULTIPLEXER_MENU)
            case Event.MOVE_RIGHT:
                self.statemachine.set_state(CursesStates.FILE_MENU)
            case Event.MOVE_UP:
                current_menu.handle_event(event)
            case Event.MOVE_DOWN:
                current_menu.handle_event(event)
            case Event.CREATE_SESSION:
                name = self.message_window.handle_event(event)
                if not isinstance(name, str):
                    self.message_window.handle_event(
                        Event.SHOW_MESSAGE, "Error: no name provided"
                    )
                    return
                self.model.create_session(name)
            case Event.KILL_SESSION:
                session = current_menu.handle_event(Event.GET_SESSION)
                if not session:
                    self.message_window.handle_event(
                        Event.SHOW_MESSAGE, "Error: no session selected"
                    )
                    return
                if not self.message_window.handle_event(event, session.name):
                    self.message_window.handle_event(
                        Event.SHOW_MESSAGE, "Error: session not killed"
                    )
                    return
                self.model.kill_session(session)
            case Event.DELETE_SESSION:
                session = current_menu.handle_event(Event.GET_SESSION)
                if not session:
                    self.message_window.handle_event(
                        Event.SHOW_MESSAGE, "Error: no session selected"
                    )
                    return
                if not self.message_window.handle_event(event, session.name):
                    self.message_window.handle_event(
                        Event.SHOW_MESSAGE, "Error: session not deleted"
                    )
                    return
                self.model.delete_session(session)
            case Event.RENAME_SESSION:
                session = current_menu.handle_event(Event.GET_SESSION)
                if not session:
                    self.message_window.handle_event(
                        Event.SHOW_MESSAGE, "Error: no session selected"
                    )
                    return
                new_name = self.message_window.handle_event(event)
                if not isinstance(new_name, str):
                    self.message_window.handle_event(
                        Event.SHOW_MESSAGE, "Error: no name provided"
                    )
                    return
                self.model.rename_session(session, new_name)
            case Event.SAVE_SESSION:
                session = current_menu.handle_event(Event.GET_SESSION)
                if not session:
                    self.message_window.handle_event(
                        Event.SHOW_MESSAGE, "Error: no session selected"
                    )
                    return
                if session in self.model.list_saved_sessions():
                    if not self.message_window.handle_event(event, session.name):
                        self.message_window.handle_event(
                            Event.SHOW_MESSAGE, "Error: session not saved"
                        )
                        return
                self.model.save_session(session)
            case Event.LOAD_SESSION:
                session = current_menu.handle_event(Event.GET_SESSION)
                if not session:
                    self.message_window.handle_event(
                        Event.SHOW_MESSAGE, "Error: no session selected"
                    )
                    return
                self.model.load_session(session)
            case Event.NOOP:
                pass
            case _:
                self.message_window.handle_event(
                    Event.SHOW_MESSAGE, f"Error: running command {event}"
                )


class MenuPresenter(Presenter[Optional[SessionLabel]]):
    def __init__(
        self, view: View, model: Model, session_handler: SessionHandler
    ) -> None:
        """
        Presenter for Menus.
        """
        if not view or not isinstance(view, View):
            raise TypeError("View must implement the View interface")
        if not model or not isinstance(model, Model):
            raise TypeError("Model must implement the Model interface")
        self.view = view
        self.model = model
        self.session_handler: SessionHandler = session_handler
        self.position = 0

    def update_view(self) -> None:
        """
        Get data from the model and update the view.
        """
        self.sessions = self.session_handler.update_sessions()
        self.view.render(self.session_handler.get_annotated_sessions(), self.position)

    def get_event(self) -> Event:
        """
        Get event from the view.
        """
        return self.view.get_command()

    def handle_event(self, event: Event, *args: Any) -> Optional[SessionLabel]:
        """
        Handle a given `event`.
        """
        match event:
            case Event.MOVE_UP:
                self._cursor_up()
            case Event.MOVE_DOWN:
                self._cursor_down()
            case Event.GET_SESSION:
                return self.session_handler.sessions[self.position]
        return None

    def _cursor_up(self) -> None:
        if self.position > 0:
            self.position -= 1
        else:
            self.position = 0

    def _cursor_down(self) -> None:
        if self.position < len(self.sessions) - 1:
            self.position += 1
        else:
            self.position = len(self.sessions) - 1


class MessagePresenter(Presenter[Optional[Union[bool, str]]]):
    def __init__(self, view: View, model: Model) -> None:
        """
        Presenter for the message window.
        """
        if not view or not isinstance(view, View):
            raise TypeError("View must be an instance of View")
        if not model or not isinstance(model, Model):
            raise TypeError("Model must be an instance of Model")
        self.view = view
        self.model = model

    def update_view(self) -> None:
        """
        Clear the message window.
        """
        self.view.render("")

    def get_event(self) -> Event:
        """
        Get event from the view.
        """
        return self.view.get_command()

    def handle_event(self, event: Event, *args: Any) -> Optional[Union[bool, str]]:
        """
        Handle a given `event`.
        """
        match event:
            case Event.SHOW_MESSAGE:
                self.view.render(args[0])
            case Event.CREATE_SESSION:
                return self.view.get_input("Enter a name for the new session: ")
            case Event.RENAME_SESSION:
                return self.view.get_input(f"Enter a new name for {args[0]}: ")
            case Event.DELETE_SESSION:
                return self.view.get_confirmation(
                    f"Are you sure you want to delete the session {args[0]}? (y/N)"
                )
            case Event.KILL_SESSION:
                return self.view.get_confirmation(
                    f"Are you sure you want to kill the session {args[0]}? (y/N)"
                )
            case Event.SAVE_SESSION:
                return self.view.get_confirmation(
                    f"Are you sure you want to overwrite the session {args[0]}? (y/N)"
                )
        return None
