import sys

from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QVBoxLayout

from transakcje_do_poprawy import TransakcjeDoPoprawy
from transakcje_odrzucone import TransakcjeOdrzucone
from transakcje_search import TransakcjeSearch
from DnDFiles import DnDFiles

from transakcje_manager import transakcje_manager_singleton as transakcje_manager
from wspolnoty_manager import wspolnoty_manager_singleton as wspolnoty_manager

class TransakcjeWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())

        self.tabs = QTabWidget(self)

        self.transakcje_do_poprawy_tab = TransakcjeDoPoprawy(transakcje_manager, wspolnoty_manager)
        self.tabs.addTab(self.transakcje_do_poprawy_tab, "Transakcje do poprawy")

        self.transakcje_odrzucone_tab = TransakcjeOdrzucone(transakcje_manager, wspolnoty_manager)
        self.tabs.addTab(self.transakcje_odrzucone_tab, "Transakcje odrzucone")
        
        self.transakcje_wyszukiwanie = TransakcjeSearch(transakcje_manager, wspolnoty_manager)
        self.tabs.addTab(self.transakcje_wyszukiwanie, "Wyszukiwanie")

        self.tabs.currentChanged.connect(self.update_tables)

        self.layout().addWidget(self.tabs)

        self.dnd_files = DnDFiles(wspolnoty_manager, transakcje_manager)
        self.dnd_files.on_drop_files_events.append(self.on_drop_files)
        self.layout().addWidget(self.dnd_files)

        # self.transakcje_odrzucone = 
        # self.tabs.addTab(self.transakcje_odrzucone, "Transakcje odrzucone")

    def update_tables(self):
        self.transakcje_do_poprawy_tab.update_table()
        self.transakcje_odrzucone_tab.update_table()

    def on_drop_files(self):
        transakcje_manager.save_transakcje()
        self.transakcje_do_poprawy_tab.update_table()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     wspolnoty_manager = WspolnotyManager()
#     transakcje_manager = TransakcjeManager(wspolnoty_manager)
#     demo = TransakcjeWidget(transakcje_manager, wspolnoty_manager)
#     demo.show()
#     sys.exit(app.exec())