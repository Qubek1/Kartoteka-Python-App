import pypdf
from wyciąg import Transakcja
from pathlib import Path
from lokal_extraction import extract_lokal_from_text
from wspolnoty_manager import WspolnotyManager

def extract_transakcje_from_pdf(file_name: Path, wspolnoty_manager : WspolnotyManager) -> list[Transakcja]:
    reader = pypdf.PdfReader(file_name)
    transakcje : list[Transakcja] = []
    if reader.pages[0].extract_text().lower().find("brak transakcji") != -1:
        return transakcje
    for page in reader.pages:
        text = page.extract_text()
        text = string_after_find(text, "Saldo po transakcji")
        text = text[1:]
        next_pln = text.find("PLN")
        if next_pln == -1:
            break
        while next_pln != -1:
            current_text = text[:next_pln]
            dictionary = {}
            dictionary["id"] = extract_id(current_text)
            kwota = extract_last_kwota(current_text)
            dictionary["kwota"] = abs(kwota)
            dictionary["text"] = current_text
            dictionary["przychodzące"] = kwota > 0
            lokal = extract_lokal_from_text(current_text)
            dictionary["lokal"] = lokal
            dictionary["poprawne"] = False
            dictionary["wspolnota"] = ""
            wspolnota = wspolnoty_manager.find_wspolnota_in_text(current_text)
            if wspolnota is not None:
                dictionary["wspolnota"] = wspolnota.nazwa
                if lokal != -1 and lokal <= wspolnota.ilosc_mieszkan:
                    dictionary["poprawne"] = True
            dictionary["odrzucone"] = False
            day, month, year = extract_date(current_text)
            dictionary["year"] = year
            dictionary["month"] = month
            dictionary["day"] = day
            dictionary["numer konta"] = ""
            for numer_konta in wspolnoty_manager.numery_kont_bankowych.keys():
                if current_text.find(numer_konta) != -1:
                    dictionary["numer konta"] = numer_konta
            # print(current_text)
            # print("")
            # for key, value in dictionary.items():
            #     print(key + ": " + str(value))
            # print("\n\n\n")
            transakcje.append(Transakcja(wspolnoty_manager, dictionary=dictionary))
            text = text[next_pln + 3:]
            next_pln = text.find("PLN")
            text = text[next_pln + 4:]
            next_pln = text.find("PLN")
    return transakcje


def extract_last_kwota(text: str) -> float:
    print(text)
    current_index = len(text) - 1
    while current_index >= 0 and text[current_index] == " ":
        current_index -= 1
    text = text[:current_index + 1]
    while current_index >= 0 and text[current_index] != "\n":
        current_index -= 1
    if current_index == -1:
        raise IndexError("nie udało się znaleźć kwoty")
    print(text[(current_index+1):].replace(",", ".").replace(" ",""))
    return float(text[(current_index+1):].replace(",", ".").replace(" ",""))
    
def extract_id(text: str) -> str:
    first_index = text.find("CEN")
    while not text[first_index + 3].isnumeric():
        text = text[first_index + 3:]
        first_index = text.find("CEN")
    
    current_index = first_index + 3
    while text[current_index].isnumeric():
        current_index += 1
    return text[first_index : current_index]

def extract_date(text: str) -> tuple[int, int, int]:
    text = text[text.find(" "):]
    return (int(text[1:3]), int(text[4:6]), int(text[7:11]))

def string_after_find(string: str, substring: str) -> str:
    return string[(string.find(substring)+len(substring)):]

if __name__ == "__main__":
    wspolnoty_manager = WspolnotyManager()
    l = extract_transakcje_from_pdf(Path("03_21_3EFNF6_PL8216_0001_20250130190352006.pdf"), wspolnoty_manager)
    for transakcja in l:
        for key, value in transakcja.create_dict_for_json().items():
            print(key + ": " + str(value))
        print("\n\n\n")
