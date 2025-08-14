import sys

from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QApplication

from wspolnoty_widget import WspolnotyDropDownMenu
from wspolnoty_widget import LokalDropDownMenu

from transakcje_manager import Transakcja
from transakcje_manager import TransakcjeManager
from wspolnoty_manager import WspolnotyManager

from typing import Callable

class TransakcjeOdrzucone(QTableWidget):
    def __init__(self, transakcje_manager : TransakcjeManager, wspolnoty_manager : WspolnotyManager):
        super().__init__()

        self.transakcje_manager = transakcje_manager
        self.wspolnoty_manager = wspolnoty_manager

        self.wspolnoty_widgets : dict[Transakcja, WspolnotyDropDownMenu] = dict()
        self.lokal_widgets : dict[Transakcja, LokalDropDownMenu] = dict()

        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["opis", "kwota", "wspolnota", "lokal", ""])
        self.already_updating_transakcje = False
        self.update_table()
        
    def update_table(self):
        self.setRowCount(len(self.transakcje_manager.transakcje_odrzucone.keys()))
        for i, transakcja in enumerate(self.transakcje_manager.transakcje_odrzucone.values()):
            self.setItem(i, 0, QTableWidgetItem(transakcja.text))
            self.setItem(i, 1, QTableWidgetItem(str(transakcja.kwota)))

            wspolnoty_drop_down_menu = WspolnotyDropDownMenu(self.wspolnoty_manager)
            self.wspolnoty_widgets[transakcja] = wspolnoty_drop_down_menu
            wspolnoty_drop_down_menu.set_wspolnota(transakcja.wspolnota)
            wspolnoty_drop_down_menu.add_event(self.update_transakcje)
            self.setCellWidget(i, 2, wspolnoty_drop_down_menu)

            lokal_drop_down_menu = LokalDropDownMenu(wspolnoty_drop_down_menu)
            self.lokal_widgets[transakcja] = lokal_drop_down_menu
            lokal_drop_down_menu.set_lokal(transakcja.lokal)
            lokal_drop_down_menu.add_event(self.update_transakcje)
            self.setCellWidget(i, 3, lokal_drop_down_menu)

            zatwierdz_button = TransakcjaButton(transakcja, self.zatwierdz, "Zatwierdź")
            self.setCellWidget(i, 4, zatwierdz_button)
        self.setColumnWidth(0, 500)
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        self.setColumnWidth(0, 500)
    
    def update_transakcje(self):
        if self.already_updating_transakcje:
            return
        self.already_updating_transakcje = True
        for transakcja in self.wspolnoty_widgets.keys():
            transakcja.wspolnota = self.wspolnoty_widgets[transakcja].get_wspolnota()
        for transakcja in self.lokal_widgets.keys():
            transakcja.lokal = self.lokal_widgets[transakcja].get_lokal()
        self.already_updating_transakcje = False
        self.transakcje_manager.save_transakcje()

    def zatwierdz(self, transakcja : Transakcja):
        valid, reason = self.transakcje_manager.validate_transakcja(transakcja)
        if valid:
            self.transakcje_manager.zatwierdz_transakcje(transakcja)
            self.wspolnoty_widgets.pop(transakcja)
            self.lokal_widgets.pop(transakcja)
            self.update_table()
            self.transakcje_manager.save_transakcje()
        else:
            print(transakcja.text, reason)

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
    demo = TransakcjeOdrzucone(transakcje_manager, wspolnoty_manager)
    demo.show()
    sys.exit(app.exec())