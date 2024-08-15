from typing import TYPE_CHECKING

import wx

if TYPE_CHECKING:
    from src.plugins.base import IPlugin


class ExceptionHandler:
    def __init__(self, exception, plugin: "IPlugin", root: wx.Frame):
        self.exception = exception
        self.plugin = plugin
        self.root = root

    def handle(self):
        wx.MessageBox(f"An error occurred while running the plugin {self.plugin.name}\n\n{self.exception}", "Error", wx.OK | wx.ICON_ERROR)

        # Show stack trace in a new frame
        frame = wx.Frame(None, title="Stack Trace")
        text = wx.TextCtrl(frame, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Get the stack trace
        import traceback
        stack_trace = traceback.format_exc()
        text.SetValue(stack_trace)

        frame.SetSize(800, 400)
        frame.SetPosition(self.root.GetPosition())
        frame.Show()

        return True
