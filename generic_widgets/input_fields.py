from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QComboBox
from typing import Callable
from pynput import keyboard

class FloatInputField(QLineEdit):
    precision = 2
    non_negative = False
    accept_None_value = False
    value_range:tuple[float, float]|None = None
    _current_value:float|None = None
    _on_value_changed_event:Callable[[float], None] = None

    def __init__(self, start_value:float|None = None, non_negative = False, accept_None_value = False, precision = 2, value_range:tuple[float, float] = None):
        super().__init__()
        if (not accept_None_value) and (start_value is None):
            start_value = 0
        self.set_value(start_value)
        self.non_negative = non_negative
        self.accept_None_value = accept_None_value
        self.precision = precision
        self.value_range = value_range
        self.returnPressed.connect(self._commit_text)

    def get_value(self):
        return self._current_value

    def set_value(self, value:float):
        self._current_value = value
        self._update_text()
        if self._on_value_changed_event is not None:
            self._on_value_changed_event(value)

    def subscribe(self, callable:Callable[[float], None]):
        self._on_value_changed_event = callable

    def validate_value(self, value:float):
        if not((type(value) is float) or (type(value) is int)):
            return False 
        if (self.non_negative) and (value < 0):
            return False
        if (self.value_range is not None) and (self.value_range[0] > value or self.value_range[1] < value):
            return False
        return True

    def focusOutEvent(self, a0):
        self._commit_text()
        return super().focusOutEvent(a0)

    def _read_value_from_text(self) -> float:
        return str_to_float(self.text())

    def _commit_text(self):
        if self.accept_None_value and self.text() == "":
            if self._current_value is not None:
                self.set_value(None)
        else:
            value_from_text = self._read_value_from_text()
            if self.validate_value(value_from_text) and (not approximately_same(value_from_text, self._current_value, self.precision)):
                self.set_value(value_from_text)
            else:
                self._update_text()

    def _update_text(self):
        if self._current_value is None:
            self.setText("")
        else:
            self.setText(float_to_str(self._current_value, self.precision))


class IntInputField(QLineEdit):
    non_negative = False
    accept_None_value = False
    possible_values:list[int]|None = None
    _current_value:int|None = None
    _on_value_changed_event:Callable[[int|None], None] = None

    def __init__(self, start_value = None, non_negative = False, accept_None_value = False, possible_values:list[int] = None):
        super().__init__()
        if (not accept_None_value) and (start_value is None):
            start_value = 0
        self.set_value(start_value)
        self.non_negative = non_negative
        self.accept_None_value = accept_None_value
        self.possible_values = possible_values
        self.returnPressed.connect(self._commit_text)

    def get_value(self):
        return self._current_value

    def set_value(self, value:int|None):
        self._current_value = value
        self._update_text()
        if self._on_value_changed_event is not None:
            self._on_value_changed_event(value)

    def subscribe(self, callable:Callable[[int|None], None]):
        self._on_value_changed_event = callable

    def validate_value(self, value:int):
        if type(value) is not int:
            return False
        if (self.non_negative) and (value < 0):
            return False
        if (self.possible_values is not None) and (not value in self.possible_values):
            return False
        return True

    def focusOutEvent(self, a0):
        self._commit_text()
        return super().focusOutEvent(a0)
    
    def _read_value_from_text(self):
        return str_to_int(self.text())

    def _commit_text(self):
        if self.accept_None_value and self.text() == "":
            if self._current_value is not None:
                self.set_value(None)
        else:
            value_from_text = self._read_value_from_text()
            if (self.validate_value(value_from_text)) and (value_from_text != self._current_value):
                self._current_value = value_from_text
                if self._on_value_changed_event is not None:
                    self._on_value_changed_event(self._current_value)
            else:
                self._update_text()

    def _update_text(self):
        if self._current_value is None:
            self.setText("")
        else:
            self.setText(str(self._current_value))


def approximately_same(value1:float, value2:float, precision:int) -> bool:
    if (value1 is None) or (value2 is None):
        return False
    return round(value1, precision) == round(value2, precision)

def str_to_float(str_value:str) -> float | None:
    s = ""
    found_decimal_point = False
    for c in str_value:
        if c.isdigit():
            s += c
        if not found_decimal_point and (c == "," or c == "."):
            s += '.'
            found_decimal_point = True
    try:
        value = float(s)
        return value
    except:
        return None
    
def str_to_int(str_value:str) -> int | None:
    s = ""
    for c in str_value:
        if c.isdigit():
            s+=c
    try:
        value = int(s)
        return value
    except:
        return None
    
def float_to_str(value:float, precision:int):
    return f"{round(value, precision):.{precision}f}"

class QComboBoxSearcheable(QComboBox):
    def __init__(self, parent = ...):
        super().__init__(parent)
    
    def focusInEvent(self, e):    
        print("start")
        return super().focusInEvent(e)

    def focusOutEvent(self, e):
        print("end")
        return super().focusOutEvent(e)
