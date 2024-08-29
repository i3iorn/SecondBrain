import wx

from .components.button import PVButton
from .components.panel import BasePanel


class LoadFilePanel(BasePanel):
    def __init__(self, tv: "TableViewer") -> None:
        super().__init__(tv.panel)
        self.__plugin = tv
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.__sizer)

        self.__load_button = PVButton(self, "Load File", self.__plugin.load_file)
