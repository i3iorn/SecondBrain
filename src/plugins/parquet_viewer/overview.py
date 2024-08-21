from typing import TYPE_CHECKING

import wx

if TYPE_CHECKING:
    from src.plugins.parquet_viewer import ParquetViewer


class Overview(wx.Panel):
    """
    The Overview Panel for the Parquet Viewer

    This panel contains an overview of the Parquet file.

    The overview contains:
    - Total Rows
    - Total Columns
    - Column Names

    The overview is read-only and cannot be edited.
    """
    def __init__(self, parent: wx.Panel) -> None:
        """
        Initialize the Overview Panel

        :param parent: The parent panel
        :type parent: wx.Panel
        :return: None
        """
        super().__init__(parent)
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)

        self.__base_info = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.TE_NO_VSCROLL)
        self.__sizer.Add(self.__base_info, 1, wx.EXPAND)

    def update(self, plugin: "ParquetViewer") -> None:
        """
        Update the Overview Panel with the information from the Parquet Viewer

        :param plugin: The Parquet Viewer plugin
        :return: None
        """
        self.__base_info.Clear()
        self.__base_info.AppendText(f"Total Rows: {plugin.get_total_rows()}\n")
        self.__base_info.AppendText(f"Total Columns: {len(plugin.get_relation().columns)}\n")

        for i, column in enumerate(plugin.get_relation().columns):
            self.__base_info.AppendText(f"{i + 1}. {column}\n")

        self.__base_info.AppendText("\n")

        self.Layout()
        self.Refresh()
