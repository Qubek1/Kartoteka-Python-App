import datetime

class ValuesOverTime():
    def __init__(self):
        self.changes: dict[(int, int), float] = dict()
        self.values: dict[(int, int), float] = dict()
        self.first_year = 2000
    
    def add_change(self, month:int, year:int, value:float) -> None:
        self.changes[(month, year)] = value

    def remove_change(self, month:int, year:int) -> None:
        self.add_change(month, year, 0)

    def get_value_after_calculations(self, month:int, year:int) -> float:
        return self.values[(month, year)]

    def get_sum_after_calculations(self, month:int, year:int) -> float:
        current_sum = 0
        for year_i in range(self.first_year, year+1):
            if year_i == year:
                last_month = month
            else:
                last_month = 12
            for month_i in range(1, last_month+1):
                current_sum += self.values[(month_i, year_i)]
        return current_sum

    def calculate_values(self) -> None:
        value = 0
        for year in range(self.first_year, datetime.date.today().year+1):
            for month in range(1, 12+1):
                if (month, year) in self.changes.keys():
                    value = self.changes[(month, year)]
                self.values[(month, year)] = value


class Oplata():
    def __init__(self, name:str, na_co:str):
        self.name = name
        self.na_co = na_co
        self.values_over_time = ValuesOverTime()

    def get_table_header_text(self) -> str:
        return f"zł na {self.na_co}"

    def get_text_after_calculations(self, month:int, year:int) -> str:
        value = self.values_over_time.get_value_after_calculations(month, year)
        return f"{value} na {self.na_co}"

    def calculate_values(self) -> None:
        self.values_over_time.calculate_values()
    
    def add_change(self, month:int, year:int, value:float) -> None:
        self.values_over_time.add_change(month, year, value)

    def remove_change(self, month:int, year:int) -> None:
        self.values_over_time.remove_change(month, year)


class FunduszChange():
    def __init__(self, oplata:Oplata, lokal:int, month:int, year:int, new_value:float):
        self.oplata = oplata
        self.lokal = lokal
        self.month = month
        self.year = year
        self.new_value = new_value


class Fundusz():
    def __init__(self, name:str, lokale:list[int]):
        self.name = name
        self.lokale = lokale
        #change per oplata and lokal
        self.values_dict:dict[(Oplata, int), ValuesOverTime] = dict()
        self.changes_list:list[FunduszChange] = []
        self.wydatki:list[float] = []
        self.oplaty:list[Oplata] = []

    def add_new_oplata(self, oplata:Oplata) -> None:
        self.oplaty.append(oplata)

    def add_new_wydatek(self, value:float) -> None:
        self.wydatki.append(value)

    def add_new_change(self, fundusz_change:FunduszChange) -> None:
        self.changes_list.append(fundusz_change)
        self.values_dict[(fundusz_change.oplata, fundusz_change.lokal)].add_change(fundusz_change.month, fundusz_change.year, fundusz_change.new_value)

    def calculate_values(self) -> None:
        for oplata in self.oplaty:
            for lokal in self.lokale:
                self.values_dict[(oplata, lokal)].calculate_values()

    def get_value_after_calculations(self, oplata:Oplata, lokal:int, month:int, year:int) -> float:
        return self.values_dict[(oplata, lokal)].get_value_after_calculations(month, year)

    def get_current_sum_after_calculations(self) -> float:
        current_sum = 0
        for oplata in self.oplaty:
            for lokal in self.lokale:
                today = datetime.date.today()
                month = today.month
                year = today.year
                current_sum += self.values_dict[(oplata, lokal)].get_value_after_calculations(month, year)
        return current_sum