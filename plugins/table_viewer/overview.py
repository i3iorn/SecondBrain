import wx

from .components.panel import BasePanel


class OverviewPanel(BasePanel):
    def __init__(self, tv: "TableViewer") -> None:
        super().__init__(tv.panel)
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)
