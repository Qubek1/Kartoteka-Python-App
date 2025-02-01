import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from DnDFiles import DnDFiles
from wspolnoty import WspolnotyWidget

from transakcje_manager import TransakcjeManager
from wyciąg import Transakcja
from wspolnoty_manager import WspolnotyManager

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1000, 500)
        
        main_layout = QVBoxLayout()

        self.tabs = QTabWidget(self)
        main_layout.addWidget(self.tabs)

        self.wspolnoty_manager = WspolnotyManager()
        self.transakcje_manager = TransakcjeManager(self.wspolnoty_manager)

        self.createTables()
        self.transakcje_tabs = QTabWidget(self.tabs)
        self.transakcje_tabs.addTab(self.tableWidget, "Transakcje Przychodzące")
        self.transakcje_tabs.addTab(self.failed_transactions_table, "Do Ręcznego Poprawienia")
        self.tabs.addTab(self.transakcje_tabs, "Transakcje")

        self.wspolnoty_tab = QTabWidget(self.tabs)
        self.wspolnoty_podsumowanie = WspolnotyWidget(self.wspolnoty_manager)

        self.wspolnoty_tab.addTab(self.wspolnoty_podsumowanie, "Podsumowanie")
        self.tabs.addTab(self.wspolnoty_tab, "Wspólnoty")

        self.dnd_files = DnDFiles(self, self.wspolnoty_manager)
        self.dnd_files.on_drop_files_events.append(self.on_drop_files_event)
        main_layout.addWidget(self.dnd_files)

        self.setLayout(main_layout)

    # def on_drop_files_event(self):
    #     wyciąg = self.dnd_files.wyciągi[0]
    #     self.tableWidget.setRowCount(len(wyciąg.transakcje))
    #     self.tableWidget.setHorizontalHeaderLabels(["przychodzące", "opis", "lokal", "kwota"])
        
    #     for index, transakcja in enumerate(wyciąg.transakcje):
    #         if transakcja.przychodzące:
    #             self.tableWidget.setItem(index, 0, QTableWidgetItem("przychodzące"))
    #         else:
    #             self.tableWidget.setItem(index, 0, QTableWidgetItem("wychodzące"))
    #         self.tableWidget.setItem(index, 1, QTableWidgetItem(transakcja.text))
    #         self.tableWidget.setItem(index, 2, QTableWidgetItem(str(transakcja.lokal)))
    #         self.tableWidget.setItem(index, 3, QTableWidgetItem(str(transakcja.kwota)))
    #     self.tableWidget.resizeRowsToContents()
    #     self.tableWidget.resizeColumnsToContents()

    #     self.transakcje_manager.dodaj_transakcje(wyciąg.transakcje)
    #     self.transakcje_manager.save_transakcje()

    def on_drop_files_event(self):
        dodane_transakcje = self.dnd_files.transakcje
        self.transakcje_manager.dodaj_transakcje(dodane_transakcje)
        self.transakcje_manager.save_transakcje()

        self.tableWidget.setRowCount(len(dodane_transakcje))
        self.tableWidget.setHorizontalHeaderLabels(["przychodzące", "opis", "lokal", "kwota"])
        for index, transakcja in enumerate(dodane_transakcje):
            if transakcja.przychodzące:
                self.tableWidget.setItem(index, 0, QTableWidgetItem("przychodzące"))
            else:
                self.tableWidget.setItem(index, 0, QTableWidgetItem("wychodzące"))
            self.tableWidget.setItem(index, 1, QTableWidgetItem(transakcja.text))
            self.tableWidget.setItem(index, 2, QTableWidgetItem(str(transakcja.lokal)))
            self.tableWidget.setItem(index, 3, QTableWidgetItem(str(transakcja.kwota)))
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnsToContents()

    def createTables(self): 
        self.tableWidget = QTableWidget() 
        #Column count 
        self.tableWidget.setColumnCount(4)

        self.tableWidget.setRowCount(0)
   
        #Table will fit the screen horizontally 
        self.tableWidget.horizontalHeader().setStretchLastSection(True) 
        self.tableWidget.horizontalHeader().setSectionResizeMode( 
            QHeaderView.Stretch) 
        
        self.failed_transactions_table = QTableWidget()

        self.failed_transactions_table.setColumnCount(4)
        self.failed_transactions_table.setRowCount(0)
        self.failed_transactions_table.horizontalHeader().setStretchLastSection(True) 
        self.failed_transactions_table.horizontalHeader().setSectionResizeMode( 
            QHeaderView.Stretch) 

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = MainApp()
    demo.show()
    sys.exit(app.exec())