from wyciąg import Wyciąg
from wyciąg import Transakcja
from wspolnoty_manager import Wspolnota
from wspolnoty_manager import WspolnotyManager
from wspolnoty_manager import wspolnoty_manager_singleton as wspolnoty_manager

import json

class TransakcjeManager:
    def __init__(self):
        #key -> id transakcji, value -> obiekt transakcji
        self.transakcje : dict[str, Transakcja] = {}
        self.zatwierdzone_transakcje : dict[str, Transakcja] = {}
        self.transakcje_do_zatwierdzenia : dict[str, Transakcja] = {}
        self.transakcje_odrzucone : dict[str, Transakcja] = {}
        self.on_transakcje_update : list[function] = []
        self.load_transakcje()

    def dodaj_transakcje(self, lista_transakcji : list[Transakcja]):
        for transakcja in lista_transakcji:
            if not transakcja.przychodzące:
                continue
            if transakcja.id in self.transakcje.keys():
                continue
            self.transakcje[transakcja.id] = transakcja
            if transakcja.odrzucone:
                self.transakcje_odrzucone[transakcja.id] = transakcja
            elif transakcja.zatwierdzone:
                self.zatwierdzone_transakcje[transakcja.id] = transakcja
            else:
                self.transakcje_do_zatwierdzenia[transakcja.id] = transakcja
    
    def load_transakcje(self) -> None:
        try:
            with open("transakcje.json", 'r') as file:
                saved_list = json.load(file)
                for transakcja_in_json in saved_list:
                    transakcja = Transakcja(wspolnoty_manager, dictionary=transakcja_in_json)
                    #print(transakcja_in_json["lokal"])
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

    def zatwierdz_transakcje(self, transakcja : Transakcja) -> tuple[bool, str]:
        valid, reason = self.validate_transakcja(transakcja)
        if not valid:
            return (valid, reason)
        if transakcja in self.transakcje_do_zatwierdzenia:
            self.transakcje_do_zatwierdzenia.pop(transakcja.id)
        if transakcja in self.transakcje_odrzucone:
            self.transakcje_odrzucone.pop(transakcja.id)
        self.zatwierdzone_transakcje[transakcja.id] = transakcja
        transakcja.poprawne = True
        transakcja.zatwierdzone = True
        return (True, "")

    def validate_transakcja(self, transakcja : Transakcja) -> tuple[bool, str]:
        if transakcja.wspolnota is None:
            return (False, "nie znaleziono wspolnoty")
        if transakcja.wspolnota.ilosc_mieszkan < transakcja.lokal or transakcja.lokal <= 0:
            return (False, "nie ma takiego lokalu w danej wspólnocie")
        transakcja.poprawne = True
        return (True, "")
    
    def odrzuc_poprawna_transakcje(self, transakcja : Transakcja) -> None:
        self.zatwierdzone_transakcje.pop(transakcja.id)
        self.transakcje_odrzucone[transakcja.id] = transakcja
        transakcja.poprawne = False
        transakcja.zatwierdzone = False
        transakcja.odrzucone = True
        self.save_transakcje()

    def odrzuc_transakcje(self, transakcja : Transakcja) -> None:
        self.transakcje_do_zatwierdzenia.pop(transakcja.id)
        self.transakcje_odrzucone[transakcja.id] = transakcja
        transakcja.poprawne = False
        transakcja.zatwierdzone = False
        transakcja.odrzucone = True
        self.save_transakcje()
    
    def przywroc_transakcje(self, transakcja : Transakcja) -> None:
        self.transakcje_odrzucone.pop(transakcja.id)
        self.transakcje_do_zatwierdzenia[transakcja.id] = transakcja
        transakcja.odrzucone = False
    
    def get_transakcje_lokalu(self, wspolnota : Wspolnota, nr_lokalu : int) -> list[Transakcja]:
        ret : list[Transakcja] = []
        for transakcja in self.zatwierdzone_transakcje.values():
            if transakcja.wspolnota == wspolnota and transakcja.lokal == nr_lokalu:
                ret.append(transakcja)
        return ret
    
    def add_numer_bankowy(self, numer_bankowy: str):
        to_revalidate_list : list[Transakcja] = []
        for transakcja in self.transakcje_do_zatwierdzenia.values():
            if transakcja.numer_konta == "" and transakcja.text.find(numer_bankowy) != -1:
                transakcja.numer_konta = numer_bankowy
            if transakcja.numer_konta == numer_bankowy:
                transakcja.wspolnota, transakcja.lokal = wspolnoty_manager.numery_kont_bankowych[numer_bankowy]
                to_revalidate_list.append(transakcja)
        for transakcja in to_revalidate_list:
            self.zatwierdz_transakcje(transakcja)
        self.save_transakcje()
        for f in self.on_transakcje_update:
            f()
    
    def search_transakcje(self, wspolnota : Wspolnota = None, numer_lokalu = 0, year = 0, month = 0, numer_konta = "", text = "") -> list[Transakcja]:
        wyszukane_transakcje : list[Transakcja] = []
        for transakcja in self.transakcje.values():
            #if (transakcja.lokal != 0):
                #print(transakcja.lokal, numer_lokalu)
            if (wspolnota is not None) and (transakcja.wspolnota is not wspolnota):
                continue
            if (numer_lokalu != 0) and (transakcja.lokal != numer_lokalu):
                continue
            if (year != 0) and (transakcja.year != year):
                continue
            if (month != 0) and (transakcja.month != month):
                continue
            if (numer_konta != "") and (transakcja.numer_konta != numer_konta):
                continue
            if (text != "") and (transakcja.text.lower().find(text.lower()) == -1):
                continue
            wyszukane_transakcje.append(transakcja)
        return wyszukane_transakcje

transakcje_manager_singleton = TransakcjeManager()

#if __name__ == "__main__":
    #wm = WspolnotyManager()
    #tm = TransakcjeManager(wm)