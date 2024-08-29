import wx

from config.colors import *


class PVButton(wx.Button):
    def __init__(self, parent, label, callback, disabled=False):
        super().__init__(parent, label=label, size=(100, 30))
        self.SetForegroundColour(BUTTON_FOREGROUND)
        self.SetBackgroundColour(BUTTON_BACKGROUND)

        self.Bind(wx.EVT_BUTTON, callback)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)

        if disabled:
            self.Disable()

        self.parent_sizer = parent.GetSizer()
        self.parent_sizer.Add(self, 1, wx.EXPAND)

    def on_hover(self, event):
        self.SetBackgroundColour(BUTTON_HOVER)
        self.Refresh()
        event.Skip()

    def on_leave(self, event):
        self.SetBackgroundColour(BUTTON_BACKGROUND)
        self.Refresh()
        event.Skip()

    def on_click(self, event):
        self.SetBackgroundColour(BUTTON_CLICK)
        self.Refresh()
        event.Skip()

    def Disable(self):
        self.SetBackgroundColour(BUTTON_DISABLED)
        self.Refresh()
        super().Disable()
