import threading
from typing import TYPE_CHECKING

import duckdb
import wx
import wx.grid

from .components.panel import BasePanel
from .helpers import status_message

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
        self.plugin = tv
        self.status_bar = tv.status_bar
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)
        self.SetMaxSize(tv.panel.GetSize())

        self.setup_ui()

        self.Show()

    def setup_ui(self):
        """
        Set up the UI for the Column Overview Panel.
        Returns:
            bool: True if the UI was successfully set up, False otherwise.
        """
        self.info_grid = wx.grid.Grid(self)
        self.info_grid.CreateGrid(0, 3)

        self.info_grid.SetColLabelValue(0, "Column Name")
        self.info_grid.SetColLabelValue(1, "Coverage")
        self.info_grid.SetColLabelValue(2, "Unique Values")

        self.__sizer.Add(self.info_grid, 1, wx.EXPAND)

        return True

    def update(self):
        update_thread = threading.Thread(target=self.update_thread)
        update_thread.start()

    @status_message("Updating column overview", 1)
    def update_thread(self) -> bool:
        """
        Update the overview information in the text control.
        """
        self.info_grid.ClearGrid()

        if self.info_grid.GetNumberRows() > 0:
            self.info_grid.DeleteRows(0, self.info_grid.GetNumberRows())

        if self.plugin.grid.df is None:
            return False
        df = self.plugin.grid.df

        total_rows = len(df)
        if total_rows >= 10000000:
            wx.MessageBox("The file is too large to display all unique values. 10 million rows will be used as a sample.", "Warning", wx.OK | wx.ICON_WARNING)
            rows_to_check = 10000000
        else:
            rows_to_check = total_rows

        for i, column in enumerate(df.columns):
            while True:
                try:
                    column_values = [value[0] for value in df[column].limit(rows_to_check).fetchall() if value[0] is not None]
                    break
                except duckdb.InvalidInputException:
                    continue

            self.info_grid.AppendRows(1)
            self.info_grid.SetCellValue(i, 0, column)
            self.info_grid.SetCellValue(i, 1, f"{len(column_values) / rows_to_check:.2%}" if column_values is not None else "N/A")

            if len(set(column_values)) == rows_to_check:
                self.info_grid.SetCellValue(i, 2, "Unique")
            elif len(column_values) == 0:
                self.info_grid.SetCellValue(i, 2, "N/A")
            else:
                self.info_grid.SetCellValue(i, 2, f"{len(set(column_values)) / rows_to_check:.2%}")

        self.info_grid.AutoSize()
        self.GetTopLevelParent().Layout()

        return True

    def on_label_click(self, event):
        label = event.GetRow()
        print(label)
        column = self.info_grid.GetCellValue(label, 0)
        coverage = self.info_grid.GetCellValue(label, 1)
        unique = self.info_grid.GetCellValue(label, 2)

        self.status_bar.SetStatusText(f"Column: {column}, Coverage: {coverage}, Unique Values: {unique}", 1)
        event.Skip()
