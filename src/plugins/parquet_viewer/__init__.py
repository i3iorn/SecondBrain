import logging

import wx
import wx.grid

import duckdb
import duckdb.duckdb

from .components import PVButton

from ..base import IPlugin


# Decorator that sets a status bar message when a function is called and clears it when the function completes
def status_message(message):
    def decorator(func):
        def wrapper(*args, **kwargs):
            wx.CallAfter(args[0].status_bar.SetStatusText, message)
            result = func(*args, **kwargs)
            wx.CallAfter(args[0].status_bar.SetStatusText, "Main thread ready")
            return result

        return wrapper

    return decorator


class Overview(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)

        self.__base_info = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.TE_NO_VSCROLL)
        self.__sizer.Add(self.__base_info, 1, wx.EXPAND)

    def update(self, plugin):
        self.__base_info.Clear()
        self.__base_info.AppendText(f"Total Rows: {plugin.get_total_rows()}\n")
        self.__base_info.AppendText(f"Total Columns: {len(plugin.get_relation().columns)}\n")

        for i, column in enumerate(plugin.get_relation().columns):
            self.__base_info.AppendText(f"{i + 1}. {column}\n")

        self.__base_info.AppendText("\n")

        self.Layout()
        self.Refresh()


class Pagination(wx.Panel):
    def __init__(self, parent, plugin):
        super().__init__(parent)
        self.logger = plugin.logger.getChild("Pagination")
        self.__plugin = plugin
        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.__sizer)

        buttons = ("first", "prev", "next", "last")

        for name in buttons:
            func = getattr(self, name)
            button = PVButton(self, label=name.title(), callback=func, disabled=True)
            setattr(self, f"__{name}_button", button)
            self.__sizer.Add(button, 1, wx.EXPAND)

        self.Show()

    def prev(self, event):
        if self.__plugin.OFFSET - self.__plugin.SAMPLE_SIZE < 0:
            self.logger.debug("Cannot go back any further")
            return
        self.__plugin.OFFSET -= self.__plugin.SAMPLE_SIZE
        self.__plugin.load_parquet_data()

    def next(self, event):
        if self.__plugin.OFFSET + self.__plugin.SAMPLE_SIZE >= self.__plugin.get_total_rows():
            self.logger.debug("Cannot go forward any further")
            return
        self.__plugin.OFFSET += self.__plugin.SAMPLE_SIZE
        self.__plugin.load_parquet_data()

    def first(self, event):
        self.__plugin.OFFSET = 0
        self.__plugin.load_parquet_data()

    def last(self, event):
        self.__plugin.OFFSET = self.__plugin.get_total_rows() - self.__plugin.SAMPLE_SIZE
        self.__plugin.load_parquet_data()

    def activate(self):
        self.__first_button.Enable()
        self.__prev_button.Enable()
        self.__next_button.Enable()
        self.__last_button.Enable()


