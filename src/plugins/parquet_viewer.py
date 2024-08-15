import wx
import wx.grid

import duckdb

from .base import IPlugin


class Welcome(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        text = wx.StaticText(self, label="Welcome to the Parquet Viewer!")
        sizer.Add(text, 0, wx.ALL, 5)

        button = wx.Button(self, label="Open file")
        button.Bind(wx.EVT_BUTTON, self.on_open_file)
        sizer.Add(button, 0, wx.ALL, 5)

        self.Layout()
        self.Fit()

    def on_open_file(self, event):
        dialog = wx.FileDialog(self, "Open Parquet file", wildcard="Parquet files (*.parquet)|*.parquet", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_CANCEL:
            return
        path = dialog.GetPath()
        dialog.Destroy()

        self.show_parquet_file(path)

    def show_parquet_file(self, path):
        the_grid = wx.grid.Grid(self)
        duckdb.read_parquet(path)
        the_grid.CreateGrid(0, 0, wx.grid.Grid.SelectRows)
        the_grid.AppendCols(len(duckdb.sql(f"SELECT * FROM read_parquet('{path}') LIMIT 1").columns))
        for i, column in enumerate(duckdb.sql(f"SELECT * FROM read_parquet('{path}') LIMIT 1").columns):
            the_grid.SetColLabelValue(i, column)

        batch_size = 100
        for batch in range(0, 100000000, batch_size):
            rel = duckdb.sql(f"SELECT * FROM read_parquet('{path}') LIMIT {batch_size} OFFSET {batch}")
            data = rel.fetchall()
            count = len(data)
            if count == 0:
                break

            the_grid.AppendRows(count)
            for i, row in enumerate(data):
                for j, value in enumerate(row):
                    the_grid.SetCellValue(i + batch, j, str(value))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(the_grid, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()
        self.Fit()

        return True

class ParquetViewer(IPlugin):
    @property
    def name(self):
        return "Parquet Viewer"

    def run(self, event, environment):
        frame = environment['plugin_frame']

        p_sizer = wx.BoxSizer(wx.VERTICAL)
        frame.SetSizer(p_sizer)

        panel = Welcome(frame)
        p_sizer.Add(panel, 1, wx.EXPAND)

        frame.Layout()
        frame.Fit()
        frame.Show()

        return True
