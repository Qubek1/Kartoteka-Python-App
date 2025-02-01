from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QComboBox

import sys
from PyQt5.QtWidgets import QApplication

from wspolnoty_manager import Wspolnota
from wspolnoty_manager import WspolnotyManager

from typing import Callable

class WspolnotyWidget(QTabWidget):
    def __init__(self, wspolnoty_manager : WspolnotyManager):
        super().__init__()
        self.wspolnoty_manager = wspolnoty_manager
        
        self.podsumowanie_tab = QWidget()
        podsumowanie_tab_layout = QVBoxLayout()

        self.dodawanie_wspolnot_form = QWidget()
        dodawanie_wspolnot_form_layout = QFormLayout()
        self.dodawanie_wspolnoty_nazwa = QLineEdit()
        self.dodawanie_wspolnoty_ilosc = QLineEdit()
        self.dodawanie_wspolnoty_button = QPushButton("Dodaj nową wspólnotę")
        self.dodawanie_wspolnoty_button.clicked.connect(self.dodaj_nowa_wspolnote)
        dodawanie_wspolnot_form_layout.addRow("Nazwa wspólnoty (np. Gęsickiego)", self.dodawanie_wspolnoty_nazwa)
        dodawanie_wspolnot_form_layout.addRow("Ilość mieszkań", self.dodawanie_wspolnoty_ilosc)
        dodawanie_wspolnot_form_layout.addRow("", self.dodawanie_wspolnoty_button)
        self.dodawanie_wspolnot_form.setLayout(dodawanie_wspolnot_form_layout)
        podsumowanie_tab_layout.addWidget(self.dodawanie_wspolnot_form)

        self.podsumowanie_wszystkich_wspolnot = QTableWidget()
        self.podsumowanie_wszystkich_wspolnot.setColumnCount(2)
        self.podsumowanie_wszystkich_wspolnot.setRowCount(0)
        self.update_podsumowanie_table()
        self.podsumowanie_wszystkich_wspolnot.setHorizontalHeaderLabels(["Nazwa", "Ilość mieszkań"])

        podsumowanie_tab_layout.addWidget(self.podsumowanie_wszystkich_wspolnot)

        test = WspolnotyDropDownMenu(wspolnoty_manager)
        test.update_menu()
        podsumowanie_tab_layout.addWidget(test)
        test.add_event(lambda : print(test.currentText()))
        
        self.podsumowanie_tab.setLayout(podsumowanie_tab_layout)

        self.addTab(self.podsumowanie_tab, "Podsumowanie")
    
    def update_podsumowanie_table(self):
        self.podsumowanie_wszystkich_wspolnot.setRowCount(len(self.wspolnoty_manager.wspolnoty))
        for index, wspolnota in enumerate(self.wspolnoty_manager.wspolnoty):
            self.podsumowanie_wszystkich_wspolnot.setItem(index, 0, QTableWidgetItem(wspolnota.nazwa))
            self.podsumowanie_wszystkich_wspolnot.setItem(index, 1, QTableWidgetItem(str(wspolnota.ilosc_mieszkan)))

    def dodaj_nowa_wspolnote(self):
        self.wspolnoty_manager.dodaj_wspolnote(Wspolnota(self.dodawanie_wspolnoty_nazwa.text(), int(self.dodawanie_wspolnoty_ilosc.text())))
        self.update_podsumowanie_table()
        self.dodawanie_wspolnoty_nazwa.clear()
        self.dodawanie_wspolnoty_ilosc.clear()


class WspolnotyDropDownMenu(QComboBox):
    def __init__(self, wspolnoty_manager: WspolnotyManager):
        super().__init__()
        self.addItem("")
        self.wspolnoty_manager = wspolnoty_manager
        wspolnoty_manager.on_list_change_events.append(self.update_menu)
        self.update_menu()
    
    def update_menu(self):
        current_items : set[str] = set()
        items_to_remove : list[str] = []
        count = self.count()
        x = 0
        for i in range(1, count):
            current_items.add(self.itemText(i - x))
            if self.wspolnoty_manager.wspolnota_by_name(self.itemText(i - x)) is None:
                self.removeItem(i - x)
                x += 1
        for wspolnota in self.wspolnoty_manager.wspolnoty:
            if wspolnota.nazwa not in current_items:
                self.addItem(wspolnota.nazwa)

    def add_event(self, f : Callable[[], None]):
        self.currentTextChanged.connect(f)
    
class WspolnotaTabWidget(QTabWidget):
    def __init__(self, wspolnota:Wspolnota):
        self.wspolnota = wspolnota
        self.tabs : list[QWidget] = []
        for lokal in range(1, wspolnota.ilosc_mieszkan+1):
            lokal_tab = QWidget()
            self.addTab(lokal_tab, "lokal " + str(lokal))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wspolnoty_manager = WspolnotyManager()
    demo = WspolnotyWidget(wspolnoty_manager)
    demo.show()
    sys.exit(app.exec())