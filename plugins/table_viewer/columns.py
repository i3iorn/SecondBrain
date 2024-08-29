from typing import TYPE_CHECKING
from .helpers import status_message
from .components.panel import BasePanel

import wx

if TYPE_CHECKING:
    from plugins.table_viewer import TableViewer


class ColumnOverviewPanel(BasePanel):
    """
    The Overview Panel for the Table Viewer.

    This panel provides an overview of the file, including the total number of rows, total number of columns,
    and the column names.

    The overview is displayed in a read-only text control, and is updated whenever the Table Viewer plugin is
    updated with a new file.

    Attributes:
        __sizer (wx.BoxSizer): The main sizer for the panel, which contains the text control.
        __base_info (wx.TextCtrl): The text control that displays the overview information.
    """

    def __init__(self, tv: "TableViewer") -> None:
        """
        Initialize the Overview Panel.

        Args:
            parent (wx.Panel): The parent panel for the Overview Panel.
        """
        super().__init__(tv.panel)
        self.status_bar = tv.status_bar
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)

        self.__base_info = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.__sizer.Add(self.__base_info, 1, wx.EXPAND)

    @status_message(f"Updating overview")
    def update(self, columns: list) -> None:
        """
        Update the Overview Panel with the information from the Table Viewer.

        This method clears the text control and populates it with the total number of rows, total number of columns,
        and the column names from the Table Viewer plugin.

        Args:
            columns (list): The list of column names from the Table Viewer plugin.
        """
        for i, column in enumerate(columns):
            self.__base_info.AppendText(f"{i + 1}. {column}\n")

        self.__base_info.AppendText("\n")

        self.Layout()
        self.Refresh()
