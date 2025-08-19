#Timeline
from timeline.month_date import MonthDate
from timeline.month_date import months_in_year
from timeline.values_over_time import ValuesOverTime

#Input Fields
from generic_widgets.input_fields import FloatInputField
from generic_widgets.input_fields import IntInputField
from generic_widgets.input_fields import float_to_str

from generic_widgets.better_q_combo_box import QComboBoxSearcheable

#PyQt Widgets
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton

class AbstractUpdateable:
    def update(self):
        pass

class AbstractColumn:
    header:str
    custom_widget:bool
    table_to_update:AbstractUpdateable

    def get_str(self, date:MonthDate) -> str:
        pass

    def create_widget(self, date:MonthDate) -> QWidget:
        pass


class ColumnValuesSum(AbstractColumn):
    values:ValuesOverTime
    integer_values:bool
    precision:int

    def __init__(self, header:str, values:ValuesOverTime, integer_values = False, precision = 2):
        self.header = header
        self.values = values
        self.integer_values = integer_values
        if integer_values:
            self.precision = 0
        else:
            self.precision = precision
        self.custom_widget = False

    def get_str(self, date:MonthDate) -> str:
        if date in self.values.sums.keys():
            return float_to_str(self.values.get_sum(date), self.precision)
        return ""
    

class ColumnValues(AbstractColumn):
    values:ValuesOverTime
    integer_values:bool
    precision:int

    def __init__(self, header:str, values:ValuesOverTime, table_to_update:AbstractUpdateable, integer_values = False, precision = 2, editable = False):
        self.header = header
        self.values = values
        self.table_to_update = table_to_update
        self.integer_values = integer_values
        if integer_values:
            self.precision = 0
        else:
            self.precision = precision
        self.custom_widget = editable

    def get_str(self, date):
        if date in self.values.values.keys():
            return float_to_str(self.values.get_value(date), self.precision)
        return ""
    
    def create_widget(self, date):
        new_widget = None
        if date in self.values.values.keys():
            if self.integer_values:
                new_widget = IntInputField(self.values.get_value(date))
            else:
                new_widget = FloatInputField(self.values.get_value(date))
                new_widget.precision = self.precision
            new_widget.subscribe(lambda new_value: self._on_edit(date, new_value))
        return new_widget
        
    def _on_edit(self, date:MonthDate, new_value:float|int):
        self.values.add_change(date, new_value)
        self.values.calculate_values()
        self.table_to_update.update()


class ColumnValuesChange(AbstractColumn):
    values:ValuesOverTime
    integer_values:bool
    precision:int

    def __init__(self, header:str, values:ValuesOverTime, table_to_update:AbstractUpdateable, integer_values = False, precision = 2, editable = False):
        self.header = header
        self.values = values
        self.table_to_update = table_to_update
        self.integer_values = integer_values
        if integer_values:
            self.precision = 0
        else:
            self.precision = precision
        self.custom_widget = editable

    def get_str(self, date):
        if date in self.values.changes.keys():
            return float_to_str(self.values.get_value(date), self.precision)
        return ""

    def create_widget(self, date):
        new_widget = None
        if date in self.values.values.keys():
            input_field_value = None
            if date in self.values.changes.keys():
                input_field_value = self.values.get_value(date)
            if self.integer_values:
                new_widget = IntInputField(input_field_value, accept_None_value=True)
            else:
                new_widget = FloatInputField(input_field_value, accept_None_value=True, precision=self.precision)
            new_widget.subscribe(lambda new_value: self._on_edit(date, new_value))
        return new_widget
        
    def _on_edit(self, date:MonthDate, new_value:float|int|None):
        if new_value is None:
            self.values.remove_change(date)
        else:
            self.values.add_change(date, new_value)
        self.values.calculate_values()
        self.table_to_update.update()


class ColumnValuesChangesDelete(AbstractColumn):
    values:ValuesOverTime

    def __init__(self, header:str, values:ValuesOverTime, table_to_update:AbstractUpdateable):
        self.header = header
        self.values = values
        self.table_to_update = table_to_update
        self.custom_widget = True

    def create_widget(self, date):
        if date in self.values.changes.keys():
            new_button = QPushButton(text="Usuń")
            new_button.clicked.connect(lambda :self._on_clicked(date))
            return new_button
        return None
    
    def _on_clicked(self, date:MonthDate):
        self.values.remove_change(date)
        self.values.calculate_values()
        self.table_to_update.update()


class TimelineTable(AbstractUpdateable, QTableWidget):
    columns:list[AbstractColumn]
    current_year:int
    year_selection:QComboBoxSearcheable

    def __init__(self, current_year:int = MonthDate.today().year, columns:list[AbstractColumn] = []):
        super().__init__()
        self.current_year = current_year
        self.columns = columns
        self.year_selection = QComboBoxSearcheable()

    def add_column(self, column:AbstractColumn):
        self.columns.append(column)

    def update(self):
        self.clear()
        self.setColumnCount(len(self.columns))
        self.setRowCount(12)
        horizontal_labels = [column.header for column in self.columns]
        self.setHorizontalHeaderLabels(horizontal_labels)
        vertical_labels = [str(date) for date in months_in_year(self.current_year)]
        self.setVerticalHeaderLabels(vertical_labels)
        for y, date in enumerate(months_in_year(self.current_year)):
            for x, column in enumerate(self.columns):
                if column.custom_widget:
                    self.setCellWidget(y, x, column.create_widget(date))
                else:
                    print(x, y, column.get_str(date))
                    self.setItem(y, x, QTableWidgetItem(column.get_str(date)))
        