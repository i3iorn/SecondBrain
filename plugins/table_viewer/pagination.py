from enum import Enum
from typing import TYPE_CHECKING

import wx

from .components.button import PVButton
from .components.panel import BasePanel
from .helpers import status_message

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

    def __init__(self, tv: 'TableViewer') -> None:
        """
        Initialize the Pagination Panel.

        Args:
            parent (wx.Panel): The parent panel for the Pagination Panel.
            plugin (TableViewer): The Table Viewer plugin instance.
        """
        super().__init__(tv.panel)
        self.logger = tv.logger.getChild("pagination")
        self.status_bar = tv.status_bar
        self.__plugin = tv
        self.__setup_ui()

    def __setup_ui(self) -> None:
        """
        Set up the user interface.

        This method creates the buttons for the Pagination Panel and adds them to the sizer.
        """
        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.__sizer)

        for name in self.BUTTONS:
            self.__create_button(name)

    def __create_button(self, name: ButtonNames) -> None:
        """
        Create a pagination button.

        This method creates a button for the Pagination Panel with the given name and adds it to the sizer.

        Args:
            name (ButtonNames): The name of the button to create.
        """
        func = getattr(self, name.value.lower())
        button = PVButton(self, label=name.value.title(), callback=func, disabled=True)
        setattr(self, f"__{name.value.lower()}_button", button)

    @status_message(f"Loading previous page")
    def prev(self, event: wx.Event) -> None:
        """
        Go back one page.

        This method is called when the "Prev" button is clicked. It decrements the offset in the Table Viewer plugin
        and calls the `load_data` method to update the grid.

        Args:
            event (wx.Event): The event that triggered this callback.
        """
        if self.__plugin.offset - self.__plugin.sample_size < 0:
            self.logger.debug("Cannot go back any further")
            return
        self.__plugin.offset -= self.__plugin.sample_size

        getattr(self, "__next_button").enable()
        getattr(self, "__last_button").enable()

        self.__plugin.load_data()

    @status_message(f"Loading next page")
    def next(self, event: wx.Event) -> None:
        """
        Go forward one page.

        This method is called when the "Next" button is clicked. It increments the offset in the Table Viewer plugin
        and calls the `load_data` method to update the grid.

        Args:
            event (wx.Event): The event that triggered this callback.
        """
        if self.__plugin.offset + self.__plugin.sample_size >= self.__plugin.get_total_rows():
            self.logger.debug("Cannot go forward any further")
            return
        self.__plugin.offset += self.__plugin.sample_size

        getattr(self, "__first_button").enable()
        getattr(self, "__prev_button").enable()

        self.__plugin.load_data()

    @status_message(f"Loading first page")
    def first(self, event: wx.Event) -> None:
        """
        Go to the first page.

        This method is called when the "First" button is clicked. It sets the offset in the Table Viewer plugin to 0
        and calls the `load_data` method to update the grid.

        Args:
            event (wx.Event): The event that triggered this callback.
        """
        self.__plugin.offset = 0

        getattr(self, "__first_button").disable()
        getattr(self, "__prev_button").disable()
        getattr(self, "__next_button").enable()
        getattr(self, "__last_button").enable()

        self.__plugin.load_data()

    @status_message(f"Loading last page")
    def last(self, event: wx.Event) -> None:
        """
        Go to the last page.

        This method is called when the "Last" button is clicked. It sets the offset in the Table Viewer plugin to the
        total number of rows minus the sample size, and calls the `load_data` method to update the grid.

        Args:
            event (wx.Event): The event that triggered this callback.
        """
        if self.__plugin.get_total_rows() < self.__plugin.sample_size:
            self.logger.debug("Cannot go to last page")
            getattr(self, "__last_button").disable()
            getattr(self, "__next_button").disable()
            return

        self.__plugin.offset = self.__plugin.get_total_rows() - self.__plugin.sample_size

        getattr(self, "__first_button").enable()
        getattr(self, "__prev_button").enable()
        getattr(self, "__next_button").disable()
        getattr(self, "__last_button").disable()

        self.__plugin.load_data()

    @status_message(f"Activate pagination")
    def activate(self) -> None:
        """
        Activate all buttons.

        This method enables all the pagination buttons, allowing the user to navigate through the data.
        """
        for name in self.BUTTONS:
            button = getattr(self, f"__{name.value.lower()}_button")
            button.enable()

    @status_message(f"Deactivate pagination")
    def deactivate(self) -> None:
        """
        Deactivate all buttons.

        This method disables all the pagination buttons, preventing the user from navigating through the data.
        """
        for name in self.BUTTONS:
            button = getattr(self, f"__{name.value.lower()}_button")
            button.disable()
