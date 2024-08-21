from typing import TYPE_CHECKING

import wx

from src.plugins.parquet_viewer.components.button import PVButton

if TYPE_CHECKING:
    from src.plugins.parquet_viewer import ParquetViewer


class Pagination(wx.Panel):
    """
    The Pagination Panel for the Parquet Viewer

    This panel contains buttons to navigate through the data in the Parquet file.

    The buttons are:
    - First: Go to the first page
    - Prev: Go back one page
    - Next: Go forward one page
    - Last: Go to the last page

    The buttons are disabled if they cannot be used.
    """
    BUTTONS = ("first", "prev", "next", "last")

    def __init__(self, parent: wx.Panel, plugin: 'ParquetViewer'):
        """
        Initialize the Pagination Panel

        :param parent: The parent panel
        :type parent: wx.Panel
        :param plugin: The Parquet Viewer plugin
        :type plugin: ParquetViewer
        """
        super().__init__(parent)
        self.logger = plugin.logger.getChild("pagination")
        self.__plugin = plugin
        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.__sizer)

        for name in self.BUTTONS:
            func = getattr(self, name)
            button = PVButton(self, label=name.title(), callback=func, disabled=True)
            setattr(self, f"__{name}_button", button)
            self.__sizer.Add(button, 1, wx.EXPAND)

        self.Show()

    def prev(self, event: wx.Event) -> None:
        """
        Go back one page

        :param event: The event that triggered this callback
        :return: None
        """
        if self.__plugin.OFFSET - self.__plugin.SAMPLE_SIZE < 0:
            self.logger.debug("Cannot go back any further")
            return
        self.__plugin.OFFSET -= self.__plugin.SAMPLE_SIZE
        self.__plugin.load_parquet_data()

    def next(self, event: wx.Event) -> None:
        """
        Go forward one page

        :param event: The event that triggered this callback
        :return: None
        """
        if self.__plugin.OFFSET + self.__plugin.SAMPLE_SIZE >= self.__plugin.get_total_rows():
            self.logger.debug("Cannot go forward any further")
            return
        self.__plugin.OFFSET += self.__plugin.SAMPLE_SIZE
        self.__plugin.load_parquet_data()

    def first(self, event: wx.Event) -> None:
        """
        Go to the first page

        :param event: The event that triggered this callback
        :return: None
        """
        self.__plugin.OFFSET = 0
        self.__plugin.load_parquet_data()

    def last(self, event: wx.Event) -> None:
        """
        Go to the last page

        :param event: The event that triggered this callback
        :return: None
        """
        self.__plugin.OFFSET = self.__plugin.get_total_rows() - self.__plugin.SAMPLE_SIZE
        self.__plugin.load_parquet_data()

    def activate(self):
        """
        Activate all buttons

        :return: None
        """
        for name in self.BUTTONS:
            button = getattr(self, f"__{name}_button")
            button.Enable()