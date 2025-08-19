from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QKeyEvent
from itertools import product
from typing import Callable

app = QtWidgets.QApplication([])

# wordlist for testing
wordlist = [''.join(combo) for combo in product('abc', repeat = 4)]
#wordlist = [str(i) for i in range(1, 100)]

class QBetterLineEdit(QtWidgets.QLineEdit):
    on_focus_in_event:Callable[[],None] = None
    on_focus_out_event:Callable[[],None] = None
    on_enter_click_event:Callable[[],None] = None
    on_esc_click_event:Callable[[],None] = None
    select_all_on_focus = True

    def focusInEvent(self, a0):
        if self.select_all_on_focus:
            self.single_shot_select_all()
        if self.on_focus_in_event is not None:
            self.on_focus_in_event()
        super().focusInEvent(a0)

    def focusOutEvent(self, a0):
        if self.on_focus_out_event is not None:
            self.on_focus_out_event()
        super().focusOutEvent(a0)

    def keyPressEvent(self, key_event:QKeyEvent):
        if key_event.key() == QtCore.Qt.Key.Key_Escape:
            if self.on_esc_click_event is not None:
                self.on_esc_click_event()
        elif key_event.key() == QtCore.Qt.Key.Key_Enter or key_event.key() == QtCore.Qt.Key.Key_Return:
            if self.on_enter_click_event is not None:
                self.on_enter_click_event()
        return super().keyPressEvent(key_event)

    def single_shot_select_all(self):
        QTimer.singleShot(0, self.selectAll)

    def single_shot_clear_focus(self):
        #QTimer.singleShot(0, lambda:self.setSelection(0, 0))
        QTimer.singleShot(0, self.clearFocus)

class QComboBoxSearcheable(QtWidgets.QComboBox):
    current_search = ""
    popup_opened = False
    unfiltered_items:list[str] = []
    current_selection = ""
    last_selection = ""

    def __init__(self, items:list[str] = [], start_item_text:str = None, start_item_index:int = None):
        super().__init__()
        self.dummy_keyboard_grabber_widget = QtWidgets.QWidget()
        better_line_edit = QBetterLineEdit()
        better_line_edit.on_focus_in_event = self._on_lineEdit_focus_in
        better_line_edit.on_enter_click_event = self._on_enter_press
        better_line_edit.on_esc_click_event = self._on_esc_press
        better_line_edit.textEdited.connect(self._on_text_edited)
        self.better_line_edit = better_line_edit
        self.setLineEdit(better_line_edit)
        #self.setCurrentText("abbb")
        #self.current_selection = "abbb"
        if items is not None:
            self.add_items(items)
            if start_item_text is not None:
                self.setCurrentText(start_item_text)
            elif start_item_index is not None:
                self.setCurrentIndex(start_item_index)

    def add_item(self, item:str):
        self.unfiltered_items.append(item)

    def add_items(self, items:list[str]):
        self.unfiltered_items.extend(items)

    def _on_lineEdit_focus_in(self):
        #print(self.popup_opened)
        if not self.popup_opened:
            self.better_line_edit.single_shot_select_all()
            self.clear()
            for item in self.unfiltered_items:
                self.addItem(item)
            self.showPopup()
            self.setCurrentText(self.current_selection)
            #QTimer.singleShot(0, lambda:self.setCurrentText(self.current_selection))
            self.last_selection = self.current_selection
            self.current_search = ""
            self.better_line_edit.grabKeyboard()
            #self.better_line_edit.grabMouse()
        else:
            self.better_line_edit.single_shot_clear_focus()
            self.dummy_keyboard_grabber_widget.grabKeyboard()
            QTimer.singleShot(0, self._commit_selection)
        self.popup_opened = not self.popup_opened

    def _on_enter_press(self):
        QTimer.singleShot(0, self.hidePopup)

    def _on_esc_press(self):
        self.current_selection = self.last_selection
        self.better_line_edit.setText(self.current_selection)
        QTimer.singleShot(0, self.hidePopup)

    def _commit_selection(self):
        if self.better_line_edit.text() not in self.unfiltered_items:
            self.current_selection = self.itemText(0)
            self.better_line_edit.setText(self.current_selection)
        else:
            self.current_selection = self.better_line_edit.text()

    def _on_text_edited(self):
        self.current_search = self.better_line_edit.text()
        #selection_start = self.better_line_edit.selectionStart()
        #selection_end = self.better_line_edit.selectionEnd()
        #print(selection_start, selection_end)
        self._update_items()
        self.better_line_edit.setText(self.current_search)
        # print(self.better_line_edit.cursor())
        # print(self.better_line_edit.cursor().shape())
        # print(self.better_line_edit.cursorPosition())
        #self.better_line_edit.setSelection(selection_start, selection_end)
        #self.better_line_edit.setSelection(1,1)
    
    def _update_items(self):
        self.clear()
        correct_items:list[str, int] = []
        for item in self.unfiltered_items:
            correct, first = str_is_in_str(self.current_search, item)
            if correct:
                correct_items.append((item, first))
        sorted_items = sorted(correct_items, key=lambda a: -a[1])
        for item in sorted_items:
            self.addItem(item[0])

def str_is_in_str(str1:str, str2:str) -> tuple[bool, int]:
    i = 0
    j = 0
    first = 100000
    while i < len(str1) and j < len(str2):
        if str1[i] == str2[j]:
            i+=1
        else:
            first = min(first, j)
        j+=1
    return i >= len(str1), first

if __name__ == "__main__":
    a = QtWidgets.QWidget()
    a.setLayout(QtWidgets.QVBoxLayout())

    combo = QtWidgets.QComboBox()#QComboBoxSearcheable()
    combo.addItems(wordlist)
    a.layout().addWidget(combo)

    combo2 = QComboBoxSearcheable()
    combo2.setEditable(True)
    combo2.add_items(wordlist)
    a.layout().addWidget(combo2)

    c = QBetterLineEdit()
    a.layout().addWidget(c)

    a.show()
    app.exec()