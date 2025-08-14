import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTabWidget
from wspolnoty_widget import WspolnotyWidget

#from transakcje_manager import transakcje_manager_singleton as transakcje_manager
#from wspolnoty_manager import wspolnoty_manager_singleton as wspolnoty_manager
from transakcje_widget import TransakcjeWidget
from czynsze_widget import CzynszeWidget

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1000, 500)
        
        main_layout = QVBoxLayout()

        self.tabs = QTabWidget(self)
        main_layout.addWidget(self.tabs)

        self.transakcje_widget = TransakcjeWidget()
        self.tabs.addTab(self.transakcje_widget, "Transakcje")

        self.wspolnoty_tab = WspolnotyWidget()
        self.tabs.addTab(self.wspolnoty_tab, "Wspólnoty")

        self.czynsze_tab = CzynszeWidget()
        self.tabs.addTab(self.czynsze_tab, "Czynsze")

        self.setLayout(main_layout)

        #self.tabs.currentChanged.connect(self.on_tab_changed)
    
    def on_tab_changed(self):
        self.tabs.currentWidget().show_update()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = MainApp()
    demo.show()
    sys.exit(app.exec())