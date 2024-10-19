import pytest

from src.jmux_model import JmuxModel


class TestConstructor:
    @pytest.fixture
    def setup(self, mock_multiplexer, mock_file_handler):
        self.multiplexer = mock_multiplexer
        self.file_handler = mock_file_handler

    def test_throws_exception_when_multiplexer_is_invalid(self):
        with pytest.raises(Exception):
            JmuxModel(self.file_handler, self.file_handler)
        with pytest.raises(Exception):
            JmuxModel(None, self.file_handler)

    def test_throws_exception_when_file_handler_is_invalid(self):
        with pytest.raises(Exception):
            JmuxModel(self.multiplexer, self.multiplexer)
        with pytest.raises(Exception):
            JmuxModel(self.multiplexer, None)
