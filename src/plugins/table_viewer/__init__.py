import logging
from pathlib import Path

import duckdb
import wx
import wx.grid

from .components import PVButton
from .overview import Overview
from .pagination import Pagination
from ..base import IPlugin


def status_message(message):
    """
    Decorator to set the status bar message in the main window.

    This decorator function sets the status bar message to the provided message before executing the decorated function,
    and then sets the status bar message back to "Main thread ready" after the function has completed.

    Args:
        message (str): The message to be displayed in the status bar.

    Returns:
        The decorated function.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            self.status_bar.SetStatusText(message)
            result = func(self, *args, **kwargs)
            self.status_bar.SetStatusText("Main thread ready")
            return result
        return wrapper
    return decorator


class TableViewer(IPlugin):
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
    - Switching between files may cause the grid to display incorrect data. Reloading the plugin will fix this issue.
    - The grid may not resize correctly when the plugin frame is resized. Reloading the plugin will fix this issue.

    # Dependencies
    - DuckDB: To read the file and display the data in a grid
    - wxPython: To create the user interface
    """
    SAMPLE_SIZE = 100
    OFFSET = 0
    BASE_SPAN = 10

    def __init__(self):
        """
        Initialize the Table Viewer Plugin
        """
        self.logger = logging.getLogger("table_viewer")
        self.__panel = None
        self.__button = None
        self.__grid = None
        self.__overview = None
        self.__pagination = None
        self.environment = None
        self.total_rows = {}
        self.relation = {}

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
        if self.__panel:
            self.__panel.Destroy()
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
        self.__panel = wx.Panel(self.plugin_frame)
        self.__panel_sizer = wx.FlexGridSizer(3, 2, self.BASE_SPAN, self.BASE_SPAN)
        self.__panel_sizer.AddGrowableCol(0)
        self.__panel_sizer.AddGrowableCol(1)
        self.__panel_sizer.AddGrowableRow(1)

        self.__add_button()
        self.__add_overview_label()
        self.__add_grid()
        self.__add_overview()
        self.__add_pagination()
        self.__add_spacer()

        self.__main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__main_sizer.Add(self.__panel_sizer, 1, wx.EXPAND | wx.ALL, self.BASE_SPAN)
        self.__panel.SetSizer(self.__main_sizer)
        self.__panel.SetSize(self.plugin_frame.GetSize())
        self.__panel.Show()

    def __add_button(self) -> None:
        """
        Add the load file button to the panel.

        This method creates a button with the label "Load File" and associates it with the __load_file method as the
        callback function.
        """
        self.__button = PVButton(self.__panel, label="Load File", callback=self.__load_file)
        self.__panel_sizer.Add(self.__button, 1, wx.EXPAND)

    def __add_overview_label(self) -> None:
        """
        Add the overview label to the panel.

        This method creates a static text label with the text "Overview" and sets its foreground color and font style.
        """
        overview_label = wx.StaticText(self.__panel, label="Overview")
        overview_label.SetForegroundColour(wx.Colour(240, 250, 255))
        overview_label.SetExtraStyle(wx.BOLD)
        self.__panel_sizer.Add(overview_label, 1, wx.ALIGN_CENTER)

    def __add_grid(self) -> None:
        """
        Add the grid to the panel.

        This method creates a wx.grid.Grid and sets its maximum size based on the size of the plugin frame.
        """
        self.__grid = wx.grid.Grid(self.__panel)
        self.__grid.SetMaxSize(
            (self.plugin_frame.GetSize()[0] - self.plugin_frame.GetSize()[0] // 4, self.plugin_frame.GetSize()[1] // 2))
        self.__panel_sizer.Add(self.__grid, 4, wx.EXPAND)

    def __add_overview(self) -> None:
        """
        Add the overview to the panel.

        This method creates an instance of the Overview class and adds it to the panel.
        """
        self.__overview = Overview(self.__panel)
        self.__panel_sizer.Add(self.__overview, 2, wx.EXPAND)

    def __add_pagination(self) -> None:
        """
        Add the pagination to the panel.

        This method creates an instance of the Pagination class and adds it to the panel.
        """
        self.__pagination = Pagination(self.__panel, self)
        self.__panel_sizer.Add(self.__pagination, 1, wx.EXPAND)

    def __add_spacer(self) -> None:
        """
        Add a spacer to the panel.

        This method adds a static text element as a spacer to the panel.
        """
        self.__panel_sizer.Add(wx.StaticText(self.__panel, label=""), 1, wx.EXPAND)

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
    def __load_file(self, event: wx.CommandEvent) -> bool:
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
            self.__panel, "Open File",
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

            table = wx.grid.GridStringTable(self.SAMPLE_SIZE, len(columns))
            self.__grid.SetTable(table, True)

            self.__pagination.activate()
            self.load_data()
            self.__overview.update(self)

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
        key = f"{self.path}_{self.SAMPLE_SIZE}_{self.OFFSET}"
        if key not in self.relation:
            self.relation[key] = duckdb.sql(
                f"SELECT * FROM '{self.path}' LIMIT {self.SAMPLE_SIZE} OFFSET {self.OFFSET}")
        return self.relation[key]

    @status_message("Getting total rows")
    def get_total_rows(self) -> int:
        """
        Get the total number of rows in the file.

        This method retrieves the total number of rows in the file, using the file path as a key to cache the result.
        If the total number of rows is not yet cached, it is calculated and stored in the cache.

        Returns:
            int: The total number of rows in the file.
        """
        if self.path not in self.total_rows:
            self.total_rows[self.path] = duckdb.sql(f"SELECT COUNT(*) FROM '{self.path}'").fetchone()[0]
        return self.total_rows[self.path]

    @status_message("Loading Data")
    def load_data(self) -> bool:
        """
        Load the data into the grid.

        This method retrieves the data from the duckdb relation, sets the column labels in the grid, and populates the
        grid with the data. It also resizes the grid to fit the panel.

        Returns:
            bool: True if the data was loaded successfully.
        """
        columns = self.get_relation().columns
        self.logger.debug(f"Columns: {columns}")
        data = self.get_relation().fetchall()
        self.logger.debug(f"Settings up grid table with data")

        for i, column in enumerate(columns):
            self.__grid.SetColLabelValue(i, column)

        for i, row in enumerate(data):
            self.__grid.SetRowLabelValue(i, str(self.OFFSET + i + 1))
            for j, value in enumerate(row):
                self.__grid.SetCellValue(i, j, str(value))

        self.on_size(wx.SizeEvent((0, 0)))
        self.logger.debug(f"File loaded")
        return True

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
        self.__panel.SetSize(self.plugin_frame.GetSize())
        self.__panel.Layout()
        self.__panel.Refresh()
        event.Skip()
        return True
