import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QFormLayout

from transakcje_manager import TransakcjeManager
from wyciąg import Transakcja
from podsumowanie_lokalu import PodsumowanieLokalu
from wspolnoty_widget import WspolnotyDropDownMenu

from wspolnoty_manager import wspolnoty_manager_singleton as wspolnoty_manager
from transakcje_manager import transakcje_manager_singleton as transakcje_manager

class CzynszeWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QFormLayout()
        main_layout = self.main_layout

        self.current_wspolnota = None
        self.current_lokal = -1

        self.wspolnota_dropdown_menu = WspolnotyDropDownMenu(wspolnoty_manager)
        main_layout.addRow("Wspólnota", self.wspolnota_dropdown_menu)
        self.wspolnota_dropdown_menu.add_event(self.on_wspolnota_change)

        self.lokal_dropdown_menu = QComboBox()
        main_layout.addRow("Lokal", self.lokal_dropdown_menu)
        self.lokal_dropdown_menu.currentTextChanged.connect(self.on_lokal_change)

        self.current_podsumowanie = None

        self.setLayout(main_layout)

    def on_wspolnota_change(self):
        self.current_wspolnota = wspolnoty_manager.wspolnota_by_name(self.wspolnota_dropdown_menu.currentText())
        self.current_lokal =  1
        self.lokal_dropdown_menu.addItems((str(i) for i in range(1, self.current_wspolnota.ilosc_mieszkan + 1)))
        self.lokal_dropdown_menu.setCurrentIndex(0)
    
    def on_lokal_change(self):
        self.current_lokal = int(self.lokal_dropdown_menu.currentText())
        if self.current_podsumowanie is not None:
            self.main_layout.removeWidget(self.current_podsumowanie)
        self.current_podsumowanie = PodsumowanieLokalu(self.current_wspolnota, self.current_lokal, transakcje_manager)
        self.main_layout.addWidget(self.current_podsumowanie)
    
    def show_update(self):
        if self.current_podsumowanie is not None:
            self.current_podsumowanie.update_everything()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = CzynszeWidget()
    demo.show()
    sys.exit(app.exec())