from pathlib import Path

import pytest

from src.multiplexer import TerminalMultiplexerClient
from src.session_manager import SessionManager
from src.elements import JmuxLoader


@pytest.fixture
def multiplexer(mocker):
    yield mocker.Mock(spec=TerminalMultiplexerClient)


@pytest.fixture
def jmux_loader(multiplexer, mocker):
    jmux_loader = JmuxLoader(multiplexer)
    yield mocker.Mock(spec=jmux_loader)


@pytest.fixture
def session_manager(multiplexer, jmux_loader):
    yield SessionManager(multiplexer, jmux_loader)


@pytest.fixture
def file(mocker):
    path = Path("/tmp/test")
    yield mocker.Mock(spec=path)


class TestSessionManagerConstructor:
    def test_throws_exception_if_multiplexer_is_none(self, jmux_loader):
        with pytest.raises(ValueError):
            SessionManager(None, jmux_loader)

    def test_throws_exception_if_multiplexer_wrong_type(self, jmux_loader):
        with pytest.raises(ValueError):
            SessionManager("multiplexer", jmux_loader)

    def test_throws_exception_if_multiplexer_not_running(
            self, multiplexer, jmux_loader):
        multiplexer.is_running.return_value = False
        with pytest.raises(EnvironmentError):
            SessionManager(multiplexer, jmux_loader)

    def test_throws_exception_if_jmux_loader_is_none(
            self, multiplexer, mocker):
        with pytest.raises(ValueError):
            SessionManager(multiplexer, None)


class TestSaveSessionMethod:
    def test_throws_exception_if_file_path_is_not_pathlib_path(
            self, session_manager):
        with pytest.raises(TypeError):
            session_manager.save_session("test_path")

    def test_creates_file_if_not_exists(self, session_manager,
                                        file, jmux_loader):
        file.exists.return_value = False
        file.touch.return_value = None
        jmux_loader.load.return_value = "$1"
        session_manager.save_session(file)
        file.touch.assert_called_once()

    def test_gets_current_session_data(
            self, session_manager, file, jmux_loader):
        jmux_loader.load.return_value = "$1"
        session_manager.save_session(file)
        jmux_loader.load.assert_called_once()

    def test_writes_current_session_data_to_file(
            self, session_manager, file, jmux_loader):
        session_manager.save_session(file)
