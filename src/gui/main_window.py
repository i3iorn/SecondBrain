import threading
from typing import Tuple, TYPE_CHECKING

import wx

from src.exceptions import ExceptionHandler

if TYPE_CHECKING:
    from src.engine import Environment


class GuiApplication(wx.App):
    def __init__(self, environment: "Environment"):
        self.environment = environment
        self.logger = self.environment.logger.getChild("gui")
        self.plugin_lock = threading.Lock()
        super().__init__(False)

        if hasattr(self.environment, "profiler"):
            self.environment.profiler.add_function(self.OnInit)
            self.environment.profiler.add_function(self.OnExit)
            self.environment.profiler.add_function(self.OnAbout)
            self.environment.profiler.add_function(self.OnQuit)
            self.environment.profiler.add_function(self.OnPluginStart)
            self.environment.profiler.add_function(self.OnReloadPlugins)
            self.environment.profiler.add_function(self.__setup_menu)
            self.environment.profiler.add_function(self.__setup_plugin_frame)
            self.environment.profiler.add_function(self.__setup_status_bar)
            self.environment.profiler.add_function(self.__center_on_all_monitors)

    def OnInit(self):
        # Create the main window
        self.root_frame = wx.Frame(None, title=self.environment.get("application", {}).get("name", "Application"))

        # Set icon
        icon_path = self.environment.get("application", {}).get("icon")
        if icon_path:
            icon = wx.Icon(icon_path)
            self.root_frame.SetIcon(icon)

        # Set window minimum size
        x, y = wx.DisplaySize()
        self.root_frame.SetMinSize((x // 2, y // 2))

        # Set window size
        size = self.environment.get("application", {}).get("size", {}).get("width", 800), self.environment.get("application", {}).get("size", {}).get("height", 600)
        self.root_frame.SetSize(size)

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

    def OnExit(self):
        self.logger.debug("Destroying GuiApplication")
        if hasattr(self.environment, "profiler") and self.logger.getEffectiveLevel() < 5:
            self.environment.profiler.disable()
            self.environment.profiler.print_stats()
        return True

    def OnAbout(self, event):
        wx.MessageBox("This is a wxPython application\n\nIcon made by Freepik from www.flaticon.com", "About", wx.OK | wx.ICON_INFORMATION)
        return True

    def OnQuit(self, event):
        self.OnExit()
        self.root_frame.Close()
        return True

    def OnPluginStart(self, event):
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

    def OnReloadPlugins(self, event):
        """Reload all plugins from the plugins folder"""
        for plugin in self.environment.plugins:
            plugin.stop()
            del plugin

        self.environment.plugins = self.environment.reload_plugins()
        self.logger.info("Plugins reloaded")
        return True

    def OnForceClosePlugin(self, event):
        """Force close the running plugin"""
        if hasattr(self, "active_plugin"):
            self.active_plugin.stop()
            self.logger.info("Active plugin closed")
            self.plugin_thread.join()
            del self.active_plugin
        else:
            self.logger.warning("No plugin is running")
        return True

    def __setup_menu(self):
        self.menu_bar = wx.MenuBar()
        self.root_frame.SetMenuBar(self.menu_bar)

        plugins = wx.Menu()
        self.menu_bar.Append(plugins, "&Plugins")

        for plugin in self.environment.plugins:
            plugin_menu = plugins.Append(wx.ID_ANY, plugin.name)
            self.root_frame.Bind(wx.EVT_MENU, self.OnPluginStart, plugin_menu)

        settings = wx.Menu()
        self.menu_bar.Append(settings, "&Settings")

        reload_plugins_item = settings.Append(wx.ID_ANY, "&Reload Plugins", "Reload all plugins")
        self.root_frame.Bind(wx.EVT_MENU, self.OnReloadPlugins, reload_plugins_item)

        about_item = settings.Append(wx.ID_ABOUT, "&About", "Information about this application")
        self.root_frame.Bind(wx.EVT_MENU, self.OnAbout, about_item)

        force_close_plugin_item = settings.Append(wx.ID_ANY, "&Close Active Plugin", "Force close the running plugin")
        self.root_frame.Bind(wx.EVT_MENU, self.OnForceClosePlugin, force_close_plugin_item)

        quit_item = settings.Append(wx.ID_EXIT, "&Quit", "Quit this application")
        self.root_frame.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        return True

    def __setup_plugin_frame(self):
        self.plugin_frame = wx.Panel(self.root_frame)
        self.plugin_frame.SetBackgroundColour(wx.Colour(35, 45, 65))

        self.plugin_sizer = wx.BoxSizer(wx.VERTICAL)
        self.plugin_frame.SetSizer(self.plugin_sizer)

        self.root_frame.SetClientSize(self.plugin_frame.GetSize())
        self.environment['plugin_frame'] = self.plugin_frame
        return True

    def __setup_status_bar(self):
        self.environment['status_bar'] = self.root_frame.CreateStatusBar()

        # Create a space to display running sub-processes
        self.environment['status_bar'].SetFieldsCount(2)
        self.environment['status_bar'].SetStatusWidths([-1, 200])

        # Set the default text for the status bar
        self.environment['status_bar'].SetStatusText("Main thread ready", 0)

        # Set the default text for the sub-processes
        self.environment['status_bar'].SetStatusText("No sub-processes running", 1)
        return True

    @staticmethod
    def __center_on_all_monitors(frame: wx.Frame) -> Tuple:
        # Get the number of available displays
        num_displays = wx.Display.GetCount()

        top = 0
        bottom = 0
        leftmost = 0
        rightmost = 0
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
