import logging
import os
from pathlib import Path

import duckdb
import wx
import wx.grid

from .columns import ColumnOverviewPanel
from .components import PVButton
from .components.panel import BasePanel
from .grid import GridPanel
from .helpers import status_message
from .load_file import LoadFilePanel
from .overview import OverviewPanel
from .pagination import Pagination


class TableViewer:
    """
    The Table Viewer Plugin

    This plugin allows the user to view the contents of a tabular file. The plugin allows the user to load a file
    and view the data in a grid. The plugin also provides an overview of the file, including the total number of
    rows, the total number of columns, and the column names.

    The plugin also provides pagination to allow the user to navigate through the data in the file.

    The plugin uses DuckDB to read the Parquet, JSON, and CSV files and display the data in a grid.

    The plugin provides the following functionality:
    - Load File: Load a file to view the data
    - Overview: View an overview of the file
    - Grid: View the data in a grid
    - Pagination: Navigate through the data in the file

    # Limitations
    - The plugin only supports Parquet, CSV, and JSON files
    - The plugin only supports reading data from the file
    - The plugin only supports viewing the data in a grid
    - The plugin only supports navigating through the data in the file with pagination

    # Future Improvements
    - Add support for other file formats
    - Add support for editing data in the grid
    - Add support for filtering data in the grid
    - Add support for sorting data in the grid
    - Add support for searching data in the grid
    - Add support for exporting data from the grid

    # Known Issues
    - The grid may not resize correctly when the plugin frame is resized. Reloading the plugin will fix this issue.

    # Dependencies
    - DuckDB: To read the file and display the data in a grid
    - wxPython: To create the user interface
    """
    BASE_SPAN = 10

    def __init__(self):
        """
        Initialize the Table Viewer Plugin
        """
        self.logger = logging.getLogger("table_viewer")
        self.panel = None
        self.__button = None
        self.grid = None
        self.overview = None
        self.pagination = None
        self.environment = None
        self.total_rows = {}
        self.relation = {}
        self.df = None
        self.offset = 0
        self.sample_size = 1000

    @property
    def name(self) -> str:
        """
        Get the name of the plugin.

        Returns:
            str: The name of the plugin.
        """
        return "Table Viewer"

    @property
    def plugin_frame(self) -> wx.Frame:
        """
        Get the plugin frame.

        Returns:
            wx.Frame: The plugin frame.
        """
        return self.environment.get("plugin_frame") if self.environment else None

    @property
    def status_bar(self) -> wx.StatusBar:
        """
        Get the status bar.

        Returns:
            wx.StatusBar: The status bar.
        """
        return self.environment.get("status_bar") if self.environment else None

    def stop(self) -> bool:
        """
        Stop the Table Viewer.

        This method is called when the plugin needs to be stopped. It destroys the panel associated with the plugin,
        effectively stopping the plugin.

        Returns:
            bool: True if the plugin was stopped successfully.
        """
        self.logger.debug("Stopping Table Viewer")
        if self.panel:
            self.panel.Destroy()
        return True

    def run(self, environment) -> bool:
        """
        Run the Table Viewer.

        This method is called to start the plugin. It initializes the user interface, binds the necessary events.

        Args:
            environment (Environment): The environment to run the plugin in.
        """
        self.logger.debug("Running Table Viewer")
        self.environment = environment
        wx.CallAfter(self.__initialize_ui)
        wx.CallAfter(self.__bind_events)
        return True

    def __initialize_ui(self) -> None:
        """
        Initialize the user interface.

        This method sets up the panel, sizers, and various UI elements for the plugin, including the load file button,
        overview label, grid, overview, pagination, and a spacer.
        """
        self.panel = wx.Panel(self.plugin_frame)
        self.panel_sizer = wx.FlexGridSizer(3, 2, self.BASE_SPAN, self.BASE_SPAN)
        self.panel_sizer.AddGrowableCol(0, 3)
        self.panel_sizer.AddGrowableCol(1, 1)
        self.panel_sizer.AddGrowableRow(1, 4)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.panel_sizer, 1, wx.EXPAND | wx.ALL, self.BASE_SPAN)
        self.panel.SetSizer(self.main_sizer)

        self.overview = OverviewPanel(self)
        self.panel_sizer.Add(wx.StaticText(self.panel, label=""), 1, wx.EXPAND)
        self.grid = GridPanel(self)
        self.column_overview = ColumnOverviewPanel(self)
        self.pagination = Pagination(self)
        self.load_file_button = LoadFilePanel(self)

        self.panel.SetSize(self.plugin_frame.GetSize())
        self.panel.Show()

    def __bind_events(self) -> None:
        """
        Bind the resizing events to the plugin frame to ensure the panel resizes correctly.

        This method binds various resize-related events to the plugin frame, such as wx.EVT_SIZE, wx.EVT_MAXIMIZE,
        wx.EVT_ICONIZE, wx.EVT_CLOSE, wx.EVT_MOVE, and wx.EVT_SIZING. When these events are triggered, the on_size
        method is called to resize the panel accordingly.
        """
        for event in [wx.EVT_SIZE, wx.EVT_MAXIMIZE, wx.EVT_ICONIZE, wx.EVT_CLOSE, wx.EVT_MOVE, wx.EVT_SIZING]:
            self.plugin_frame.Bind(event, self.on_size)

    @status_message("Begin loading file")
    def load_file(self, event: wx.CommandEvent) -> bool:
        """
        Load a file.

        This method opens a file dialog to allow the user to select a file to load. Supported file types include Parquet,
        CSV, and JSON. Once a file is selected, the method sets up the grid, activates the pagination, loads the data,
        and updates the overview.

        Args:
            event (wx.CommandEvent): The event that triggered the file loading.

        Returns:
            bool: True if the file was loaded successfully.
        """
        file_dialog = wx.FileDialog(
            self.panel, "Open File",
            wildcard="Parquet files (*.parquet)|*.parquet|CSV files (*.csv)|*.csv|JSON files (*.json)|*.json|All files|*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )

        if not Path(file_dialog.GetPath()).exists():
            self.logger.error("File does not exist")
            return False

        if file_dialog.ShowModal() == wx.ID_OK:
            self.logger.debug("Loading File")
            self.path = file_dialog.GetPath()
            self.logger.debug(f"Path: {self.path}")

            columns = duckdb.sql(f"SELECT * FROM '{self.path}' LIMIT 1").columns

            if not columns:
                self.logger.error("No columns found in file")
                return False

            table = wx.grid.GridStringTable(self.sample_size, len(columns))
            self.grid.SetTable(table, True)

            self.pagination.activate()
            self.load_data()
            self.overview.update(total_rows=self.get_total_rows(True), columns=columns)

        return True

    @status_message("Setting up file relation")
    def get_relation(self) -> "duckdb.DuckDBPyRelation":
        """
        Get the duckdb relation of the file.

        This method retrieves the duckdb relation for the current file, using the file path, sample size, and offset as
        a key to cache the relation. If the relation is not yet cached, it is created and stored in the cache.

        Returns:
            duckdb.DuckDBPyRelation: The relation of the file.
        """
        key = f"{self.path}_{self.sample_size}_{self.offset}"
        if key not in self.relation:
            self.relation[key] = duckdb.sql(
                f"SELECT * FROM '{self.path}' LIMIT {self.sample_size} OFFSET {self.offset}")
        return self.relation[key]

    @status_message("Getting total size")
    def get_size(self) -> str:
        """
        Get the size of the file.

        This method retrieves the size of the file, using the file path as a key to cache the result. If the size is not
        yet cached, it is calculated and stored in the cache.

        Returns:
            int: The size of the file.
        """
        size = os.path.getsize(self.path)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 ** 2:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 ** 3:
            return f"{size / 1024 ** 2:.2f} MB"
        else:
            return f"{size / 1024 ** 3:.2f} GB"

    @status_message("Getting total rows")
    def get_total_rows(self, file_count: bool = False) -> int:
        """
        Get the total number of rows in the file.

        This method retrieves the total number of rows in the file, using the file path as a key to cache the result.
        If the total number of rows is not yet cached, it is calculated and stored in the cache.

        Returns:
            int: The total number of rows in the file.
        """
        if self.df is not None and not file_count:
            return self.df.count("*").fetchone()[0]

        if self.path not in self.total_rows:
            self.total_rows[self.path] = duckdb.sql(f"SELECT COUNT(*) FROM '{self.path}'").fetchone()[0]

        return self.total_rows[self.path]

    @status_message("Loading Data: ?")
    def load_data(self, df: duckdb.DuckDBPyRelation = None) -> bool:
        """
        Load the data into the grid.

        This method retrieves the data from the duckdb relation, sets the column labels in the grid, and populates the
        grid with the data. It also resizes the grid to fit the panel.

        Arguments:
            df (duckdb.DuckDBPyRelation): The duckdb relation to load the data from.

        Returns:
            bool: True if the data was loaded successfully.
        """
        if df is None:
            df = self.df or self.get_relation()

        self.logger.debug(f"Loading data")
        data = df.fetchall()
        columns = df.columns

        self.grid.ClearGrid()

        for i, column in enumerate(columns):
            self.grid.SetColLabelValue(i, column)

        for i, row in enumerate(data):
            self.grid.SetRowLabelValue(i, str(self.offset + i + 1))
            for j, value in enumerate(row):
                self.grid.SetCellValue(i, j, str(value))

            self.status_bar.SetStatusText(f"Loading Data: {i}")

        # Remove extra rows
        if len(data) < self.sample_size:
            self.grid.DeleteRows(len(data), self.sample_size - len(data))

        self.df = df

        self.grid.AutoSizeColumns()
        self.grid.AutoSizeRows()

        self.on_size(wx.SizeEvent((0, 0)))
        self.logger.debug(f"File loaded")
        return True

    @status_message(f"Recalculate window size")
    def on_size(self, event: wx.SizeEvent) -> bool:
        """
        Resize the panel so all elements are visible.

        This method is called when the plugin frame is resized. It sets the size of the panel to match the size of the
        plugin frame, and then layouts and refreshes the panel.

        Args:
            event (wx.SizeEvent): The event that triggered the resize.

        Returns:
            bool: True if the panel was resized successfully.
        """
        self.logger.trace("Resizing panel")
        self.panel.SetSize(self.plugin_frame.GetSize())
        self.panel.Layout()
        self.panel.Refresh()
        event.Skip()
        return True

    @status_message(f"Searching")
    def search(self, column: str, search: str) -> bool:
        """
        Search for a value in a column.

        This method searches for a value in a column and highlights the cell in the grid that contains the value.

        Args:
            column (str): The column to search in.
            search (str): The value to search for.

        Returns:
            bool: True if the value was found and highlighted successfully.
        """
        self.logger.debug(f"Searching for {search} in {column}")
        self.offset = 0
        self.df = duckdb.sql(f"SELECT * FROM '{self.path}' WHERE {column} = '{search}' LIMIT {self.sample_size} OFFSET {self.offset}")

        self.load_data(self.df)
        return True