class ParquetViewer(IPlugin):
    SAMPLE_SIZE = 100
    OFFSET = 0
    BASE_SPAN = 10

    def __init__(self):
        self.__data = None
        self.__panel = None
        self.__button = None
        self.__grid = None
        self.__overview = None
        self.__pagination = None
        self.environment = None
        self.total_rows = {}
        self.relation = {}

    @property
    def data(self):
        if hasattr(self, "__data"):
            return self.__data
        return None

    @data.setter
    def data(self, value):
        # TODO: Implement validation
        self.__data = value

    @property
    def name(self):
        return "Parquet Viewer"

    @property
    def plugin_frame(self):
        if hasattr(self, "environment") and self.environment is not None:
            return self.environment["plugin_frame"]
        return None

    @property
    def status_bar(self):
        if hasattr(self, "environment") and self.environment is not None:
            return self.environment["status_bar"]
        return None

    def stop(self):
        self.logger.debug("Stopping Parquet Viewer")
        self.__panel.Destroy()
        return True

    def run(self, environment):
        self.environment = environment
        self.logger = self.environment.logger.getChild(self.name)

        # Create a panel for the plugin with the plugin frame as the parent
        self.__panel = wx.Panel(self.plugin_frame)

        # Divide the panel into a grid, 3 x 2. Each row takes up 100% of the width
        self.__panel_sizer = wx.FlexGridSizer(3, 2, self.BASE_SPAN, self.BASE_SPAN)
        self.__panel_sizer.AddGrowableCol(0)
        self.__panel_sizer.AddGrowableCol(1)
        self.__panel_sizer.AddGrowableRow(1)

        # Add a button to the first row, first column with the label "Load Parquet File".
        # Bind the button to the load_parquet_file method
        self.__button = PVButton(self.__panel, label="Load Parquet File", callback=self.load_parquet_file)
        self.__panel_sizer.Add(self.__button, 1, wx.EXPAND)

        overview_label = wx.StaticText(self.__panel, label="Overview")
        overview_label.SetForegroundColour(wx.Colour(240, 250, 255))
        overview_label.SetExtraStyle(wx.BOLD)
        self.__panel_sizer.Add(overview_label, 1, wx.ALIGN_CENTER)

        # Add a grid to the second row, first column that will display the parquet data
        self.__grid = wx.grid.Grid(self.__panel)

        self.__grid.SetMaxSize((self.plugin_frame.GetSize()[0] - self.plugin_frame.GetSize()[0] // 4, self.plugin_frame.GetSize()[1] // 2))
        self.__panel_sizer.Add(self.__grid, 1, wx.EXPAND)

        # Add an overview of the parquet data to the second row, second column
        self.__overview = Overview(self.__panel)
        self.__panel_sizer.Add(self.__overview, 1, wx.EXPAND)

        # Add pagination buttons to the third row, first column
        self.__pagination = Pagination(self.__panel, self)
        self.__panel_sizer.Add(self.__pagination, 1, wx.EXPAND)

        # Add a filter to the third row, second column
        self.__panel_sizer.Add(wx.StaticText(self.__panel, label=""), 1, wx.EXPAND)

        self.__main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__main_sizer.Add(self.__panel_sizer, 1, wx.EXPAND | wx.ALL, self.BASE_SPAN)

        # Set the sizer for the panel
        self.__panel.SetSizer(self.__main_sizer)

        # Set the size of the panel
        self.__panel.SetSize(self.plugin_frame.GetSize())

        # Show the panel
        self.__panel.Show()

        sizing_events = [wx.EVT_SIZE, wx.EVT_MAXIMIZE, wx.EVT_ICONIZE, wx.EVT_CLOSE, wx.EVT_MOVE, wx.EVT_SIZING]

        for event in sizing_events:
            self.plugin_frame.Bind(event, self.on_size)

        return True

    @status_message("Begin loading parquet file")
    def load_parquet_file(self, event):
        # Create a file dialog to select a parquet file
        file_dialog = wx.FileDialog(self.__panel, "Open Parquet File", wildcard="Parquet files (*.parquet)|*.parquet",
                                    style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        # If the user selects a file
        if file_dialog.ShowModal() == wx.ID_OK:
            self.logger.debug("Loading Parquet File")

            # Get the path to the file
            self.path = file_dialog.GetPath()
            self.logger.debug(f"Path: {self.path}")

            columns = duckdb.sql(f"SELECT * FROM '{self.path}' LIMIT 1").columns
            if len(columns) == 0:
                self.logger.error("No columns found in parquet file")
                return False

            self.__grid.CreateGrid(self.SAMPLE_SIZE, len(columns))

            self.__pagination.activate()
            # Load the parquet file
            self.load_parquet_data()
            self.__overview.update(self)

        return True

    @status_message("Setting up file relation")
    def get_relation(self):
        self.logger.debug(f"Loading {self.SAMPLE_SIZE} rows from{self.path} with an offset of '{self.OFFSET}'")

        key = f"{self.path}_{self.SAMPLE_SIZE}_{self.OFFSET}"
        if key not in self.relation:
            self.relation[key] = duckdb.sql(f"SELECT * FROM '{self.path}' LIMIT {self.SAMPLE_SIZE} OFFSET {self.OFFSET}")

        return self.relation[key]

    @status_message("Getting total rows")
    def get_total_rows(self) -> int:
        # Get the total number of rows in the parquet file
        if self.path not in self.total_rows:
            self.total_rows[self.path] = duckdb.sql(f"SELECT COUNT(*) FROM '{self.path}'").fetchone()[0]
        return self.total_rows[self.path]

    @status_message("Loading Parquet Data")
    def load_parquet_data(self):
        # Get the columns from the parquet file
        columns = self.get_relation().columns
        self.logger.debug(f"Columns: {columns}")

        data = self.get_relation().fetchall()

        self.logger.debug(f"Settings up grid table with data")
        # Create a grid

        # Set the column labels
        for i, column in enumerate(columns):
            self.__grid.SetColLabelValue(i, column)

        # Set the data in the grid
        for i, row in enumerate(data):
            # Set the row label
            self.__grid.SetRowLabelValue(i, str(self.OFFSET + i + 1))
            for j, value in enumerate(row):
                self.__grid.SetCellValue(i, j, str(value))

        # Emit size event
        self.on_size(wx.SizeEvent((0, 0)))

        self.logger.debug(f"Parquet file loaded")

        return True

    def on_size(self, event):
        """Adjust the size of the panel to fit the plugin frame and redraw all components"""
        self.logger.trace("Resizing panel")
        self.__main_sizer.Layout()
        self.__panel.SetSize(self.plugin_frame.GetSize())
        self.__panel.Layout()
        self.__panel.Refresh()

        event.Skip()
        return True
