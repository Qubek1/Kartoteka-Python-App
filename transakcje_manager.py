from wyciąg import Wyciąg
from wyciąg import Transakcja
from wspolnoty import Wspolnota
from wspolnoty_manager import WspolnotyManager

import json

class TransakcjeManager:
    def __init__(self, wspolnoty_manager : WspolnotyManager):
        #key -> id transakcji, value -> obiekt transakcji
        self.transakcje : dict[str, Transakcja] = {}
        self.poprawne_transakcje : dict[str, Transakcja] = {}
        self.transakcje_do_poprawienia : dict[str, Transakcja] = {}
        self.transakcje_odrzucone : dict[str, Transakcja] = {}
        self.wspolnoty_manager = wspolnoty_manager
        self.load_transakcje()

    def dodaj_transakcje(self, lista_transakcji : list[Transakcja]):
        for transakcja in lista_transakcji:
            if not transakcja.przychodzące:
                continue
            if transakcja.id in self.transakcje.keys():
                continue
            self.transakcje[transakcja.id] = transakcja
            valid, reason = self.validate_transakcja(transakcja)
            if not valid:
                print(transakcja.id + " " + reason)
                self.transakcje_do_poprawienia[transakcja.id] = transakcja
            else:
                self.poprawne_transakcje[transakcja.id] = transakcja
    
    def load_transakcje(self) -> None:
        try:
            with open("transakcje.json", 'r') as file:
                saved_list = json.load(file)
                for transakcja_in_json in saved_list:
                    transakcja = Transakcja(self.wspolnoty_manager, dictionary=transakcja_in_json)
                    self.dodaj_transakcje([transakcja])
        except FileNotFoundError:
            self.transakcje = {}
        except Exception as e:
            print(e)
            raise e

    def save_transakcje(self) -> None:
        with open("transakcje.json", "w") as file:
            transakcje_lista = []
            for transakcja in self.transakcje.values():
                transakcje_lista.append(transakcja.create_dict_for_json())
            json.dump(transakcje_lista, file)

    def revalidate_transakcja(self, transakcja : Transakcja) -> None:
        if self.validate_transakcja(transakcja)[0]:
            self.transakcje_do_poprawienia.pop(transakcja.id)
            self.poprawne_transakcje[transakcja.id] = transakcja
            transakcja.poprawne = True

    def validate_transakcja(self, transakcja : Transakcja) -> tuple[bool, str]:
        if transakcja.wspolnota is None:
            return (False, "nie znaleziono wspolnoty")
        if transakcja.wspolnota.ilosc_mieszkan < transakcja.lokal or transakcja.lokal <= 0:
            return (False, "nie ma takiego lokalu w danej wspólnocie")
        transakcja.poprawne = True
        return (True, "")
    
    def odrzuc_transakcje(self, transakcja : Transakcja) -> None:
        self.transakcje_do_poprawienia.pop(transakcja.id)
        self.transakcje_odrzucone[transakcja.id] = transakcja
        transakcja.poprawne = False
        transakcja.odrzucone = True
    
    def przywroc_transakcje(self, transakcja : Transakcja) -> None:
        self.transakcje_odrzucone.pop(transakcja.id)
        self.transakcje_do_poprawienia[transakcja.id] = transakcja
        transakcja.odrzucone = False
    
    def get_transakcje_lokalu(self, wspolnota : Wspolnota, nr_lokalu : int) -> list[Transakcja]:
        ret : list[Transakcja] = []
        for transakcja in self.poprawne_transakcje.values():
            if transakcja.wspolnota == wspolnota and transakcja.lokal == nr_lokalu:
                ret.append(transakcja)
        return ret