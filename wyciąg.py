import xml.etree.ElementTree as ET
from lokal_extraction import extract_lokal_from_text
import json
from wspolnoty_manager import WspolnotyManager
from wspolnoty_manager import Wspolnota

from datetime import datetime

class Wyciąg:
    def __init__(self, xml_file_path, wspolnoty_manager: WspolnotyManager):
        tree = ET.parse(xml_file_path)
        self.tree = tree

        root = tree.getroot()
        self.id = root[0][0][0].text
        
        self.transakcje : list[Transakcja] = []
        self.czynsze : list[Transakcja] = []

        for i in range(1, len(root[0])):
            stmt = root[0][i]
            self.date = find(stmt, "Id")

            print(self.date.text)

            
            for transakcja_tree in find_all(stmt, "Ntry"):
                new_transakcja = Transakcja(wspolnoty_manager, transakcja_tree)
                self.transakcje.append(new_transakcja)
                if new_transakcja.text.lower().find("czynsz") != -1:
                    self.czynsze.append(new_transakcja)
        for transakcja in self.transakcje:
            print(transakcja.text)
            if transakcja in self.czynsze:
                czynsz = transakcja
                print("lokal: " + str(extract_lokal_from_text(czynsz.text)))
                print("kwota: " + str(czynsz.kwota))
            else:
                print(find(transakcja.tree_node, "CdtDbtInd").text)


class Transakcja:
    def __init__(self, wspolnoty_manager: WspolnotyManager, tree_node: ET.Element = None, dictionary: dict = None):
        if tree_node is not None:
            self.tree_node = tree_node
            self.kwota : float = float(find(tree_node, "Amt").text)
            print(self.kwota)
            self.nm_text : str = ""
            if len(search(tree_node, "Nm")) > 0:
                self.nm_text : str = search(tree_node, "Nm")[0].text
            if self.nm_text is None:
                self.nm_text = ""
            self.ustrd_text : str = search(tree_node, "Ustrd")[0].text
            if self.ustrd_text is None:
                self.ustrd_text = ""
            self.text : str = self.nm_text + "\n" + self.ustrd_text
            self.przychodzące : bool = (find(tree_node, "CdtDbtInd").text == "CRDT")
            self.id : str = search(tree_node, "InstrId")[0].text
            print(self.id)
            date : str = find(tree_node, "BookgDt")[0].text
            self.year : int = int(date[0:4])
            self.month : int = int(date[5:7])
            self.day : int = int(date[8:10])
            self.lokal : int = extract_lokal_from_text(self.text)
            self.wspolnota : Wspolnota = wspolnoty_manager.find_wspolnota_in_text(self.text)
            self.poprawne : bool = False
            self.odrzucone : bool = False
            self.numer_konta : str = ""
            try:
                self.numer_konta = search(tree_node, "DbtrAcct")[0][0][0].text
            except Exception as e:
                print("nie udało się znaleźć konta bankowego")
                print(e)
        if dictionary is not None:
            self.id = dictionary["id"]
            self.kwota = dictionary["kwota"]
            self.text = dictionary["text"]
            self.przychodzące = dictionary["przychodzące"]
            self.lokal = dictionary["lokal"]
            self.poprawne = dictionary["poprawne"]
            self.wspolnota = wspolnoty_manager.wspolnota_by_name(dictionary["wspolnota"])
            self.odrzucone = dictionary["odrzucone"]
            self.year = dictionary["year"]
            self.month = dictionary["month"]
            self.day = dictionary["day"]
            self.numer_konta = dictionary["numer konta"]
        if self.przychodzące and ((self.wspolnota is None) or self.lokal == -1):
            if self.numer_konta in wspolnoty_manager.numery_kont_bankowych.keys():
                self.wspolnota, self.lokal = wspolnoty_manager.numery_kont_bankowych[self.numer_konta]
        
    def create_dict_for_json(self) -> dict:
        dictionary = {}
        dictionary["id"] = self.id
        dictionary["kwota"] = self.kwota
        dictionary["text"] = self.text
        dictionary["przychodzące"] = self.przychodzące
        dictionary["lokal"] = self.lokal
        if self.wspolnota is None:
            dictionary["wspolnota"] = ""
        else:
            dictionary["wspolnota"] = self.wspolnota.nazwa
        dictionary["poprawne"] = self.poprawne
        dictionary["odrzucone"] = self.odrzucone
        dictionary["year"] = self.year
        dictionary["month"] = self.month
        dictionary["day"] = self.day
        dictionary["numer konta"] = self.numer_konta
        return dictionary


def find(node:ET.Element, tag:str) -> ET.Element:
    for child in node:
        if tag_check(child, tag):
            return child
    
def find_all(node:ET.Element, tag:str) -> list[ET.Element]:
    result = []
    for child in node:
        if tag_check(child, tag):
            result.append(child)
    return result
    
def search(node:ET.Element, tag:str) -> list[ET.Element]:
    result = []
    for child in node:
        if tag_check(child, tag):
            result.append(child)
        else:
            result.extend(search(child, tag))
    return result
    
def tag_check(node:ET.Element, tag:str) -> bool:
    return node.tag[-len(tag):] == tag

def save_wyciąg(wyciąg:Wyciąg) -> None:
    with open(str(wyciąg.id) + ".json", 'w') as file:
        transakcje = []
        for transakcja in wyciąg.transakcje:
            transakcje.append(transakcja.create_dict_for_json())
        json.dump(transakcje, file)

def day_from_str(text : str) -> int:
    if text[0] == "0":
        return int(text[1])
    return int(text)

if __name__ == "__main__":
    wspolnoty_manager = WspolnotyManager()
    wyciąg = Wyciąg("12_24_3EFNF6_PL8216_0001_20250106201837.xml", wspolnoty_manager)
    save_wyciąg(wyciąg)