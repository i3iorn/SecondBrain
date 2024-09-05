import wx

from config.colors import *


class TVTextCntrl(wx.TextCtrl):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs, style=wx.BORDER_SIMPLE | wx.TE_CENTER | wx.TE_PROCESS_ENTER)
        self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        self.parent_sizer = parent.GetSizer()
        self.parent_sizer.Add(self, 1, wx.EXPAND)

        self.SetBackgroundColour(TEXTBOX_BACKGROUND)
        self.SetForegroundColour(TEXTBOX_FOREGROUND)

        self.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)

    def on_hover(self, event):
        self.SetBackgroundColour(TEXTBOX_BACKGROUND_HOVER)
        event.Skip()

    def on_leave(self, event):
        self.SetBackgroundColour(TEXTBOX_BACKGROUND)
        event.Skip()
