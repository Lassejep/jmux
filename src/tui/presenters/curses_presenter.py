from typing import Optional, Union

from src.data_models import CursesStates, Event, SessionLabel
from src.interfaces import Model, Presenter, View


class CursesPresenter(Presenter[None]):
    def __init__(
        self,
        view: View[Event],
        model: Model,
        multiplexer_menu: Presenter[Optional[SessionLabel]],
        file_menu: Presenter[Optional[SessionLabel]],
        command_bar: Presenter[Union[bool, str, None]],
    ) -> None:
        """
        Main presenter for the Curses GUI.
        """
        self.view: View[Event] = view
        self.model: Model = model
        self.multiplexer_menu: Presenter[Optional[SessionLabel]] = multiplexer_menu
        self.file_menu: Presenter[Optional[SessionLabel]] = file_menu
        self.command_bar: Presenter[Union[bool, str, None]] = command_bar
        self.active: bool = False
        self.state: CursesStates = CursesStates.MULTIPLEXER_MENU
        self._render_starting_screen()

    def _render_starting_screen(self) -> None:
        self.view.render()
        self.multiplexer_menu.activate()
        self.multiplexer_menu.update_view()
        self.file_menu.update_view()
        self.command_bar.update_view()

    def activate(self) -> None:
        """
        Activate the presenter.
        """
        self.active = True
        while self.active:
            self.update_view()
            event = self.get_event()
            self.handle_event(event)

    def deactivate(self) -> None:
        """
        Deactivate the presenter.
        """
        self.active = False

    def update_view(self) -> None:
        """
        Update views based on the current state.
        """
        self.command_bar.update_view()
        self.file_menu.update_view()
        self.multiplexer_menu.update_view()

    def get_event(self) -> Event:
        """
        Get an event from the presenter based on the current state.
        """
        match self.state:
            case CursesStates.MULTIPLEXER_MENU:
                return self.multiplexer_menu.get_event()
            case CursesStates.FILE_MENU:
                return self.file_menu.get_event()
        return Event.EXIT

    def handle_event(self, event: Event) -> None:
        """
        Handle a given `event`.
        """
        match event:
            case Event.EXIT:
                self.deactivate()
            case Event.MOVE_LEFT:
                self._move_left()
            case Event.MOVE_RIGHT:
                self._move_right()
            case Event.MOVE_UP:
                self._move_up()
            case Event.MOVE_DOWN:
                self._move_down()
            case Event.LOAD_SESSION:
                self._load_session()
            case Event.CREATE_SESSION:
                self._create_session()
            case Event.KILL_SESSION:
                self._kill_session()
            case Event.SAVE_SESSION:
                self._save_session()
            case Event.DELETE_SESSION:
                self._delete_session()
            case Event.RENAME_SESSION:
                self._rename_session()
            case Event.UNKNOWN:
                pass
            case _:
                self._invalid_command(event)

    def _get_session(self) -> SessionLabel:
        """
        Get the currently selected session.
        """
        if self.state == CursesStates.FILE_MENU:
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
        confirmation = self.command_bar.handle_event(Event.CONFIRM, prompt)
        if not isinstance(confirmation, bool) or not confirmation:
            self.command_bar.handle_event(
                Event.SHOW_MESSAGE, error_message, is_error=True
            )
            return False
        return confirmation

    def _get_new_name(self, prompt: str, error_message: str) -> str:
        """
        Get a new name for a session.
        """
        new_name = self.command_bar.handle_event(Event.INPUT, prompt)
        if not isinstance(new_name, str) or not new_name:
            self.command_bar.handle_event(
                Event.SHOW_MESSAGE, error_message, is_error=True
            )
            return ""
        return new_name

    def _move_left(self) -> None:
        """
        Move the cursor left.
        """
        self.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.activate()
        self.file_menu.deactivate()

    def _move_right(self) -> None:
        """
        Move the cursor right.
        """
        self.state = CursesStates.FILE_MENU
        self.file_menu.activate()
        self.multiplexer_menu.deactivate()

    def _move_up(self) -> None:
        """
        Move the cursor up.
        """
        if self.state == CursesStates.FILE_MENU:
            self.file_menu.handle_event(Event.MOVE_UP)
        else:
            self.multiplexer_menu.handle_event(Event.MOVE_UP)

    def _move_down(self) -> None:
        """
        Move the cursor down.
        """
        if self.state == CursesStates.FILE_MENU:
            self.file_menu.handle_event(Event.MOVE_DOWN)
        else:
            self.multiplexer_menu.handle_event(Event.MOVE_DOWN)

    def _load_session(self) -> None:
        """
        Load the currently selected session.
        """
        try:
            session = self._get_session()
            self.model.load_session(session)
        except ValueError as error:
            self.command_bar.handle_event(Event.SHOW_MESSAGE, str(error), is_error=True)

    def _create_session(self) -> None:
        """
        Create a new session.
        """
        try:
            name = self._get_new_name(
                "Enter a name for the new session: ", "Error: no name provided"
            )
            if name:
                self.model.create_session(name)
        except ValueError as error:
            self.command_bar.handle_event(Event.SHOW_MESSAGE, str(error), is_error=True)

    def _kill_session(self) -> None:
        """
        Kill the currently selected session.
        """
        try:
            session = self._get_session()
            if self._confirm(
                f"Kill {session.name}? (y/N)", "Error: session not killed"
            ):
                self.model.kill_session(session)
        except ValueError as error:
            self.command_bar.handle_event(Event.SHOW_MESSAGE, str(error), is_error=True)

    def _save_session(self) -> None:
        """
        Save the currently selected session.
        """
        try:
            session = self._get_session()
            if session in self.model.list_saved_sessions() and not self._confirm(
                f"Overwrite {session.name}? (y/N)", "Error: session not saved"
            ):
                return
            self.model.save_session(session)
        except ValueError as error:
            self.command_bar.handle_event(Event.SHOW_MESSAGE, str(error), is_error=True)

    def _delete_session(self) -> None:
        """
        Delete the currently selected session.
        """
        try:
            session = self._get_session()
            if self._confirm(
                f"Delete {session.name}? (y/N)", "Error: session not deleted"
            ):
                self.model.delete_session(session)
        except ValueError as error:
            self.command_bar.handle_event(Event.SHOW_MESSAGE, str(error), is_error=True)

    def _rename_session(self) -> None:
        """
        Rename the currently selected session.
        """
        try:
            session = self._get_session()
            if not self._confirm(f"Rename {session.name}? (y/N)", "Error: not renamed"):
                return
            new_name = self._get_new_name(
                f"Enter a new name for {session.name}: ", "Error: no name provided"
            )
            if new_name:
                self.model.rename_session(session, new_name)
        except ValueError as error:
            self.command_bar.handle_event(Event.SHOW_MESSAGE, str(error), is_error=True)

    def _invalid_command(self, command: Event) -> None:
        """
        Handle an invalid command.
        """
        self.command_bar.handle_event(
            Event.SHOW_MESSAGE, f"Error: running command {command}", is_error=True
        )
