from datetime import date
from dataclasses import dataclass

DEFAULT_FIRST_DAY = 10
MONTHS = list(range(1, 13))
_FIRST_YEAR = 2018

@dataclass(frozen=True)
class MonthDate:
    month:int
    year:int

    @classmethod
    def from_date(cls, day:int, month:int, year:int, first_day = DEFAULT_FIRST_DAY):
        if day < first_day:
            month -= 1
            if month <= 0:
                year -= 1
                month = 12
        return cls(month=month, year=year)
    
    @classmethod
    def today(cls, first_day = DEFAULT_FIRST_DAY):
        t = date.today()
        return cls.from_date(t.day, t.month, t.year, first_day)

    def __str__(self):
        zero_prefix = "0" if self.month < 10 else ""
        return f"{zero_prefix}{self.month}.{self.year}r."

def first_year():
    return _FIRST_YEAR

def set_first_year(new_first_year:int):
    _FIRST_YEAR = new_first_year

def months_in_year(year:int):
    return [MonthDate(month, year) for month in MONTHS]