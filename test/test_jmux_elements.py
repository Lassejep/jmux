import pytest
import subprocess

from src.multiplexer import TmuxAPI
from src.elements import JmuxPane
from src.elements import JmuxLoader


class TestJmuxLoader:
    """Test the JmuxLoader class."""

    def test_throws_exception_given_invalid_multiplexer(self):
        """Test that an exception is thrown if the multiplexer is invalid."""
        with pytest.raises(ValueError):
            JmuxLoader(None)


class TestJmuxLoaderLoadPanesMethod:
    """Test the JmuxLoader.load_panes method."""

    def test_load_from_no_target_throws_exception(self):
        """Test that an exception is thrown if the target is invalid."""
        loader = JmuxLoader(TmuxAPI(subprocess))
        with pytest.raises(ValueError):
            loader.load_panes("")

    def test_load_from_valid_target_returns_list_of_panes(self):
        """Test that the method returns a list of JmuxPane objects."""
        loader = JmuxLoader(TmuxAPI(subprocess))
        panes = loader.load_panes("@1")
        assert all(isinstance(pane, JmuxPane) for pane in panes)

    def test_load_from_target_with_one_pane_returns_list_with_one_pane(self):
        """Test that the method returns a list with one JmuxPane object."""
        loader = JmuxLoader(TmuxAPI(subprocess))
        panes = loader.load_panes("@1")
        assert len(panes) == 1
        assert isinstance(panes[0], JmuxPane)

    def test_load_from_target_with_multiple_panes_returns_list_with_all_panes(
            self):
        """Test that the method returns a list with all JmuxPane objects."""
        loader = JmuxLoader(TmuxAPI(subprocess))
        panes = loader.load_panes("@1")
        assert len(panes) == 2
        assert all(isinstance(pane, JmuxPane) for pane in panes)
