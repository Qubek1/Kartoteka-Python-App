import sys
from PyQt5.QtWidgets import QApplication

import json
from datetime import date
from typing import Callable

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton

from wspolnoty_manager import Wspolnota
from wspolnoty_manager import WspolnotyManager
from wyciąg import Transakcja
from transakcje_manager import TransakcjeManager

class PodsumowanieLokalu(QWidget):
    def __init__(self, wspolnota : Wspolnota, numer_lokalu : int, transakcje_manager : TransakcjeManager):
        super().__init__()
        self.wspolnota = wspolnota
        self.numer_lokalu = numer_lokalu
        self.transakcje_manager = transakcje_manager
        self.resize(1000, 700)
        
        self.years = list(range(2018, 2025 + 1))
        self.months = list(range(1, 12 + 1))

        self.changes : dict[int, dict[int, float]] = dict()
        self.winien_dict : dict[int, dict[int, float]] = dict()
        self.wplacil_dict : dict[int, dict[int, float]] = dict()
        self.stan_na_dany_miesiac : dict[int, dict[int, float]] = dict()
        for year in self.years:
            self.changes[year] = dict()
            self.winien_dict[year] = dict()
            self.wplacil_dict[year] = dict()
            self.stan_na_dany_miesiac[year] = dict()
        self.load_changes()
        self.read_transakcje()
        self.update_values()

        self.form_layout = QFormLayout()
        self.setLayout(self.form_layout)

        self.stan_aktualny = QLineEdit(kwota_to_str(self.stan_na_dany_miesiac[date.today().year][date.today().month]))
        self.form_layout.addRow("Stan aktualny (" + str(date.today()) + "):", self.stan_aktualny)

        if numer_lokalu in wspolnota.numery_kont_bankowych.keys():
            self.numer_konta = wspolnota.numery_kont_bankowych[numer_lokalu]
        self.numer_konta_line_edit = QLineEdit(self.numer_konta)
        self.numer_konta_line_edit.textChanged.connect(self.change_numer_konta)
        self.form_layout.addRow("Numer konta bankowego:", self.numer_konta_line_edit)

        self.tworzenie_zmian = TworzenieZmianWidget()
        self.tworzenie_zmian.dodaj_button.clicked.connect(self.dodaj_zmiane)
        self.form_layout.addRow("Zmiana kwoty czynszu", self.tworzenie_zmian)

        self.wybor_roku = QComboBox()
        self.wybor_roku.addItems(str(year) for year in self.years)
        self.wybor_roku.currentTextChanged.connect(self.show_current_year)
        self.form_layout.addRow("Rok w tabelce: ", self.wybor_roku)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["data", "winien", "wpłacił", "stan na dany miesiąc"])
        self.form_layout.addWidget(self.table)
    
    def change_numer_konta(self):
        self.numer_konta = self.numer_konta_line_edit.text()
        self.wspolnota.add_numer_konta(self.numer_lokalu, self.numer_konta)

    def read_transakcje(self) -> None:
        self.wplacil_dict = dict()
        for year in self.years:
            self.wplacil_dict[year] = dict()
        transakcje = self.transakcje_manager.get_transakcje_lokalu(self.wspolnota, self.numer_lokalu)
        for transakcja in transakcje:
            month = transakcja.month
            year = transakcja.year
            if month in self.wplacil_dict[year]:
                self.wplacil_dict[year][month] += transakcja.kwota
            else:
                self.wplacil_dict[year][month] = transakcja.kwota

    def show_current_year(self) -> None:
        self.table.clear()
        self.table.setHorizontalHeaderLabels(["data", "winien", "wpłacił", "stan na dany miesiąc"])
        current_year = int(self.wybor_roku.currentText())
        self.table.setRowCount(12 + len(self.changes[current_year].keys()))
        self.table.setVerticalHeaderLabels([""] * (12 + len(self.changes[current_year].keys())))
        current_row = 0
        for month in self.months:
            if month in self.changes[current_year].keys():
                self.table.setItem(current_row, 1, QTableWidgetItem("zmiana na " + kwota_to_str(self.changes[current_year][month])))
                self.table.setCellWidget(current_row, 0, ZmianaButton(current_year, month, self.usun_zmiane))
                current_row += 1
            self.table.setItem(current_row, 0, QTableWidgetItem(month_to_str(month) + "." + str(current_year)))
            self.table.setItem(current_row, 1, QTableWidgetItem(kwota_to_str(self.winien_dict[current_year][month])))
            if month in self.wplacil_dict[current_year].keys():
                self.table.setItem(current_row, 2, QTableWidgetItem(kwota_to_str(self.wplacil_dict[current_year][month])))
            self.table.setItem(current_row, 3, QTableWidgetItem(kwota_to_str(self.stan_na_dany_miesiac[current_year][month])))
            current_row += 1
    
    def update_values(self):
        last_winien_value = 0
        stan_na_dany_miesiac_value = 0
        for year in self.years:
            for month in self.months:
                if month in self.changes[year].keys():
                    self.winien_dict[year][month] = self.changes[year][month]
                    last_winien_value = self.winien_dict[year][month]
                else:
                    self.winien_dict[year][month] = last_winien_value
                stan_na_dany_miesiac_value -= self.winien_dict[year][month]
                if month in self.wplacil_dict[year].keys():
                    stan_na_dany_miesiac_value += self.wplacil_dict[year][month]
                self.stan_na_dany_miesiac[year][month] = stan_na_dany_miesiac_value
    
    def update_stan_aktualny(self):
        self.stan_aktualny.setText(kwota_to_str(self.stan_na_dany_miesiac[date.today().year][date.today().month]))

    def update_everything(self):
        self.update_values()
        self.save_changes()
        self.show_current_year()
        self.update_stan_aktualny()

    def dodaj_zmiane(self):
        year = int(self.tworzenie_zmian.rok_text.text())
        month = int(self.tworzenie_zmian.miesiac_text.text())
        self.changes[year][month] = float(self.tworzenie_zmian.nowa_kwota.text())
        self.update_everything()

    def usun_zmiane(self, year : int, month : int):
        self.changes[year].pop(month)
        self.update_everything()
    
    def save_changes(self):
        with open("podsumowanie " + self.wspolnota.nazwa + " lokal nr. " + str(self.numer_lokalu) + ".json", "w") as file:
            json.dump({"zmiany": self.changes, "numer konta": self.numer_konta}, file)
            file.close()

    def load_changes(self):
        self.numer_konta = ""
        try:
            with open("podsumowanie " + self.wspolnota.nazwa + " lokal nr. " + str(self.numer_lokalu) + ".json", "r") as file:
                json_dictionary = json.load(file)
                self.numer_konta = json_dictionary["numer konta"]
                changes : dict[str, dict[str, int]] = json_dictionary["zmiany"]
                for year_in_str, dictionary in changes.items():
                    for month_in_str, value in dictionary.items():
                        self.changes[int(year_in_str)][int(month_in_str)] = value
                file.close()
        except FileNotFoundError:
            return
        except Exception as exception:
            raise exception

