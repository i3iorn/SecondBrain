import duckdb
import wx
import wx._core
import wx.grid

from . import BasePanel
from .helpers import status_message
from .pagination import Pagination


class GridPanel(BasePanel):
    def __init__(self, tv: "TableViewer") -> None:
        super().__init__(tv.panel)
        self.SetSizer(wx.FlexGridSizer(2, 1, 10, 10))
        self.GetSizer().AddGrowableRow(0)
        self.GetSizer().AddGrowableCol(0)
        self.SetMaxSize(tv.panel.GetSize())

        self.__row_count = {}
        self.__plugin = tv
        self.logger = tv.logger.getChild("grid")
        self.__df = None
        self.__offset = 0
        self.__setup_ui()

    @property
    def row_count(self) -> int:
        if self.__plugin.path not in self.__row_count:
            self.__row_count[self.__plugin.path] = duckdb.sql(f"SELECT COUNT(*) FROM '{self.__plugin.path}'").fetchone()[0]
        return self.__row_count[self.__plugin.path]

    @property
    def df(self):
        if self.__df is None:
            self.__df = self.get_all_rows()
        return self.__df

    @df.setter
    def df(self, value):
        self.__df = value

    @property
    def offset(self) -> int:
        return self.__offset

    @offset.setter
    def offset(self, value: int) -> None:
        self.__offset = value

    @property
    def sample_size(self) -> int:
        return self.__plugin.sample_size

    @sample_size.setter
    def sample_size(self, value: int) -> None:
        self.__plugin.sample_size = value

    @property
    def status_bar(self) -> wx.StatusBar:
        return self.__plugin.status_bar

    def __setup_ui(self):
        self.__setup_grid()
        self.__setup_pagination()

        self.Layout()
        return True

    def __setup_grid(self):
        self.__grid = wx.grid.Grid(self)
        self.__grid.CreateGrid(0, 0)
        self.GetSizer().Add(self.__grid, 1, wx.EXPAND)
        self.__grid.SetMaxSize(self.__plugin.panel.GetSize())

    def __setup_pagination(self):
        self.__pagination = Pagination(self)
        self.GetSizer().Add(self.__pagination, 1, wx.EXPAND)

    @status_message("Get all data from file")
    def get_all_rows(self) -> duckdb.DuckDBPyRelation:
        return duckdb.sql(f"SELECT * FROM '{self.__plugin.path}'")

    @status_message("Loading data into grid")
    def show_data(self, df: duckdb.DuckDBPyRelation=None, offset: int = None, limit: int = None) -> bool:
        offset = offset or self.offset
        limit = limit or self.sample_size
        if df is None:
            df = self.df

        df = df.limit(limit, offset=offset)

        self.__grid.ClearGrid()

        if self.__grid.GetNumberCols() > 0:
            self.__grid.DeleteCols(0, self.__grid.GetNumberCols())
            self.__grid.DeleteRows(0, self.__grid.GetNumberRows())

        self.__grid.AppendCols(len(df.columns))
        self.__grid.AppendRows(len(df))

        for i, col in enumerate(df.columns):
            self.__grid.SetColLabelValue(i, col)

        for i, row in enumerate(df.fetchall()):
            self.__grid.SetRowLabelValue(i, str(i + 1 + self.offset))
            for j, value in enumerate(row):
                value = str(value) if value is not None else ""
                self.__grid.SetCellValue(i, j, str(value))

        self.__pagination.activate()
        self.__grid.AutoSize()
        self.__grid.Refresh()
        self.__grid.Update()
        self.__plugin.panel.Layout()
        return True
