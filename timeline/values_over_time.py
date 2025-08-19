from timeline.month_date import MonthDate, first_year
from json_generics.serializable import JsonSerializable
from json_generics.collections import serialize_dict, deserialize_to_dict

# from month_date import MonthDate
# from month_date import first_year
# import json

class ValuesOverTime(JsonSerializable):
    changes:dict[MonthDate, float]
    values:dict[MonthDate, float]
    sums:dict[MonthDate, float]
    not_calculated_changes:bool
    calculate_sums:bool
    save_calculations:bool

    CHANGES_KEY = "changes"
    VALUES_KEY = "values"
    SUMS_KEY = "sums"
    CALCULATE_SUMS_KEY = "calculate sums"

    def __init__(self, calculate_sum = True, save_calculations = False):
        self.changes = dict()
        self.values = dict()
        self.sums = dict()
        self.not_calculated_changes = False
        self.calculate_sums = calculate_sum
        self.save_calculations = save_calculations
    
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
                if self.calculate_sums:
                    current_sum += value
                    self.sums[MonthDate(month, year)] = current_sum

    def to_json_object(self):
        json_dict = dict()
        json_dict[self.CHANGES_KEY] = serialize_dict(self.changes)
        json_dict[self.CALCULATE_SUMS_KEY] = self.calculate_sums
        if self.save_calculations:
            if self.not_calculated_changes:
                self.calculate_values()
            json_dict[self.VALUES_KEY] = serialize_dict(self.values)
            json_dict[self.SUMS_KEY] = serialize_dict(self.sums)
        return json_dict
    
    @classmethod
    def from_json_object(cls, json_object:dict):
        instance = cls()
        if json_object is not None:
            instance.changes = deserialize_to_dict(json_object[instance.CHANGES_KEY], key_cls=MonthDate)
            if instance.VALUES_KEY in json_object.keys():
                instance.values = deserialize_to_dict(json_object[instance.VALUES_KEY], key_cls=MonthDate)
            if instance.SUMS_KEY in json_object.keys():
                instance.sums = deserialize_to_dict(json_object[instance.SUMS_KEY], key_cls=MonthDate)
            instance.calculate_sums = json_object[instance.CALCULATE_SUMS_KEY]
            instance.save_calculations = instance.VALUES_KEY in json_object.keys()
        return instance
    
# a = ValuesOverTime()
# a.add_change(MonthDate.today(), 100)
# with open("tescik.json", "w") as file:
#     json.dump(a.to_json_serializable(with_calculated_values=True), file)
# with open("tescik.json", "r") as file:
#     b = ValuesOverTime.from_json_serializable(json.load(file))
#     print(b.changes)
#     print(b.values)
#     print(b.sums)