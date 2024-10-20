import pytest

from src.services import JmuxModel


class TestConstructor:
    @pytest.fixture(autouse=True)
    def setup(self, mock_multiplexer, mock_file_handler):
        self.multiplexer = mock_multiplexer
        self.file_handler = mock_file_handler

    def test_invalid_multiplexer_argument_raises_value_error(self):
        with pytest.raises(ValueError):
            JmuxModel(self.file_handler, self.file_handler)
        with pytest.raises(ValueError):
            JmuxModel(None, self.file_handler)

    def test_invalid_file_handler_argument_raises_value_error(self):
        with pytest.raises(ValueError):
            JmuxModel(self.multiplexer, self.multiplexer)
        with pytest.raises(ValueError):
            JmuxModel(self.multiplexer, None)

    def test_valid_arguments_set_multiplexer_and_file_handler(self):
        model = JmuxModel(self.multiplexer, self.file_handler)
        assert model.multiplexer == self.multiplexer
        assert model.file_handler == self.file_handler

    def test_returns_instance_of_jmux_model(self):
        model = JmuxModel(self.multiplexer, self.file_handler)
        assert isinstance(model, JmuxModel)
