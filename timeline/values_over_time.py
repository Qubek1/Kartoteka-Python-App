from timeline.month_date import MonthDate
from timeline.month_date import first_year

class ValuesOverTime:
    def __init__(self):
        self.changes: dict[MonthDate, float] = dict()
        self.values: dict[MonthDate, float] = dict()
        self.sums: dict[MonthDate, float] = dict()
        self.not_calculated_changes = False
    
    def add_change(self, date:MonthDate, value:float) -> None:
        self.changes[date] = value
        self.not_calculated_changes = True

    def remove_change(self, date:MonthDate) -> None:
        self.changes.pop(date)
        self.not_calculated_changes = True

    def get_value(self, date:MonthDate) -> float:
        if self.not_calculated_changes:
            self.calculate_values(date=date)
        return self.values[date]

    def get_sum(self, date:MonthDate) -> float:
        if self.not_calculated_changes:
            self.calculate_values(date=date)
        return self.sums[date]

    def calculate_values(self, date=MonthDate.today()) -> None:
        self.not_calculated_changes = False
        value = 0
        current_sum = 0
        for year in range(first_year(), date.year+1):
            last_month = 12
            if year == date.year:
                last_month = date.month
            for month in range(1, last_month+1):
                if MonthDate(month, year) in self.changes.keys():
                    value = self.changes[MonthDate(month, year)]
                self.values[MonthDate(month, year)] = value
                current_sum += value
                self.sums[MonthDate(month, year)] = current_sum