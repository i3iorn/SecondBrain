import wx

from config.colors import *


class BasePanel(wx.Panel):
    def __init__(self, parent: wx.Panel) -> None:
        super().__init__(parent)
        self.parent_sizer = parent.GetSizer().GetItem(0).GetSizer()
        self.parent_sizer.Add(self, 1, wx.EXPAND)

        self.SetForegroundColour(COMPONENT_FOREGROUND)

        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Avenir")
        self.SetFont(font)

        self.__outer_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__outer_sizer)

    @property
    def outer_sizer(self):
        return self.__outer_sizer
