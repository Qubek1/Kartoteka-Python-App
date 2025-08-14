import sys

from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QApplication

from wspolnoty_widget import WspolnotyDropDownMenu
from wspolnoty_widget import LokalDropDownMenu

from transakcje_manager import Transakcja
from transakcje_manager import transakcje_manager_singleton as transakcje_manager
from wspolnoty_manager import wspolnoty_manager_singleton as wspolnoty_manager

from typing import Callable

class TransakcjeDoPoprawy(QTableWidget):
    def __init__(self):
        super().__init__()

        transakcje_manager.on_transakcje_update.append(self.update_table)

        self.wspolnoty_widgets : dict[Transakcja, WspolnotyDropDownMenu] = dict()
        self.lokal_widgets : dict[Transakcja, LokalDropDownMenu] = dict()

        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["opis", "kwota", "wspolnota", "lokal", "", ""])
        self.already_updating_transakcje = False
        self.update_table()
        
    def update_table(self):
        self.already_updating_transakcje = True
        self.wspolnoty_widgets = dict()
        self.lokal_widgets = dict()
        self.clear()
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["opis", "kwota", "wspolnota", "lokal", "", ""])
        self.setRowCount(len(transakcje_manager.transakcje_do_zatwierdzenia.keys()))
        for i, transakcja in enumerate(transakcje_manager.transakcje_do_zatwierdzenia.values()):
            self.setItem(i, 0, QTableWidgetItem(transakcja.text))
            self.setItem(i, 1, QTableWidgetItem(str(transakcja.kwota)))

            wspolnoty_drop_down_menu = WspolnotyDropDownMenu()
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

            odrzuc_button = TransakcjaButton(transakcja, self.odrzuc, "Odrzuć")
            self.setCellWidget(i, 5, odrzuc_button)
        self.setColumnWidth(0, 500)
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        self.setColumnWidth(0, 500)
        self.already_updating_transakcje = False

    def update_transakcje(self):
        if self.already_updating_transakcje:
            return
        self.already_updating_transakcje = True
        for transakcja in self.wspolnoty_widgets.keys():
            transakcja.wspolnota = self.wspolnoty_widgets[transakcja].get_wspolnota()
        for transakcja in self.lokal_widgets.keys():
            lokal_widget = self.lokal_widgets[transakcja]
            lokal_widget.update()
            transakcja.lokal = lokal_widget.get_lokal()
        self.already_updating_transakcje = False
        transakcje_manager.save_transakcje()

    def zatwierdz(self, transakcja : Transakcja):
        valid, reason = transakcje_manager.validate_transakcja(transakcja)
        if valid:
            transakcje_manager.zatwierdz_transakcje(transakcja)
            self.wspolnoty_widgets.pop(transakcja)
            self.lokal_widgets.pop(transakcja)
            self.update_table()
            transakcje_manager.save_transakcje()
        else:
            print(transakcja.text, reason)

    def odrzuc(self, transakcja : Transakcja):
        print(transakcja.lokal)
        print(transakcja.text)
        transakcje_manager.odrzuc_transakcje(transakcja)
        self.wspolnoty_widgets.pop(transakcja)
        self.lokal_widgets.pop(transakcja)
        self.update_table()
        transakcje_manager.save_transakcje()

class TableRow():
    def __init__(self, 
                 row_index: int, 
                 transakcja: Transakcja, 
                 table: QTableWidget, 
                 update_table_func: Callable[[int],None]):
        
        self.row_index = row_index
        self.transakcja = transakcja
        self.table = table
        self.update_table_func = update_table_func
        table.setItem(row_index, 0, QTableWidgetItem(transakcja.text))
        table.setItem(row_index, 1, QTableWidgetItem(str(transakcja.kwota)))

        self.wspolnoty_drop_down_menu = WspolnotyDropDownMenu(wspolnoty_manager)
        self.wspolnoty_drop_down_menu.set_wspolnota(transakcja.wspolnota)
        self.wspolnoty_drop_down_menu.add_event(self.update)
        table.setCellWidget(row_index, 2, self.wspolnoty_drop_down_menu)

        self.lokal_drop_down_menu = LokalDropDownMenu(self.wspolnoty_drop_down_menu)
        self.lokal_drop_down_menu.set_lokal(transakcja.lokal)
        self.lokal_drop_down_menu.add_event(self.update)
        table.setCellWidget(row_index, 3, self.lokal_drop_down_menu)

        zatwierdz_button = TransakcjaButton(transakcja, self.zatwierdz, "Zatwierdź")
        table.setCellWidget(row_index, 4, zatwierdz_button)

        odrzuc_button = TransakcjaButton(transakcja, self.odrzuc, "Odrzuć")
        table.setCellWidget(row_index, 5, odrzuc_button)
    
    def zatwierdz(self):
        if self.lokal_drop_down_menu.is_valid():
            self.transakcja.lokal = self.lokal_drop_down_menu.get_lokal()
        if self.wspolnoty_drop_down_menu.is_valid():
            self.transakcja.wspolnota = self.wspolnoty_drop_down_menu.get_wspolnota()
        valid, reason = transakcje_manager.zatwierdz_transakcje(self.transakcja)
        if valid:
            self.table.removeRow(self.row_index)
            self.transakcja.zatwierdzone = True
        else:
            print(reason)
    
    def odrzuc(self):
        self.transakcja.odrzucone = True
        self.table.removeRow(self.row_index)

    def update(self):
        self.transakcja.wspolnota = self.wspolnoty_drop_down_menu.get_wspolnota()
        self.transakcja.lokal = self.lokal_drop_down_menu.get_lokal()
        transakcje_manager.save_transakcje()
        self.update_table_func(self.row_index)

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
    demo = TransakcjeDoPoprawy()
    demo.show()
    sys.exit(app.exec())