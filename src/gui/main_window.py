from typing import Tuple, TYPE_CHECKING

import wx

from src.exceptions import ExceptionHandler

if TYPE_CHECKING:
    from src.engine import Environment


class GuiApplication(wx.App):
    def __init__(self, environment: "Environment"):
        self.environment = environment
        super().__init__(False)

    def OnInit(self):
        # Create the main window
        self.root_frame = wx.Frame(None, title=self.environment.get("application", {}).get("name", "Application"))

        # Set icon
        icon_path = self.environment.get("application", {}).get("icon")
        if icon_path:
            icon = wx.Icon(icon_path)
            self.root_frame.SetIcon(icon)

        # Set window minimum size
        min_size = 400, 300
        self.root_frame.SetMinSize(min_size)

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
        self.root_frame.Destroy()
        return True

    def OnAbout(self, event):
        wx.MessageBox("This is a wxPython application\n\nIcon made by Freepik from www.flaticon.com", "About", wx.OK | wx.ICON_INFORMATION)
        return True

    def OnQuit(self, event):
        self.root_frame.Close()
        return True

    def OnPluginStart(self, event):
        plugin_name = self.menu_bar.GetLabel(event.GetId())
        plugin = next((plugin for plugin in self.environment.plugins if plugin.name == plugin_name), None)
        if plugin:
            try:
                plugin.run(event, self.environment.config)
            except Exception as e:
                ExceptionHandler(e, plugin, self.root_frame).handle()

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

        about_item = settings.Append(wx.ID_ABOUT, "&About", "Information about this application")
        self.root_frame.Bind(wx.EVT_MENU, self.OnAbout, about_item)

        quit_item = settings.Append(wx.ID_EXIT, "&Quit", "Quit this application")
        self.root_frame.Bind(wx.EVT_MENU, self.OnQuit, quit_item)
        return True

    def __setup_plugin_frame(self):
        self.plugin_frame = wx.Panel(self.root_frame)
        self.plugin_frame.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.plugin_sizer = wx.BoxSizer(wx.VERTICAL)
        self.plugin_frame.SetSizer(self.plugin_sizer)

        self.root_frame.SetClientSize(self.plugin_frame.GetSize())
        self.environment['plugin_frame'] = self.plugin_frame
        return True

    def __setup_status_bar(self):
        self.status_bar = self.root_frame.CreateStatusBar()

        # Create a space to display running sub-processes
        self.status_bar.SetFieldsCount(2)
        self.status_bar.SetStatusWidths([-1, 100])

        # Set the default text for the status bar
        self.status_bar.SetStatusText("Ready", 0)

        # Set the default text for the sub-processes
        self.status_bar.SetStatusText("No sub-processes running", 1)
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
