import json
from typing import Callable

class Wspolnota:
    def __init__(self, nazwa = "", ilosc_mieszkan = 0, json_dict = None):
        self.nazwa : str = nazwa
        self.ilosc_mieszkan : int = ilosc_mieszkan
        self.numery_kont_bankowych : dict[int, str] = dict()
        self.on_add_numer_konta : list[Callable[[Wspolnota, int, str],None]] = []
        if json_dict is not None:
            self.load_json_dict(json_dict)

        self.functions_to_call : list[function] = []
    
    def create_json_dict(self):
        json_dictionary = dict()
        json_dictionary["nazwa"] = self.nazwa
        json_dictionary["ilosc mieszkan"] = self.ilosc_mieszkan
        json_dictionary["numery kont bankowych"] = self.numery_kont_bankowych
        return json_dictionary

    def load_json_dict(self, json_dict):
        self.nazwa = json_dict["nazwa"]
        self.ilosc_mieszkan = json_dict["ilosc mieszkan"]
        numery_kont_bankowych = json_dict["numery kont bankowych"]
        self.numery_kont_bankowych = {}
        for key, value in numery_kont_bankowych.items():
            self.numery_kont_bankowych[int(key)] = value

    def add_numer_konta(self, lokal: int, numer_konta: str):
        self.numery_kont_bankowych[lokal] = numer_konta
        for f in self.on_add_numer_konta:
            f(self, lokal, numer_konta)

class WspolnotyManager:
    def __init__(self):
        self.wspolnoty : list[Wspolnota] = []
        self.on_list_change_events : list[function] = []
        self.numery_kont_bankowych : dict[str, tuple[Wspolnota, int]] = dict()
        self.load_wspolnoty()

    def wspolnota_by_name(self, name : str) -> Wspolnota:
        for wspolnota in self.wspolnoty:
            if wspolnota.nazwa == name:
                return wspolnota
        return None
    
    def load_wspolnoty(self):
        try:
            with open("wspolnoty.json", "r") as file:
                array = json.load(file)
                for item in array:
                    wspolnota = Wspolnota(json_dict=item)
                    wspolnota.on_add_numer_konta.append(self.add_numer_konta_bankowego)
                    self.wspolnoty.append(wspolnota)
                    for lokal, numer_konta in wspolnota.numery_kont_bankowych.items():
                        self.numery_kont_bankowych[numer_konta] = (wspolnota, lokal)
        except FileNotFoundError:
            return
        except Exception as e:
            raise e
        
    def save_wspolnoty(self):
        with open("wspolnoty.json", "w") as file:
            array = []
            for wspolnota in self.wspolnoty:
                array.append(wspolnota.create_json_dict())
            json.dump(array, file)

    def dodaj_wspolnote(self, wspolnota : Wspolnota):
        self.wspolnoty.append(wspolnota)
        self.save_wspolnoty()
        for f in self.on_list_change_events:
            f()
    
    def usun_wspolnote(self, wspolnota : Wspolnota):
        self.wspolnoty.remove(wspolnota)
        self.save_wspolnoty()
        for f in self.on_list_change_events:
            f()
    
    def find_wspolnota_in_text(self, text : str) -> Wspolnota:
        for wspolnota in self.wspolnoty:
            index = text.lower().find(wspolnota.nazwa.lower())
            if index != -1:
                return wspolnota
        return None

    def add_numer_konta_bankowego(self, wspolnota: Wspolnota, lokal: int, numer_konta: str):
        self.numery_kont_bankowych[numer_konta] = (wspolnota, lokal)
        self.save_wspolnoty()