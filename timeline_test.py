import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout

from timeline.month_date import MonthDate
from timeline.values_over_time import ValuesOverTime
from timeline.timeline_table import *

from json_generics.save_and_load import json_load, json_save

class MainApp(QWidget, AbstractUpdateable):
    def __init__(self):
        super().__init__()
        values_over_time:ValuesOverTime = json_load("timeline_test.json", ValuesOverTime)
        if values_over_time is None:
            values_over_time = ValuesOverTime(calculate_sum=False)
        #values_over_time.add_change(MonthDate.from_date(30, 1, 2025),100)
        #values_over_time.add_change(MonthDate.from_date(30, 4, 2025),200)
        values_over_time.calculate_values()
        self.values_over_time = values_over_time

        self.setLayout(QVBoxLayout())

        table = TimelineTable(on_update_event=self.update)
        table.add_column(ColumnValues("values", values_over_time, table, integer_values=True))
        table.add_column(ColumnValuesChange("change", values_over_time, table, editable=True, integer_values=True))
        table.add_column(ColumnValuesChangesDelete("delete", values_over_time, table))
        table.add_column(ColumnValuesSum("sums", values_over_time, table))
        self.layout().addWidget(table)
        table.update()

        self.resize(1000, 500)

    def update(self):
        json_save(self.values_over_time, "timeline_test.json")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = MainApp()
    demo.show()
    sys.exit(app.exec())