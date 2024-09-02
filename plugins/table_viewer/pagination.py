from enum import Enum
from typing import TYPE_CHECKING

import wx

from .components.button import PVButton
from .components.panel import BasePanel

if TYPE_CHECKING:
    from . import TableViewer


class ButtonNames(Enum):
    """
    The names of the pagination buttons.

    These names are used to identify the buttons in the Pagination Panel.

    Attributes:
        FIRST (str): The "First" button.
        PREV (str): The "Prev" button.
        NEXT (str): The "Next" button.
        LAST (str): The "Last" button
    """
    FIRST = "First"
    PREV = "Prev"
    NEXT = "Next"
    LAST = "Last"


class Pagination(BasePanel):
    """
    The Pagination Panel for the Table Viewer.

    This panel contains buttons to navigate through the data in the file. The buttons include:
    - First: Go to the first page.
    - Prev: Go back one page.
    - Next: Go forward one page.
    - Last: Go to the last page.

    The buttons are disabled if they cannot be used (e.g., the "Prev" button is disabled when on the first page).

    Attributes:
        BUTTONS (tuple): A tuple of button names, used to iterate over the buttons.
        logger (logging.Logger): The logger for the pagination panel.
        __plugin (TableViewer): The Table Viewer plugin instance.
        __sizer (wx.BoxSizer): The main sizer for the panel, which contains the buttons.
        __first_button (PVButton): The "First" button.
        __prev_button (PVButton): The "Prev" button.
        __next_button (PVButton): The "Next" button.
        __last_button (PVButton): The "Last" button.
    """
    BUTTONS = ButtonNames

    def __init__(self, parent: wx.Panel) -> None:
        """
        Initialize the Pagination Panel.

        Args:
            parent (wx.Panel): The parent panel for the Pagination Panel
        """
        super().__init__(parent)
        self.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
        self.logger = parent.logger.getChild("pagination")

        for name in self.BUTTONS:
            func = getattr(self, name.value.lower())
            button = PVButton(self, label=name.value.title(), callback=func, disabled=True)
            setattr(self, f"__{name.value.lower()}_button", button)

    @property
    def offset(self) -> int:
        """
        Get the offset for the Table Viewer.

        Returns:
            int: The offset for the Table Viewer.
        """
        return self.Parent.offset

    @offset.setter
    def offset(self, value: int) -> None:
        """
        Set the offset for the Table Viewer.

        Args:
            value (int): The new offset for the Table Viewer.
        """
        self.Parent.offset = value

    @property
    def sample_size(self) -> int:
        """
        Get the sample size for the Table Viewer.

        Returns:
            int: The sample size for the Table Viewer.
        """
        return self.Parent.sample_size

    @property
    def show_data(self):
        """
        Show the data in the Table Viewer.

        Returns:
            Callable: The `show_data` method in the Table Viewer plugin.
        """
        return self.Parent.show_data

    def prev(self, event: wx.Event) -> None:
        """
        Go back one page.

        This method is called when the "Prev" button is clicked. It decrements the offset in the Table Viewer plugin
        and calls the `load_data` method to update the grid.

        Args:
            event (wx.Event): The event that triggered this callback.
        """
        if self.Parent.offset - self.sample_size < 0:
            self.logger.debug("Cannot go back any further")
            return
        self.offset -= self.sample_size

        getattr(self, "__next_button").enable()
        getattr(self, "__last_button").enable()

        self.show_data()

    def next(self, event: wx.Event) -> None:
        """
        Go forward one page.

        This method is called when the "Next" button is clicked. It increments the offset in the Table Viewer plugin
        and calls the `load_data` method to update the grid.

        Args:
            event (wx.Event): The event that triggered this callback.
        """
        if self.offset + self.sample_size >= self.Parent.row_count:
            self.logger.debug("Cannot go forward any further")
            return
        self.offset += self.sample_size

        getattr(self, "__first_button").enable()
        getattr(self, "__prev_button").enable()

        self.show_data()

    def first(self, event: wx.Event) -> None:
        """
        Go to the first page.

        This method is called when the "First" button is clicked. It sets the offset in the Table Viewer plugin to 0
        and calls the `load_data` method to update the grid.

        Args:
            event (wx.Event): The event that triggered this callback.
        """
        self.offset = 0

        getattr(self, "__first_button").disable()
        getattr(self, "__prev_button").disable()
        getattr(self, "__next_button").enable()
        getattr(self, "__last_button").enable()

        self.show_data()

    def last(self, event: wx.Event) -> None:
        """
        Go to the last page.

        This method is called when the "Last" button is clicked. It sets the offset in the Table Viewer plugin to the
        total number of rows minus the sample size, and calls the `load_data` method to update the grid.

        Args:
            event (wx.Event): The event that triggered this callback.
        """
        if self.Parent.row_count < self.sample_size:
            self.logger.debug("Cannot go to last page")
            getattr(self, "__last_button").disable()
            getattr(self, "__next_button").disable()
            return

        self.offset = self.Parent.row_count - self.sample_size

        getattr(self, "__first_button").enable()
        getattr(self, "__prev_button").enable()
        getattr(self, "__next_button").disable()
        getattr(self, "__last_button").disable()

        self.show_data()

    def activate(self) -> None:
        """
        Activate all buttons.

        This method enables all the pagination buttons, allowing the user to navigate through the data.
        """
        for name in self.BUTTONS:
            button = getattr(self, f"__{name.value.lower()}_button")
            button.enable()

    def deactivate(self) -> None:
        """
        Deactivate all buttons.

        This method disables all the pagination buttons, preventing the user from navigating through the data.
        """
        for name in self.BUTTONS:
            button = getattr(self, f"__{name.value.lower()}_button")
            button.disable()
