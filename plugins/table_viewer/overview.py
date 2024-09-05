import wx

from config.colors import *
from . import PVButton
from .components.combobox import TVCombobox
from .components.panel import BasePanel
from .components.textcntrl import TVTextCntrl


class OverviewPanel(BasePanel):
    def __init__(self, tv: "TableViewer") -> None:
        super().__init__(tv.panel)
        self.__sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(self.__sizer)

        self.__plugin = tv
        self.logger = tv.logger.getChild("overview")

        self.setup_ui()
        self.SetBackgroundColour(COMPONENT_BACKGROUND)

        self.Show()

    def setup_ui(self):
        self.__setup_data_panel()
        self.__sizer.AddSpacer(10)
        self.__setup_search_panel()

        self.Layout()
        return True

    def __setup_data_panel(self):
        self.data_panel = wx.Panel(self)
        self.data_panel.SetBackgroundColour(COMPONENT_BACKGROUND)
        self.data_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.data_panel.SetSizer(self.data_sizer)
        self.__sizer.Add(self.data_panel, 1, wx.EXPAND)
        self.data_panel.Show()

        self.__setup_total_rows()
        self.data_sizer.AddSpacer(10)
        self.__setup_total_columns()

        return True

    def __setup_total_rows(self):
        self.total_rows_label = wx.StaticText(self.data_panel, label="Total Rows: ")
        self.total_rows_value = wx.StaticText(self.data_panel, label="0", size=wx.Size(100, -1))
        self.data_sizer.Add(self.total_rows_label, 0, wx.EXPAND)
        self.data_sizer.Add(self.total_rows_value, 0, wx.EXPAND)

        return True

    def __setup_total_columns(self):
        self.total_columns_label = wx.StaticText(self.data_panel, label="Total Columns: ")
        self.total_columns_value = wx.StaticText(self.data_panel, label="0", size=wx.Size(100, -1))
        self.data_sizer.Add(self.total_columns_label, 0, wx.EXPAND)
        self.data_sizer.Add(self.total_columns_value, 0, wx.EXPAND)

        return True

    def __setup_search_panel(self):
        self.search_panel = wx.Panel(self)
        self.search_panel.SetBackgroundColour(COMPONENT_BACKGROUND)
        self.search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_panel.SetSizer(self.search_sizer)
        self.__sizer.Add(self.search_panel, 0, wx.EXPAND)
        self.search_panel.Show()

        self.__setup_column_choices()
        self.__setup_search_style_combobox()
        self.__setup_search_input()
        self.__setup_search_button()

        return True

    def __setup_column_choices(self):
        self.column_choices = TVCombobox(self.search_panel, choices=[""], size=wx.Size(80, -1))

        return True

    def __setup_search_input(self):
        self.search_input = TVTextCntrl(self.search_panel)
        return True

    def __setup_search_style_combobox(self):
        self.search_style_combobox = TVCombobox(self.search_panel, choices=["Exact", "Contains", "Starts With", "Ends With", "Is Empty", "Is not Empty"], size=wx.Size(80, -1))
        self.search_style_combobox.SetSelection(0)

        self.search_style_combobox.Bind(wx.EVT_COMBOBOX, self.OnComboSelect)
        return True

    def __setup_search_button(self):
        self.search_button = PVButton(self.search_panel, label="Search", callback=self.OnSearch)

        return True

    def update(self, total_rows: int, columns: list):
        self.update_total_rows(total_rows)
        self.update_total_columns(len(columns))
        self.update_column_choices(columns)
        return True

    def update_total_rows(self, total_rows: int):
        self.total_rows_value.SetLabel(str(total_rows))
        return True

    def update_total_columns(self, total_columns: int):
        self.total_columns_value.SetLabel(str(total_columns))
        return True

    def update_column_choices(self, columns: list):
        self.column_choices.Clear()
        self.column_choices.AppendItems(columns)

        # Select the first column by default
        self.column_choices.SetSelection(0)

        return True

    def OnComboSelect(self, event: wx.Event):
        if self.search_style_combobox.GetStringSelection() == "Is Empty" or self.search_style_combobox.GetStringSelection() == "Is not Empty":
            self.search_input.SetValue("")
            self.search_input.Disable()
        else:
            self.search_input.Enable()

        return

    def OnSearch(self, event: wx.Event):
        column = self.column_choices.GetStringSelection()
        search = self.search_input.GetValue()
        style = self.search_style_combobox.GetStringSelection()

        self.logger.debug(f"Searching for {search} in {column}")

        self.__plugin.search(column, search, style)

        return True