import wx


class PVButton(wx.Button):
    def __init__(self, parent, label, callback, disabled=False):
        super().__init__(parent, label=label, size=(100, 30))
        self.default_background_color = self.GetBackgroundColour()
        self.default_foreground_color = self.GetForegroundColour()

        self.Bind(wx.EVT_BUTTON, callback)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_click)

        if disabled:
            self.Disable()

    def on_hover(self, event):
        darker_color = self.default_background_color.ChangeLightness(85)
        self.SetBackgroundColour(darker_color)
        self.Refresh()
        event.Skip()

    def on_leave(self, event):
        self.SetBackgroundColour(self.default_background_color)
        self.SetForegroundColour(self.default_foreground_color)
        self.Refresh()
        event.Skip()

    def on_click(self, event):
        self.SetBackgroundColour(wx.Colour(150, 150, 150))  # Darker grey
        self.Refresh()
        event.Skip()
