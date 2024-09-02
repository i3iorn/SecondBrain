import threading
from enum import Enum
from pathlib import Path
from typing import Tuple, TYPE_CHECKING

import wx

from config.colors import *
from src.exceptions import ExceptionHandler

if TYPE_CHECKING:
    from src.engine import Environment


class SettingMenuIName(Enum):
    """The MenuItem enum."""
    RELOAD_PLUGINS = 0
    ABOUT = 1
    QUIT = 2


class GuiApplication(wx.App):
    def __init__(self, environment: "Environment") -> None:
        self.environment = environment
        self.logger = self.environment.logger.getChild("gui")
        self.plugin_lock = threading.Lock()
        super().__init__(False)

    def OnInit(self) -> bool:
        # Create the main window
        self.root_frame = wx.Frame(None, title=self.environment.get("application", {}).get("name", "Application"))

        # Set icon
        icon_path = Path(__file__).parent.parent.parent.joinpath("assets").joinpath(self.environment.get("application", {}).get("icon"))
        self.logger.debug(f"Setting icon: {icon_path.absolute()}")
        if icon_path:
            icon = wx.Icon(icon_path.as_posix())
            self.root_frame.SetIcon(icon)

        # Set window size
        size = self.environment.get("application", {}).get("size", {}).get("width", 800), self.environment.get("application", {}).get("size", {}).get("height", 600)
        self.root_frame.SetMinSize(size)

        # Set window position
        position = self.environment.get("application", {}).get("position", {}).get("x"), self.environment.get("application", {}).get("position", {}).get("y")
        if position[0] is not None and position[1] is not None:
            self.root_frame.SetPosition(position)
        else:
            position = self.__center_on_all_monitors(self.root_frame)
        self.root_frame.SetPosition(position)

        self.__setup_plugin_frame()
        self.__setup_status_bar()
        self.__setup_menu()

        # Show the main window
        self.root_frame.Show()
        return True

    def OnExit(self) -> bool:
        self.logger.debug("Destroying GuiApplication")
        return True

    def OnAbout(self, event: "wx.Event") -> bool:
        msg = (f"Second Brain\n\n Version: {self.environment.get('application', {}).get('version', '0.0.1')}\n")
        wx.MessageBox(msg, "About", wx.OK | wx.ICON_INFORMATION)
        return True

    def OnQuit(self, event: "wx.Event") -> bool:
        self.OnExit()
        self.root_frame.Close()
        return True

    def OnPluginStart(self, event: "wx.Event") -> None:
        plugin_name = self.menu_bar.GetLabel(event.GetId())
        plugin = next((plugin for plugin in self.environment.plugins if plugin.name == plugin_name), None)
        if plugin:
            def run_plugin():
                try:
                    plugin.run(self.environment)
                except Exception as e:
                    ExceptionHandler(e, plugin, self.root_frame).handle()
                finally:
                    self.plugin_lock.release()

            if self.plugin_lock.acquire(blocking=False):
                self.active_plugin = plugin
                self.plugin_thread = threading.Thread(target=run_plugin, daemon=True)
                self.plugin_thread.start()
            else:
                self.logger.warning("Another plugin is already running")

    def OnReloadPlugins(self, event: "wx.Event") -> bool:
        """Reload all plugins from the plugins folder"""
        for plugin in self.environment.plugins:
            plugin.stop()

        self.environment.plugins = self.environment.reload_plugins()
        self.logger.info("Plugins reloaded")
        return True

    def OnForceClosePlugin(self, event: "wx.Event") -> bool:
        """Force close the running plugin"""
        if hasattr(self, "active_plugin"):
            self.active_plugin.stop()
            self.logger.info("Active plugin closed")
            self.plugin_thread.join(5)
            self.active_plugin = None
        else:
            self.logger.warning("No plugin is running")
        return True

    def __setup_menu(self) -> bool:
        """
        Setup the menu bar. This method creates the menu bar and adds the plugin and settings menus.

        Returns:
            bool: True if the menu bar was successfully setup, False otherwise
        """
        self.menu_bar = wx.MenuBar()
        self.root_frame.SetMenuBar(self.menu_bar)
        self.menu_bar.Append(self.__setup_plugin_menu(), "&Plugins")
        self.menu_bar.Append(self.__setup_settings_menu(), "&Settings")

    def __setup_plugin_menu(self) -> wx.Menu:
        """
        Setup the plugin menu. This method creates the plugin menu and adds the plugins to the menu.

        Returns:
            wx.Menu: The plugin menu
        """
        plugins = wx.Menu()
        for plugin in self.environment.plugins:
            plugins.Append(
                wx.ID_ANY,
                plugin.name
            )
            self.root_frame.Bind(wx.EVT_MENU, self.OnPluginStart, plugins.FindItemById(wx.ID_ANY))
        return plugins

    def __setup_settings_menu(self) -> wx.Menu:
        """
        Setup the settings menu. This method creates the settings menu and adds the settings to the menu.

        Returns:
            wx.Menu: The settings menu
        """
        settings = wx.Menu()
        for setting in SettingMenuIName:
            settings.Append(
                setting.value,
                setting.name.replace("_", " ").title()
            )
            func_ = getattr(self, f"On{setting.name.title().replace('_', '')}")
            self.root_frame.Bind(wx.EVT_MENU, func_, settings.FindItemById(setting.value))
        return settings

    def __setup_plugin_frame(self) -> bool:
        """
        Setup the plugin frame. This method creates the plugin frame and sets the background color.

        Returns:
            bool: True if the plugin frame was successfully setup, False otherwise
        """
        self.plugin_frame = wx.Panel(self.root_frame)
        self.plugin_frame.SetBackgroundColour(wx.Colour(WINDOW_BACKGROUND))

        self.plugin_sizer = wx.BoxSizer(wx.VERTICAL)
        self.plugin_frame.SetSizer(self.plugin_sizer)

        self.root_frame.SetClientSize(self.plugin_frame.GetSize())
        self.environment['plugin_frame'] = self.plugin_frame
        return True

    def __setup_status_bar(self) -> bool:
        """
        Setup the status bar. This method creates the status bar and sets the default text.

        Returns:
            bool: True if the status bar was successfully setup, False otherwise
        """
        self.environment['status_bar'] = self.root_frame.CreateStatusBar()

        # Create a space to display running sub-processes
        self.environment['status_bar'].SetFieldsCount(2)
        self.environment['status_bar'].SetStatusWidths([
            -1,
            self.environment["application"].get("status_bar", {}).get("sub_process", {}).get("width", 200)
        ])

        # Set the default text for the status bar
        self.environment['status_bar'].SetStatusText("Main thread ready", 0)

        # Set the default text for the sub-processes
        self.environment['status_bar'].SetStatusText("No sub-processes running", 1)
        return True

    @staticmethod
    def __center_on_all_monitors(frame: wx.Frame) -> Tuple:
        """
        Center the frame on all monitors. This method calculates the center of all monitors and centers the frame on the
        monitor that contains the center of the frame.

        Args:
            frame: The frame to center

        Returns:
            Tuple: The position of the frame
        """
        # Get the number of displays
        num_displays = wx.Display.GetCount()

        top = 0
        bottom = 0
        leftmost = 0
        rightmost = 0

        # Get the dimensions of all displays
        for i in range(num_displays):
            display = wx.Display(i)
            x, y, width, height = display.GetGeometry()
            if x < leftmost:
                leftmost = x
            if y < top:
                top = y

            if x + width > rightmost:
                rightmost = x + width
            if y + height > bottom:
                bottom = y + height

        # Calculate the frame size and position
        frame_width, frame_height = frame.GetSize()
        frame_x = leftmost + (rightmost - leftmost - frame_width) // 2
        frame_y = top + (bottom - top - frame_height) // 2

        # Get the screen that contains the center of the frame
        display = wx.Display.GetFromPoint((frame_x + frame_width // 2, frame_y + frame_height // 2))

        # Center the frame on the display
        x, y, width, height = wx.Display(display).GetGeometry()
        frame_x = x + (width - frame_width) // 2
        frame_y = y + (height - frame_height) // 2

        # Set the frame position
        return frame_x, frame_y
