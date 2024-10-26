from typing import Any

from src.interfaces import Model, Presenter, SessionHandler, StateMachine, View
from src.models import CursesStates, Event, SessionLabel


class CursesPresenter(Presenter):
    def __init__(
        self, view: View, model: Model, statemachine: StateMachine[CursesStates]
    ) -> None:
        """
        Presenter for the GUI.
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

    def update_view(self) -> None:
        """
        Get data from the model and update the view.
        """
        self.view.render()

    def get_event(self) -> Event:
        """
        Get event from the view.
        """
        raise NotImplementedError

    def handle_event(self, event: Event, *args: Any) -> None:
        """
        Handle a given `event`.
        """
        raise NotImplementedError


class MenuPresenter(Presenter):
    def __init__(
        self,
        view: View,
        model: Model,
        statemachine: StateMachine[CursesStates],
        session_handler: SessionHandler,
    ) -> None:
        """
        Presenter for Menus.
        """
        if not view or not isinstance(view, View):
            raise TypeError("View must implement the View interface")
        if not model or not isinstance(model, Model):
            raise TypeError("Model must implement the Model interface")
        if not statemachine or not isinstance(statemachine, StateMachine):
            raise TypeError("Statemachine must implement the StateMachine interface")
        self.view = view
        self.model = model
        self.statemachine = statemachine
        self.session_handler: SessionHandler = session_handler
        self._update_sessions()
        self.position = 0

    def __call__(self) -> None:
        self.update_view()
        self.handle_event(self.get_event())

    def _update_sessions(self) -> None:
        self.sessions = self.session_handler.update_sessions()

    def update_view(self) -> None:
        """
        Get data from the model and update the view.
        """
        self._update_sessions()
        self.view.render(self.session_handler.get_annotated_sessions(), self.position)

    def get_event(self) -> Event:
        """
        Get event from the view.
        """
        return self.view.get_command()

    def handle_event(self, event: Event, *args: Any) -> None:
        """
        Handle a given `event`.
        """
        match event:
            case Event.MOVE_UP:
                self._cursor_up()
            case Event.MOVE_DOWN:
                self._cursor_down()
            case Event.LOAD_SESSION:
                self.model.load_session(self._get_session())
            case Event.EXIT:
                self.statemachine.set_state(CursesStates.EXIT)
            case Event.MOVE_LEFT:
                self.statemachine.set_state(CursesStates.MULTIPLEXER_MENU)
            case Event.MOVE_RIGHT:
                self.statemachine.set_state(CursesStates.FILE_MENU)
            case Event.CREATE_SESSION:
                self.statemachine.set_state(CursesStates.CREATE_SESSION)
            case Event.SAVE_SESSION:
                self.statemachine.set_state(CursesStates.SAVE_SESSION)
            case Event.DELETE_SESSION:
                self.statemachine.set_state(CursesStates.DELETE_SESSION)
            case Event.KILL_SESSION:
                self.statemachine.set_state(CursesStates.KILL_SESSION)
            case Event.RENAME_SESSION:
                self.statemachine.set_state(CursesStates.RENAME_SESSION)
            case _:
                pass

    def _get_session(self) -> SessionLabel:
        return self.sessions[self.position]

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


class MessagePresenter(Presenter):
    def __init__(
        self, view: View, model: Model, statemachine: StateMachine[CursesStates]
    ) -> None:
        """
        Presenter for the message window.
        """
        if not view or not isinstance(view, View):
            raise TypeError("View must be an instance of View")
        if not model or not isinstance(model, Model):
            raise TypeError("Model must be an instance of Model")
        if not statemachine or not isinstance(statemachine, StateMachine):
            raise TypeError("Statemachine must be an instance of StateMachine")
        self.view = view
        self.model = model
        self.statemachine = statemachine

    def __call__(self) -> None:
        self.update_view()
        self.handle_event(self.get_event())

    def update_view(self) -> None:
        """
        Get data from the model and update the view.
        """
        self.view.render("")

    def get_event(self) -> Event:
        """
        Get event from the view.
        """
        return self.view.get_command()

    def handle_event(self, event: Event, *args: Any) -> None:
        """
        Handle a given `event`.
        """
        if event == Event.EXIT:
            self.statemachine.set_state(CursesStates.EXIT)
        state = self.statemachine.get_state()
        match state:
            case CursesStates.CREATE_SESSION:
                self.view.get_input("Enter session name: ")
            case CursesStates.SAVE_SESSION:
                self.view.get_confirmation("Overwrite the current save? (y/N)")
            case CursesStates.DELETE_SESSION:
                self.view.get_confirmation("Delete the session save? (y/N)")
            case CursesStates.KILL_SESSION:
                self.view.get_confirmation("Kill the session? (y/N)")
            case CursesStates.RENAME_SESSION:
                self.view.get_input("Enter new session name: ")
            case _:
                pass
