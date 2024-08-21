import wx
from src.plugins.parquet_viewer.components.button import PVButton

class Pagination(wx.Panel):
    BUTTONS = ("first", "prev", "next", "last")

    def __init__(self, parent, plugin):
        super().__init__(parent)
        self.logger = plugin.logger.getChild("pagination")
        self.__plugin = plugin
        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.__sizer)

        for name in self.BUTTONS:
            func = getattr(self, name)
            button = PVButton(self, label=name.title(), callback=func, disabled=True)
            setattr(self, f"__{name}_button", button)
            self.__sizer.Add(button, 1, wx.EXPAND)

        self.Show()

    def prev(self, event):
        if self.__plugin.OFFSET - self.__plugin.SAMPLE_SIZE < 0:
            self.logger.debug("Cannot go back any further")
            return
        self.__plugin.OFFSET -= self.__plugin.SAMPLE_SIZE
        self.__plugin.load_parquet_data()

    def next(self, event):
        if self.__plugin.OFFSET + self.__plugin.SAMPLE_SIZE >= self.__plugin.get_total_rows():
            self.logger.debug("Cannot go forward any further")
            return
        self.__plugin.OFFSET += self.__plugin.SAMPLE_SIZE
        self.__plugin.load_parquet_data()

    def first(self, event):
        self.__plugin.OFFSET = 0
        self.__plugin.load_parquet_data()

    def last(self, event):
        self.__plugin.OFFSET = self.__plugin.get_total_rows() - self.__plugin.SAMPLE_SIZE
        self.__plugin.load_parquet_data()

    def activate(self):
        for name in self.BUTTONS:
            button = getattr(self, f"__{name}_button")
            button.Enable()