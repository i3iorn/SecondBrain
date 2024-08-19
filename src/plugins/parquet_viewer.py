import logging

import wx
import wx.grid

import duckdb

from .base import IPlugin


BATCH_SIZE = 100
OFFSET = 0


class ParquetViewer(IPlugin):
    @property
    def name(self):
        return "Parquet Viewer"

    def run(self, event, environment):
        self.environment = environment
        self.logger = logging.getLogger(self.name)
        self.plugin_frame = environment.get("plugin_frame")
        self.plugin_sizer = self.plugin_frame.GetSizer()

        self.logger.debug("Running Parquet Viewer plugin")

        self.__setup_ui()

    def __setup_ui(self):
        # Create a new panel to display message and filepicker
        panel = wx.Panel(self.plugin_frame)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.plugin_sizer.Add(panel, 1, wx.EXPAND)

        # Create a new sizer for the panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)

        # Create a new message
        message = wx.StaticText(panel, label="Select a Parquet file to view")
        sizer.Add(message, 0, wx.ALL, 5)

        # Create a new file picker
        file_picker = wx.FilePickerCtrl(panel, message="Select a Parquet file", wildcard="*.parquet")
        sizer.Add(file_picker, 0, wx.ALL, 5)

        # Create a new button
        button = wx.Button(panel, label="Load Data")
        sizer.Add(button, 0, wx.ALL, 5)

        # Bind the button to the load data function
        button.Bind(wx.EVT_BUTTON, lambda event: self.__load_data(file_picker.GetPath()))

        # Refresh the plugin frame
        self.plugin_frame.Layout()
        self.plugin_frame.Fit()
        self.plugin_frame.Refresh()

    def __load_data(self, file_path):
        self.logger.debug("Loading data")

        column_names = duckdb.sql(f"SELECT * FROM '{file_path}' LIMIT 1").columns
        data = duckdb.sql(f"SELECT * FROM '{file_path}' LIMIT {BATCH_SIZE} OFFSET {OFFSET}").fetchall()

        grid = wx.grid.Grid(self.plugin_frame)
        grid.CreateGrid(len(data), len(column_names))

        for i, row in enumerate(data):
            for j, value in enumerate(row):
                grid.SetCellValue(i, j, str(value))

        for i, column_name in enumerate(column_names):
            grid.SetColLabelValue(i, column_name)

        self.plugin_sizer.Add(grid, 1, wx.EXPAND)
        self.plugin_frame.Layout()
        self.plugin_frame.Fit()
        self.plugin_frame.Refresh()
        self.logger.debug("Data loaded")
