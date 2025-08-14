import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtGui import QFont

from wyciąg import Wyciąg
from wyciąg import Transakcja
from typing import List
from transakcje_extraction_from_pdf import extract_transakcje_from_pdf
from transakcje_manager import TransakcjeManager
from wspolnoty_manager import WspolnotyManager

class DashedBorderLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Przeciągnij pliki <b>.xml</b> i <b>.pdf</b> tutaj \n\n')
        self.setFont(QFont("Arial", 15))
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
        ''')

class DnDFiles(QWidget):
    def __init__(self, wspolnoty_manager: WspolnotyManager, transakcje_manager : TransakcjeManager):
        super().__init__()
        self.resize(400, 100)
        self.setAcceptDrops(True)
        self.wspolnoty_manager = wspolnoty_manager
        self.transakcje_manager = transakcje_manager

        mainLayout = QVBoxLayout()

        self.dashed_border_label = DashedBorderLabel()
        mainLayout.addWidget(self.dashed_border_label)

        self.setLayout(mainLayout)

        self.urls : List[str] = []
        self.wyciągi : List[Wyciąg] = []
        self.transakcje : List[Transakcja] = []
        self.on_drop_files_events : List[function] = []

    def dragEnterEvent(self, event):
        self.dashed_border_label.setStyleSheet('''
            QLabel{
            border: 4px dashed #333
            }
        ''')
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.dashed_border_label.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
        ''')

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            self.transakcje = []
            self.wyciągi = []
            event.setDropAction(Qt.CopyAction)
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                try:
                    if file_path[-4:] == '.xml':
                        if not url in self.urls:
                            self.urls.append(url)
                        self.wyciągi.append(Wyciąg(file_path, self.wspolnoty_manager))
                        self.transakcje.extend(self.wyciągi[-1].transakcje)
                    elif file_path[-4:] == '.pdf':
                        transakcje_list = extract_transakcje_from_pdf(file_path, self.wspolnoty_manager)
                        self.transakcje.extend(transakcje_list)
                    print(file_path + " działa")
                except Exception as e:
                    print(file_path + " nie udało się wszytać")

            event.accept()
            self.transakcje_manager.dodaj_transakcje(self.transakcje)
            for f in self.on_drop_files_events:
                f()
        else:
            event.ignore()
        self.dashed_border_label.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
        ''')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = DnDFiles()
    demo.show()
    sys.exit(app.exec())