class ZmianaButton(QPushButton):
    def __init__(self, year : int, month : int, f : Callable[[int, int], None]):
        super().__init__("Usuń")
        self.month = month
        self.year = year
        self.f = f
        self.clicked.connect(self.on_click)
    
    def on_click(self):
        self.f(self.year, self.month)

class TworzenieZmianWidget(QWidget):
    def __init__(self):
        super().__init__()
        form_layout = QFormLayout()
        self.form_layout = form_layout

        self.miesiac_text = QLineEdit()
        form_layout.addRow("Miesiąc: ", self.miesiac_text)

        self.rok_text = QLineEdit()
        form_layout.addRow("Rok: ", self.rok_text)

        self.nowa_kwota = QLineEdit()
        form_layout.addRow("Nowa kwota: ", self.nowa_kwota)

        self.dodaj_button = QPushButton("Dodaj zmianę")
        form_layout.addWidget(self.dodaj_button)

        self.setLayout(form_layout)

def month_to_str(month : int) -> str:
    if month < 10:
        return "0" + str(month)
    return str(month)

def kwota_to_str(kwota : float) -> str:
    return '{:.2f}'.format(round(float(kwota), -2))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wspolnoty_manager = WspolnotyManager()
    transakcje_manager = TransakcjeManager(wspolnoty_manager)
    wspolnota = wspolnoty_manager.wspolnota_by_name("Gęsickiego")
    demo = PodsumowanieLokalu(wspolnota, 6, transakcje_manager)
    demo.update_values()
    demo.show_current_year()
    demo.show()
    sys.exit(app.exec())