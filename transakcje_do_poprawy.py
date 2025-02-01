import sys

from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QApplication

from wspolnoty import WspolnotyDropDownMenu

from transakcje_manager import Transakcja
from transakcje_manager import TransakcjeManager
from wspolnoty_manager import WspolnotyManager

from typing import Callable

class TransakcjeDoPoprawy(QTableWidget):
    def __init__(self, transakcje_manager : TransakcjeManager, wspolnoty_manager : WspolnotyManager):
        super().__init__()

        self.transakcje_manager = transakcje_manager
        self.wspolnoty_manager = wspolnoty_manager

        self.wspolnoty_widgets : dict[Transakcja, WspolnotyDropDownMenu] = dict()
        self.lokal_widgets : dict[Transakcja, QComboBox] = dict()

        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["opis", "kwota", "wspolnota", "lokal", "zatwierdź", "odrzuć"])
        self.already_updating_transakcje = False
        self.update_table()
        
    def update_table(self):
        self.setRowCount(len(self.transakcje_manager.transakcje_do_poprawienia.keys()))
        for i, transakcja in enumerate(self.transakcje_manager.transakcje_do_poprawienia.values()):
            self.setItem(i, 0, QTableWidgetItem(transakcja.text))
            self.setItem(i, 1, QTableWidgetItem(str(transakcja.kwota)))

            wspolnoty_widget = WspolnotyDropDownMenu(self.wspolnoty_manager)
            self.wspolnoty_widgets[transakcja] = wspolnoty_widget
            wspolnoty_widget.currentTextChanged.connect(self.update_transakcje)
            wspolnota = transakcja.wspolnota
            if wspolnota is not None:
                wspolnoty_widget.setCurrentText(transakcja.wspolnota.nazwa)
            self.setCellWidget(i, 2, wspolnoty_widget)

            lokal_widget = QComboBox()
            self.lokal_widgets[transakcja] = lokal_widget
            lokal_widget.currentTextChanged.connect(self.update_transakcje)
            lokal_widget.addItem("")
            if wspolnota is not None:
                lokal_widget.addItems(str(i) for i in range(1, wspolnota.ilosc_mieszkan + 1))
            if transakcja.lokal != -1:
                lokal_widget.currentText = str(transakcja.lokal)
            self.setCellWidget(i, 3, lokal_widget)

            zatwierdz_button = TransakcjaButton(transakcja, self.zatwierdz)
            self.setCellWidget(i, 4, zatwierdz_button)

            odrzuc_button = TransakcjaButton(transakcja, self.odrzuc)
            self.setCellWidget(i, 5, odrzuc_button)
        self.setColumnWidth(0, 500)
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
        self.setColumnWidth(0, 500)
    
    def update_transakcje(self):
        if self.already_updating_transakcje:
            return
        self.already_updating_transakcje = True
        for transakcja in self.wspolnoty_widgets.keys():
            transakcja.wspolnota = wspolnoty_manager.wspolnota_by_name(self.wspolnoty_widgets[transakcja].currentText())
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

    def zatwierdz(self, transakcja : Transakcja):
        valid, reason = transakcje_manager.validate_transakcja(transakcja)
        if valid:
            self.transakcje_manager.revalidate_transakcja(transakcja)
            self.wspolnoty_widgets.pop(transakcja)
            self.lokal_widgets.pop(transakcja)
            self.update_table()
            self.transakcje_manager.save_transakcje()
        else:
            print(transakcja.text, reason)

    def odrzuc(self, transakcja : Transakcja):
        print(transakcja.text)
        self.transakcje_manager.odrzuc_transakcje(transakcja)
        self.wspolnoty_widgets.pop(transakcja)
        self.lokal_widgets.pop(transakcja)
        self.update_table()
        self.transakcje_manager.save_transakcje()

class TransakcjaButton(QPushButton):
    def __init__(self, transakcja : Transakcja, func : Callable[[Transakcja], None]):
        super().__init__()
        self.transakcja = transakcja
        self.func = func
        self.clicked.connect(self.clicked_func)

    def clicked_func(self):
        self.func(self.transakcja)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wspolnoty_manager = WspolnotyManager()
    transakcje_manager = TransakcjeManager(wspolnoty_manager)
    demo = TransakcjeDoPoprawy(transakcje_manager, wspolnoty_manager)
    demo.show()
    sys.exit(app.exec())