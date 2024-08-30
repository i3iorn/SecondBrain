import wx
import wx.grid

from .components.panel import BasePanel


class GridPanel(BasePanel):
    def __init__(self, tv: "TableViewer") -> None:
        super().__init__(tv.panel)
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)

        self.__grid = wx.grid.Grid(self)
        self.__sizer.Add(self.__grid, 1, wx.EXPAND)

        self.SetMaxSize((tv.panel.GetSize()[0], tv.panel.GetSize()[1] // 2))

        self.__grid.AutoSizeColumns()
        self.__grid.AutoSizeRows()
        self.GetTopLevelParent().Layout()

    def AutoSizeColumns(self):
        self.__grid.AutoSizeColumns()

    def AutoSizeRows(self):
        self.__grid.AutoSizeRows()

    def ClearGrid(self):
        self.__grid.ClearGrid()

    def DeleteRows(self, pos, numRows=1):
        self.__grid.DeleteRows(pos, numRows)

    def SetCellValue(self, row, col, value):
        self.__grid.SetCellValue(row, col, value)

    def SetColLabelValue(self, col, value):
        self.__grid.SetColLabelValue(col, value)

    def SetRowLabelValue(self, row, value):
        self.__grid.SetRowLabelValue(row, value)

    def SetTable(self, table, *args, **kwargs):
        self.__grid.SetTable(table, *args, **kwargs)
        self.__grid.AutoSizeColumns()
        self.__grid.AutoSizeRows()
        self.GetTopLevelParent().Layout()
