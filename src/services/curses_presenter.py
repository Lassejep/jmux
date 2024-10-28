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
        self.view = view
        self.model = model
        self.statemachine = statemachine
        self.multiplexer_menu = multiplexer_menu
        self.file_menu = file_menu
        self.message_window = message_window
        self.active = False
        self._validate_input()
        self._render_starting_screen()

    def _validate_input(self) -> None:
        if not isinstance(self.view, View):
            raise TypeError("View must implement the View interface")
        if not isinstance(self.model, Model):
            raise TypeError("Model must implement the Model interface")
        if not isinstance(self.statemachine, StateMachine):
            raise TypeError("Statemachine must be an instance of StateMachine")
        if not isinstance(self.multiplexer_menu, Presenter):
            raise TypeError("Multiplexer menu must be an instance of Presenter")
        if not isinstance(self.file_menu, Presenter):
            raise TypeError("File menu must be an instance of Presenter")
        if not isinstance(self.message_window, Presenter):
            raise TypeError("Message window must be an instance of Presenter")

    def _render_starting_screen(self) -> None:
        self.view.render()
        self.multiplexer_menu.active = True
        self.multiplexer_menu.update_view()
        self.file_menu.update_view()
        self.message_window.update_view()

    def update_view(self) -> None:
        """
        Update views based on the current state.
        """
        self.message_window.update_view()
        self.file_menu.update_view()
        self.multiplexer_menu.update_view()

    def get_event(self) -> Event:
        """
        Get an event from the presenter based on the current state.
        """
        self.update_view()
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
        match event:
            case Event.EXIT:
                self.statemachine.set_state(CursesStates.EXIT)
            case Event.MOVE_LEFT:
                self.statemachine.set_state(CursesStates.MULTIPLEXER_MENU)
                self.multiplexer_menu.active = True
                self.file_menu.active = False
            case Event.MOVE_RIGHT:
                self.statemachine.set_state(CursesStates.FILE_MENU)
                self.file_menu.active = True
                self.multiplexer_menu.active = False
            case Event.MOVE_UP:
                self._move_up()
            case Event.MOVE_DOWN:
                self._move_down()
            case Event.CREATE_SESSION:
                name = self._get_new_name(
                    "Enter a name for the new session: ", "Error: no name provided"
                )
                self.model.create_session(name)
            case Event.KILL_SESSION:
                session = self._get_session()
                if self._confirm(
                    f"Kill {session.name}? (y/N)", "Error: session not killed"
                ):
                    self.model.kill_session(session)
            case Event.DELETE_SESSION:
                session = self._get_session()
                if self._confirm(
                    f"Delete {session.name}? (y/N)", "Error: session not deleted"
                ):
                    self.model.delete_session(session)
            case Event.RENAME_SESSION:
                session = self._get_session()
                if not self._confirm(
                    f"Rename {session.name}? (y/N)", "Error: not renamed"
                ):
                    return
                new_name = self._get_new_name(
                    f"Enter a new name for {session.name}: ", "Error: no name provided"
                )
                self.model.rename_session(session, new_name)
            case Event.SAVE_SESSION:
                session = self._get_session()
                if session in self.model.list_saved_sessions() and not self._confirm(
                    f"Overwrite {session.name}? (y/N)", "Error: session not saved"
                ):
                    return
                self.model.save_session(session)
            case Event.LOAD_SESSION:
                session = self._get_session()
                self.model.load_session(session)
            case Event.UNKNOWN:
                pass
            case _:
                self.message_window.handle_event(
                    Event.SHOW_MESSAGE, f"Error: running command {event}"
                )

    def _get_session(self) -> SessionLabel:
        """
        Get the currently selected session.
        """
        if self.statemachine.get_state() == CursesStates.FILE_MENU:
            session = self.file_menu.handle_event(Event.GET_SESSION)
        else:
            session = self.multiplexer_menu.handle_event(Event.GET_SESSION)
        if not session or not isinstance(session, SessionLabel):
            raise ValueError("No session selected")
        return session

    def _confirm(self, prompt: str, error_message: str) -> bool:
        """
        Get a confirmation from the user.
        """
        confirmation = self.message_window.handle_event(Event.CONFIRM, prompt)
        if not isinstance(confirmation, bool):
            raise ValueError("No confirmation provided")
        if not confirmation:
            self.message_window.handle_event(Event.SHOW_MESSAGE, error_message)
        return confirmation

    def _get_new_name(self, prompt: str, error_message: str) -> str:
        """
        Get a new name for a session.
        """
        new_name = self.message_window.handle_event(Event.INPUT, prompt)
        if not new_name:
            self.message_window.handle_event(Event.SHOW_MESSAGE, error_message)
            return ""
        if not isinstance(new_name, str):
            raise ValueError("No name provided")
        return new_name

    def _move_up(self) -> None:
        """
        Move the cursor up.
        """
        if self.statemachine.get_state() == CursesStates.FILE_MENU:
            self.file_menu.handle_event(Event.MOVE_UP)
        else:
            self.multiplexer_menu.handle_event(Event.MOVE_UP)

    def _move_down(self) -> None:
        """
        Move the cursor down.
        """
        if self.statemachine.get_state() == CursesStates.FILE_MENU:
            self.file_menu.handle_event(Event.MOVE_DOWN)
        else:
            self.multiplexer_menu.handle_event(Event.MOVE_DOWN)


class MenuPresenter(Presenter[Optional[SessionLabel]]):
    def __init__(
        self, view: View, model: Model, session_handler: SessionHandler
    ) -> None:
        """
        Presenter for Menus.
        """
        self.view = view
        self.model = model
        self.session_handler: SessionHandler = session_handler
        self.cursor_position = 0
        self.active = False
        self._validate_input()

    def _validate_input(self) -> None:
        if not isinstance(self.view, View):
            raise TypeError("View must implement the View interface")
        if not isinstance(self.model, Model):
            raise TypeError("Model must implement the Model interface")
        if not isinstance(self.session_handler, SessionHandler):
            raise TypeError("SessionHandler must be an instance of SessionHandler")

    def update_view(self) -> None:
        """
        Get data from the model and update the view.
        """
        self.sessions = self.session_handler.update_sessions()
        self.view.render(
            self.session_handler.get_annotated_sessions(),
            self.cursor_position,
            self.active,
        )

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
                return self.session_handler.sessions[self.cursor_position]
        return None

    def _cursor_up(self) -> None:
        if self.cursor_position > 0:
            self.cursor_position -= 1
        else:
            self.cursor_position = 0

    def _cursor_down(self) -> None:
        if self.cursor_position < len(self.sessions) - 1:
            self.cursor_position += 1
        else:
            self.cursor_position = len(self.sessions) - 1


class MessagePresenter(Presenter[Optional[Union[bool, str]]]):
    def __init__(self, view: View, model: Model) -> None:
        """
        Presenter for the message window.
        """
        self.view = view
        self.model = model
        self.active = False
        self._validate_input()

    def _validate_input(self) -> None:
        if not isinstance(self.view, View):
            raise TypeError("View must implement the View interface")
        if not isinstance(self.model, Model):
            raise TypeError("Model must implement the Model interface")

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
                self.view.show_message(args[0])
            case Event.CONFIRM:
                return self.view.get_confirmation(args[0])
            case Event.INPUT:
                return self.view.get_input(args[0])
        return None
