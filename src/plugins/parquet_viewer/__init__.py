import wx
import wx.grid
import duckdb
from .components import PVButton
from .overview import Overview
from .pagination import Pagination
from ..base import IPlugin


def status_message(message):
    """
    Decorator to set the status bar message in the main window

    :param message: The message to be displayed
    :type message: str
    :return: The decorated function
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            wx.CallAfter(self.status_bar.SetStatusText, message)
            result = func(self, *args, **kwargs)
            wx.CallAfter(self.status_bar.SetStatusText, "Main thread ready")
            return result
        return wrapper
    return decorator


class ParquetViewer(IPlugin):
    SAMPLE_SIZE = 100
    OFFSET = 0
    BASE_SPAN = 10

    def __init__(self):
        """
        Initialize the Parquet Viewer Plugin
        """
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
        Get the name of the plugin

        :return: The name of the plugin
        :rtype: str
        """
        return "Parquet Viewer"

    @property
    def plugin_frame(self) -> wx.Frame:
        """
        Get the plugin frame

        :return: The plugin frame
        :rtype: wx.Frame
        """
        return self.environment.get("plugin_frame") if self.environment else None

    @property
    def status_bar(self) -> wx.StatusBar:
        """
        Get the status bar

        :return: The status bar
        :rtype: wx.StatusBar
        """
        return self.environment.get("status_bar") if self.environment else None

    def stop(self) -> bool:
        """
        Stop the Parquet Viewer

        :return: True if the plugin was stopped successfully
        :rtype: bool
        """
        self.logger.debug("Stopping Parquet Viewer")
        self.__panel.Destroy()
        return True

    def run(self, environment) -> bool:
        """
        Run the Parquet Viewer

        :param environment: The environment to run the plugin in
        :type environment: Environment
        :return: True if the plugin was run successfully
        :rtype: bool
        """
        # TODO: This needs to be rewritten to support plugins running in their own thread
        self.environment = environment
        self.logger = self.environment.logger.getChild("parquet_viewer")
        self.__initialize_ui()
        self.__bind_events()
        return True

    def __initialize_ui(self) -> None:
        """
        Initialize the user interface

        :return: None
        """
        # Create the panel
        self.__panel = wx.Panel(self.plugin_frame)
        self.__panel_sizer = wx.FlexGridSizer(3, 2, self.BASE_SPAN, self.BASE_SPAN)
        self.__panel_sizer.AddGrowableCol(0)
        self.__panel_sizer.AddGrowableCol(1)
        self.__panel_sizer.AddGrowableRow(1)

        # Add the elements to the panel
        self.__add_button()
        self.__add_overview_label()
        self.__add_grid()
        self.__add_overview()
        self.__add_pagination()
        self.__add_spacer()

        # Add the panel to the plugin frame
        self.__main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__main_sizer.Add(self.__panel_sizer, 1, wx.EXPAND | wx.ALL, self.BASE_SPAN)
        self.__panel.SetSizer(self.__main_sizer)
        self.__panel.SetSize(self.plugin_frame.GetSize())
        self.__panel.Show()

    def __add_button(self) -> None:
        """
        Add the load parquet file button to the panel

        :return: None
        """
        self.__button = PVButton(self.__panel, label="Load Parquet File", callback=self.__load_parquet_file)
        self.__panel_sizer.Add(self.__button, 1, wx.EXPAND)

    def __add_overview_label(self) -> None:
        """
        Add the overview label to the panel

        :return: None
        """
        overview_label = wx.StaticText(self.__panel, label="Overview")
        overview_label.SetForegroundColour(wx.Colour(240, 250, 255))
        overview_label.SetExtraStyle(wx.BOLD)
        self.__panel_sizer.Add(overview_label, 1, wx.ALIGN_CENTER)

    def __add_grid(self) -> None:
        """
        Add the grid to the panel

        :return: None
        """
        self.__grid = wx.grid.Grid(self.__panel)
        self.__grid.SetMaxSize(
            (self.plugin_frame.GetSize()[0] - self.plugin_frame.GetSize()[0] // 4, self.plugin_frame.GetSize()[1] // 2))
        self.__panel_sizer.Add(self.__grid, 1, wx.EXPAND)

    def __add_overview(self) -> None:
        """
        Add the overview to the panel

        :return: None
        """
        self.__overview = Overview(self.__panel)
        self.__panel_sizer.Add(self.__overview, 1, wx.EXPAND)

    def __add_pagination(self) -> None:
        """
        Add the pagination to the panel

        :return: None
        """
        self.__pagination = Pagination(self.__panel, self)
        self.__panel_sizer.Add(self.__pagination, 1, wx.EXPAND)

    def __add_spacer(self) -> None:
        """
        Add a spacer to the panel

        :return: None
        """
        self.__panel_sizer.Add(wx.StaticText(self.__panel, label=""), 1, wx.EXPAND)

    def __bind_events(self) -> None:
        """
        Bind the resizing events to the plugin frame to ensure the panel resizes correctly

        :return: None
        """
        for event in [wx.EVT_SIZE, wx.EVT_MAXIMIZE, wx.EVT_ICONIZE, wx.EVT_CLOSE, wx.EVT_MOVE, wx.EVT_SIZING]:
            self.plugin_frame.Bind(event, self.on_size)

    @status_message("Begin loading parquet file")
    def __load_parquet_file(self, event: wx.CommandEvent) -> bool:
        """
        Load a parquet file

        :param event: The event that triggered the load
        :type event: wx.CommandEvent
        :return: True if the parquet file was loaded successfully
        """
        file_dialog = wx.FileDialog(self.__panel, "Open Parquet File", wildcard="Parquet files (*.parquet)|*.parquet",
                                    style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if file_dialog.ShowModal() == wx.ID_OK:
            self.logger.debug("Loading Parquet File")
            self.path = file_dialog.GetPath()
            self.logger.debug(f"Path: {self.path}")

            columns = duckdb.sql(f"SELECT * FROM '{self.path}' LIMIT 1").columns
            if not columns:
                self.logger.error("No columns found in parquet file")
                return False

            self.__grid.CreateGrid(self.SAMPLE_SIZE, len(columns))
            self.__pagination.activate()
            self.load_parquet_data()
            self.__overview.update(self)

        return True

    @status_message("Setting up file relation")
    def get_relation(self) -> "duckdb.DuckDBPyRelation":
        """
        Get the duckdb relation of the parquet file

        :return: The relation of the parquet file
        """
        self.logger.debug(f"Loading {self.SAMPLE_SIZE} rows from {self.path} with an offset of '{self.OFFSET}'")
        key = f"{self.path}_{self.SAMPLE_SIZE}_{self.OFFSET}"
        if key not in self.relation:
            self.relation[key] = duckdb.sql(f"SELECT * FROM '{self.path}' LIMIT {self.SAMPLE_SIZE} OFFSET {self.OFFSET}")
        return self.relation[key]

    @status_message("Getting total rows")
    def get_total_rows(self) -> int:
        """
        Get the total number of rows in the parquet file

        :return: The total number of rows in the parquet file
        :rtype: int
        """
        if self.path not in self.total_rows:
            self.total_rows[self.path] = duckdb.sql(f"SELECT COUNT(*) FROM '{self.path}'").fetchone()[0]
        return self.total_rows[self.path]

    @status_message("Loading Parquet Data")
    def load_parquet_data(self) -> bool:
        """
        Load the parquet data into the grid

        :return: True if the parquet data was loaded successfully
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
        self.logger.debug(f"Parquet file loaded")
        return True

    def on_size(self, event: wx.SizeEvent) -> bool:
        """
        Resize the panel so all elements are visible

        :param event: The event that triggered the resize
        :return: True if the panel was resized successfully
        """
        self.logger.trace("Resizing panel")
        self.__main_sizer.Layout()
        self.__panel.SetSize(self.plugin_frame.GetSize())
        self.__panel.Layout()
        self.__panel.Refresh()
        event.Skip()
        return True