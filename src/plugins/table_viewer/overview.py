from typing import TYPE_CHECKING

import wx

if TYPE_CHECKING:
    from src.plugins.table_viewer import TableViewer


class Overview(wx.Panel):
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
    def __init__(self, parent: wx.Panel) -> None:
        """
        Initialize the Overview Panel.

        Args:
            parent (wx.Panel): The parent panel for the Overview Panel.
        """
        super().__init__(parent)
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)

        self.__base_info = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.__sizer.Add(self.__base_info, 1, wx.EXPAND)

    def update(self, plugin: "TableViewer", append: bool = False) -> None:
        """
        Update the Overview Panel with the information from the Table Viewer.

        This method clears the text control and populates it with the total number of rows, total number of columns,
        and the column names from the Table Viewer plugin.

        Args:
            plugin (TableViewer): The Table Viewer plugin.
            append (bool): Set to true if you want to append instead of replace the content.
        """
        if not append:
            self.__base_info.Clear()

        self.__base_info.AppendText(f"Total Rows: {self.human_readable_rows(plugin.get_total_rows())}\n")
        self.__base_info.AppendText(f"Total Columns: {len(plugin.get_relation().columns)}\n")


        self.__base_info.AppendText("\nColumn names\n========================================================\n")
        for i, column in enumerate(plugin.get_relation().columns):
            self.__base_info.AppendText(f"{i + 1}. {column}\n")

        self.__base_info.AppendText("\n")

        self.Layout()
        self.Refresh()

    @staticmethod
    def human_readable_rows(rows: int) -> str:
        """
        Convert the number of rows to a human-readable format.

        This method takes an integer representing the number of rows and converts it to a human-readable string,
        using appropriate units (e.g., thousands, millions, billions).

        Args:
            rows (int): The number of rows.

        Returns:
            str: The human-readable number of rows.
        """
        if rows < 1_000:
            return f"{rows:,}".replace(",", " ")
        elif rows < 1000000:
            return f"{rows / 1000:.1f}K".replace(".0", "")
        elif rows < 1000000_000:
            return f"{rows / 1000000:.1f}M".replace(".0", "")
        else:
            return f"{rows / 1000000000:.1f}B".replace(".0", "")
