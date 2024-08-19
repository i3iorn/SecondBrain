import logging
import threading
from pathlib import Path

import wx
import wx.grid

import duckdb
import duckdb.duckdb

from .base import IPlugin


BATCH_SIZE = 50
OFFSET = 0


class ParquetViewer(IPlugin):

    @property
    def data(self):
        if hasattr(self, "_data"):
            return self._data
        return None

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def name(self):
        return "Parquet Viewer"

    def run(self, event, environment):
        self.environment = environment
        self.logger = logging.getLogger(self.name)
        self.plugin_frame = environment.get("plugin_frame")
        self.plugin_sizer = self.plugin_frame.GetSizer()

        self.__setup_ui()

    def __setup_ui(self):
        # Clear the plugin frame
        for child in self.plugin_frame.GetChildren():
            child.Destroy()

        self.__setup_layout()

        self.plugin_frame.Layout()
        self.plugin_frame.Fit()
        return True

    def __setup_layout(self):
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.plugin_sizer.Add(self.main_sizer, 1, wx.EXPAND)

        self.main_sizer.AddSpacer(10)
        self.__create_pickerframe()
        self.main_sizer.AddSpacer(10)
        self.__create_main_view_frame()
        self.main_sizer.AddSpacer(10)
        self.__create_buttonframe()
        self.main_sizer.AddSpacer(10)

    def __create_pickerframe(self):
        self.picker_frame = wx.Panel(self.plugin_frame)
        self.picker_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.picker_frame.SetSizer(self.picker_sizer)
        self.main_sizer.Add(self.picker_frame, 0, wx.EXPAND)

        self.file_picker = wx.FilePickerCtrl(self.picker_frame, message="Select a Parquet file", wildcard="Parquet files (*.parquet)|*.parquet")
        self.file_picker.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnFilePick)
        self.picker_sizer.Add(self.file_picker, 1, wx.EXPAND)

    def __create_main_view_frame(self):
        self.main_view_frame = wx.Panel(self.plugin_frame)
        self.main_view_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_view_frame.SetSizer(self.main_view_sizer)
        self.main_sizer.Add(self.main_view_frame, 1, wx.EXPAND)

        self.__create_gridframe()
        self.__overview_frame()

    def __overview_frame(self):
        """
        Create a panel that shows an overview of the data. For each row there is some information about the data.
        """
        self.overview_frame = wx.Panel(self.main_view_frame)
        self.overview_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.overview_frame.SetSizer(self.overview_sizer)
        self.main_view_sizer.Add(self.overview_frame, 0, wx.EXPAND)

        gutter_sizer = wx.BoxSizer(wx.VERTICAL)
        self.overview_sizer.AddSpacer(10)
        self.overview_sizer.Add(gutter_sizer, 0, wx.EXPAND)
        self.overview_sizer.AddSpacer(10)

        data_points = [
            ("rows", "0", ""),
            ("columns", "0", ""),
            ("size", "0", "bytes"),
        ]

        self.data_points = {}

        for label, value, suffix in data_points:
            attr_panel = wx.Panel(self.overview_frame)
            attr_sizer = wx.BoxSizer(wx.HORIZONTAL)
            attr_panel.SetSizer(attr_sizer)
            gutter_sizer.Add(attr_panel, 0, wx.EXPAND)

            label_text = wx.StaticText(attr_panel, label=label.title())
            attr_sizer.Add(label_text, 1, wx.EXPAND)

            attr_sizer.AddStretchSpacer()

            value_text = wx.StaticText(attr_panel, label=value)
            attr_sizer.Add(value_text, 1, wx.EXPAND)

            attr_sizer.AddSpacer(5)

            suffix_text = wx.StaticText(attr_panel, label=suffix)
            attr_sizer.Add(suffix_text, 1, wx.EXPAND)

            self.data_points[label] = value_text

    def __create_gridframe(self):
        self.grid_frame = wx.Panel(self.main_view_frame)
        self.grid_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.grid_frame.SetSizer(self.grid_sizer)
        self.main_view_sizer.Add(self.grid_frame, 1, wx.EXPAND)

        self.data_grid = wx.grid.Grid(self.grid_frame)
        self.data_grid.CreateGrid(0, 0)
        self.grid_sizer.Add(self.data_grid, 1, wx.EXPAND)

    def __create_buttonframe(self):
        self.button_frame = wx.Panel(self.plugin_frame)
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_frame.SetSizer(self.button_sizer)
        self.main_sizer.Add(self.button_frame, 0, wx.EXPAND)
        self.button_sizer.AddSpacer(5)

        self.prev_button = wx.Button(self.button_frame, label="Previous")
        self.prev_button.Bind(wx.EVT_BUTTON, self.OnPrev)
        self.button_sizer.Add(self.prev_button, 0, wx.EXPAND)
        self.button_sizer.AddSpacer(5)

        self.go_to_text = wx.TextCtrl(self.button_frame, style=wx.TE_PROCESS_ENTER)
        self.go_to_text.Bind(wx.EVT_TEXT_ENTER, self.OnGoTo)
        self.go_to_text.SetValue("1")
        self.button_sizer.Add(self.go_to_text, 0, wx.EXPAND)
        self.go_to_text.SetMinSize((50, -1))
        self.button_sizer.AddSpacer(5)

        self.go_to_button = wx.Button(self.button_frame, label="Go to")
        self.go_to_button.Bind(wx.EVT_BUTTON, self.OnGoTo)
        self.button_sizer.Add(self.go_to_button, 0, wx.EXPAND)
        self.button_sizer.AddSpacer(5)

        self.next_button = wx.Button(self.button_frame, label="Next")
        self.next_button.Bind(wx.EVT_BUTTON, self.OnNext)
        self.button_sizer.Add(self.next_button, 0, wx.EXPAND)
        self.button_sizer.AddSpacer(5)

    def OnFilePick(self, event):
        # Store the file path
        self.file_path = self.file_picker.GetPath()
        self.file_rows = duckdb.sql(f"SELECT count(*) FROM '{self.file_path}'").fetchone()
        self.data_points["rows"].SetLabel(str(self.file_rows[0]))
        self.data_points["size"].SetLabel(str(Path(self.file_path).stat().st_size))
        self.__load_data()
        return True

    def __load_data(self):
        self.logger.info("Loading data from Parquet file")
        self.data = duckdb.sql(f"SELECT * FROM '{self.file_path}' LIMIT {BATCH_SIZE} OFFSET {OFFSET}")
        self.logger.debug(f"Loaded {len(self.data)} rows of data")

        # Clear the grid
        self.data_grid.ClearGrid()

        # If the grid is empty, add columns
        if self.data_grid.GetNumberCols() == 0:
            self.data_grid.AppendCols(len(self.data.columns))
            self.data_grid.AppendRows(len(self.data))
            self.data_points["columns"].SetLabel(f"{len(self.data.columns)}")

        for i, row in enumerate(self.data.fetchall()):
            self.data_grid.SetRowLabelValue(i, str(i + OFFSET))
            for j, value in enumerate(row):
                if i == 0:
                    self.data_grid.SetColLabelValue(j, f"{self.data.columns[j]}")
                self.data_grid.SetCellValue(i, j, str(value))

        self.logger.info("Data loaded successfully")

        # Resize the columns and rows
        self.data_grid.AutoSizeColumns()
        self.data_grid.AutoSizeRows()

        # Refresh the plugin frame
        self.plugin_frame.Refresh()

        # Update the page label
        self.go_to_text.SetValue(str(OFFSET // BATCH_SIZE))

        # Calculate column coverage asynchronously
        self.update_thread = threading.Thread(target=self.update_grid_labels)
        self.update_thread.start()

        return True

    def update_grid_labels(self):
        for col in range(self.data_grid.GetNumberCols()):
            try:
                coverage = self.data.filter(f"[{self.data.columns[col]}] is not null").count(self.data.columns[col]).fetchone()[0] / self.data.count("*").fetchone()[0]
            except duckdb.duckdb.BinderException:
                coverage = 0
            wx.CallAfter(self.data_grid.SetColLabelValue, col, f"{self.data.columns[col]} ({coverage:.2%})")
            self.environment['status_bar'].SetStatusText(f"Calculating column coverage {col}/{self.data_grid.GetNumberCols()}", 1)

        self.environment['status_bar'].SetStatusText("Ready", 1)

    def OnPrev(self, event):
        global OFFSET
        OFFSET -= BATCH_SIZE
        self.__load_data()
        return True

    def OnNext(self, event):
        global OFFSET
        OFFSET += BATCH_SIZE
        self.__load_data()
        return True

    def OnGoTo(self, event):
        global OFFSET
        OFFSET = int(self.go_to_text.GetValue()) * BATCH_SIZE
        self.__load_data()
        return True
