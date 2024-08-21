from typing import TYPE_CHECKING

import wx
import inspect

if TYPE_CHECKING:
    from src.plugins.base import IPlugin


class ExceptionHandler:
    def __init__(self, exception, plugin: "IPlugin", root: wx.Frame):
        self.exception = exception
        self.plugin = plugin
        self.root = root
        self.func = inspect.currentframe().f_back.f_code

    def handle(self):
        # Show error message
        wx.MessageBox(f"An error occurred while running the plugin {self.plugin.name}\n\n{self.exception}", "Error", wx.OK | wx.ICON_ERROR)

        # Show stack trace in a new frame
        frame = wx.Frame(None, title="Stack Trace")
        text = wx.TextCtrl(frame, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Get the stack trace
        import traceback
        stack_trace = traceback.format_exc()
        text.SetValue(stack_trace)

        # Add class, function name, and line number
        text.AppendText(f"\n\nClass: {self.plugin.name}\n")
        text.AppendText(f"Function: {self.func.co_name}\n")
        text.AppendText(f"Line: {self.func.co_firstlineno}\n")

        frame.SetSize(800, 400)
        frame.SetPosition(self.root.GetPosition())
        frame.Show()

        return True
