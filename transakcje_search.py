import sys

from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLineEdit

from wspolnoty_widget import WspolnotyDropDownMenu
from wspolnoty_widget import LokalDropDownMenu

from transakcje_manager import Transakcja
from transakcje_manager import TransakcjeManager
from wspolnoty_manager import WspolnotyManager

from typing import Callable

class TransakcjeSearch(QWidget):
    def __init__(self, transakcje_manager : TransakcjeManager, wspolnoty_manager : WspolnotyManager):
        super().__init__()

        self.transakcje_manager = transakcje_manager
        transakcje_manager.on_transakcje_update.append(self.update_table)
        self.wspolnoty_manager = wspolnoty_manager

        self.years = list(range(2018, 2025 + 1))
        self.months = list(range(1, 12 + 1))

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.search_bar = QWidget()
        layout.addWidget(self.search_bar)

        search_bar_layout = QFormLayout()
        self.search_bar.setLayout(search_bar_layout)

        self.already_updating_table = True
        self.already_updating_transakcje = True

        self.search_rok_cb = QComboBox()
        self.search_rok_cb.currentTextChanged.connect(self.update_table)
        self.search_rok_cb.addItem("")
        self.search_rok_cb.addItems(str(year) for year in self.years)
        search_bar_layout.addRow("Rok", self.search_rok_cb)

        self.search_miesiac_cb = QComboBox()
        self.search_miesiac_cb.currentTextChanged.connect(self.update_table)
        self.search_miesiac_cb.addItem("")
        self.search_miesiac_cb.addItems(str(month) for month in self.months)
        search_bar_layout.addRow("Miesiąc", self.search_miesiac_cb)

        self.search_wspolnota_cb = WspolnotyDropDownMenu(wspolnoty_manager)
        self.search_wspolnota_cb.currentTextChanged.connect(self.update_table)
        search_bar_layout.addRow("Wspolnota", self.search_wspolnota_cb)

        self.search_lokal_cb = QComboBox()
        self.search_lokal_cb.currentTextChanged.connect(self.update_table)
        search_bar_layout.addRow("Lokal", self.search_lokal_cb)

        self.search_stan_cb = QComboBox()
        self.search_stan_cb.currentTextChanged.connect(self.update_table)
        self.search_stan_cb.addItems(["", "odrzucone", "poprawne", "do poprawy"])
        search_bar_layout.addRow("stan", self.search_stan_cb)

        self.search_numer_konta_le = QLineEdit()
        self.search_numer_konta_le.textChanged.connect(self.update_table)
        search_bar_layout.addRow("Numer konta", self.search_numer_konta_le)

        self.search_tekst_le = QLineEdit()
        self.search_tekst_le.textChanged.connect(self.update_table)
        search_bar_layout.addRow("Tekst", self.search_tekst_le)

        self.already_updating_table = False

        self.wspolnoty_widgets : dict[Transakcja, WspolnotyDropDownMenu] = dict()
        self.lokal_widgets : dict[Transakcja, LokalDropDownMenu] = dict()

        self.table = QTableWidget()
        layout.addWidget(self.table)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["rok", "miesiąc", "opis", "kwota", "wspolnota", "lokal", "stan", "", ""])
        self.already_updating_transakcje = False
        self.update_table()
        
    def update_search(self):
        self.already_updating_transakcje = True
        year = 0
        if self.search_rok_cb.currentText() != "":
            year = int(self.search_rok_cb.currentText())
        month = 0
        if self.search_miesiac_cb.currentText() != "":
            month = int(self.search_miesiac_cb.currentText())
        numer_konta = self.search_numer_konta_le.text()
        text = self.search_tekst_le.text()
        wspolnota = None
        if self.search_wspolnota_cb.currentText() != "":
            wspolnota = self.wspolnoty_manager.wspolnota_by_name(self.search_wspolnota_cb.currentText())
        lokal = 0
        if self.search_lokal_cb.currentText() != "":
            lokal = int(self.search_lokal_cb.currentText())
            if (wspolnota is not None) and (self.search_lokal_cb.count() == wspolnota.ilosc_mieszkan + 1):
                self.search_lokal_cb.clear()
                self.search_lokal_cb.addItem("")
                self.search_lokal_cb.addItems(str(i) for i in range(1, wspolnota.ilosc_mieszkan + 1))
                if lokal > wspolnota.ilosc_mieszkan:
                    self.search_lokal_cb.setCurrentText("")
                    lokal = 0
                else:
                    self.search_lokal_cb.setCurrentText(str(lokal))
        else:
            if wspolnota is not None:
                self.search_lokal_cb.clear()
                self.search_lokal_cb.addItem("")
                self.search_lokal_cb.addItems(str(i) for i in range(1, wspolnota.ilosc_mieszkan + 1))
        stan = ""
        if self.search_stan_cb.currentText() != "":
            stan = self.search_stan_cb.currentText()
        self.transakcje_wyszukane = self.transakcje_manager.search_transakcje(year=year, month=month, wspolnota=wspolnota, numer_lokalu=lokal, numer_konta=numer_konta, text=text)
        #print(self.transakcje_wyszukane)
        self.already_updating_transakcje = False

    def update_table(self):
        if self.already_updating_table:
            return
        self.already_updating_table = True
        self.update_search()
        self.already_updating_transakcje = True
        self.table.clear()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["rok", "miesiąc", "opis", "kwota", "wspolnota", "lokal", "stan", "", ""])
        self.table.setRowCount(len(self.transakcje_wyszukane))
        self.wspolnoty_widgets = dict()
        self.lokal_widgets = dict()
        for i, transakcja in enumerate(self.transakcje_wyszukane):
            self.table.setItem(i, 0, QTableWidgetItem(str(transakcja.year)))
            self.table.setItem(i, 1, QTableWidgetItem(str(transakcja.month)))
            self.table.setItem(i, 2, QTableWidgetItem(transakcja.text))
            self.table.setItem(i, 3, QTableWidgetItem(str(transakcja.kwota)))

            wspolnoty_drop_down_menu = WspolnotyDropDownMenu(self.wspolnoty_manager)
            self.wspolnoty_widgets[transakcja] = wspolnoty_drop_down_menu
            wspolnoty_drop_down_menu.set_wspolnota(transakcja.wspolnota)
            wspolnoty_drop_down_menu.add_event(self.update_transakcje)
            self.table.setCellWidget(i, 4, wspolnoty_drop_down_menu)

            lokal_drop_down_menu = LokalDropDownMenu(wspolnoty_drop_down_menu)
            self.lokal_widgets[transakcja] = lokal_drop_down_menu
            lokal_drop_down_menu.set_lokal(transakcja.lokal)
            lokal_drop_down_menu.add_event(self.update_transakcje)
            self.table.setCellWidget(i, 5, lokal_drop_down_menu)

            stan = ""
            if transakcja.odrzucone:
                stan = "odrzucone"
            else:
                if transakcja.zatwierdzone:
                    stan = "zatwierdzone"
                else:
                    stan = "do sprawdzenia"
            self.table.setItem(i, 6, QTableWidgetItem(stan))

            zatwierdz_button = TransakcjaButton(transakcja, self.zatwierdz, "Zatwierdź")
            self.table.setCellWidget(i, 7, zatwierdz_button)

            odrzuc_button = TransakcjaButton(transakcja, self.odrzuc, "Odrzuć")
            self.table.setCellWidget(i, 8, odrzuc_button)
        self.table.setColumnWidth(2, 500)
        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(2, 500)
        self.already_updating_table = False
        self.already_updating_transakcje = False
    
    def update_transakcje(self):
        if self.already_updating_transakcje:
            return
        self.already_updating_transakcje = True
        for transakcja in self.wspolnoty_widgets.keys():
            transakcja.wspolnota = self.wspolnoty_manager.wspolnota_by_name(self.wspolnoty_widgets[transakcja].currentText())
        for transakcja in self.lokal_widgets.keys():
            lokal_widget = self.lokal_widgets[transakcja]
            transakcja.lokal = lokal_widget.currentIndex()
            wspolnota = transakcja.wspolnota
            if (wspolnota is not None) and (wspolnota.ilosc_mieszkan != lokal_widget.count() + 1):
                lokal_widget.clear()
                lokal_widget.addItem("")
                for i in range(1, wspolnota.ilosc_mieszkan + 1):
                    lokal_widget.addItem(str(i))
                if wspolnota.ilosc_mieszkan >= transakcja.lokal:
                    lokal_widget.setCurrentIndex(transakcja.lokal)
        self.already_updating_transakcje = False
        self.transakcje_manager.save_transakcje()

    def zatwierdz(self, transakcja : Transakcja) -> None:
        if transakcja.zatwierdzone:
            return
        valid, reason = self.transakcje_manager.validate_transakcja(transakcja)
        if valid:
            self.transakcje_manager.zatwierdz_transakcje(transakcja)
            self.wspolnoty_widgets.pop(transakcja)
            self.lokal_widgets.pop(transakcja)
            self.update_table()
            self.transakcje_manager.save_transakcje()
        else:
            print(transakcja.text, reason)

    def odrzuc(self, transakcja : Transakcja) -> None:
        if transakcja.odrzucone:
            return
        print(transakcja.text)
        self.transakcje_manager.odrzuc_transakcje(transakcja)
        self.wspolnoty_widgets.pop(transakcja)
        self.lokal_widgets.pop(transakcja)
        self.update_table()
        self.transakcje_manager.save_transakcje()

class TransakcjaButton(QPushButton):
    def __init__(self, transakcja : Transakcja, func : Callable[[Transakcja], None], text = ""):
        super().__init__(text)
        self.transakcja = transakcja
        self.func = func
        self.clicked.connect(self.clicked_func)

    def clicked_func(self):
        self.func(self.transakcja)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wspolnoty_manager = WspolnotyManager()
    transakcje_manager = TransakcjeManager(wspolnoty_manager)
    demo = TransakcjeSearch(transakcje_manager, wspolnoty_manager)
    demo.show()
    sys.exit(app.exec())