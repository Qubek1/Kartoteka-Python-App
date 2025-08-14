from timeline.month_date import MonthDate
from timeline.month_date import first_year

class ValuesOverTime:
    def __init__(self):
        self.changes: dict[MonthDate, float] = dict()
        self.values: dict[MonthDate, float] = dict()
        self.sums: dict[MonthDate, float] = dict()
    
    def add_change(self, date:MonthDate, value:float) -> None:
        self.changes[date] = value

    def remove_change(self, date:MonthDate) -> None:
        self.changes.pop(date)

    def get_value_after_calculations(self, date:MonthDate) -> float:
        return self.values[date]

    def get_sum_after_calculations(self, date:MonthDate) -> float:
        return self.sums[date]

    def calculate_values(self, date=MonthDate.today()) -> None:
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