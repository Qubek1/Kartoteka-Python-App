possible_prefixes = [" lokal", " lokal nr", " lokal nr.", " mieszkanie", " mieszkania", " m.", " m", "/", "\\"]

def extract_lokal_from_text(text:str) -> int:
    for prefix in possible_prefixes:
        number_text = ""
        prefix_index = text.lower().find(prefix)
        if prefix_index == -1:
            continue
        number_text = extract_number_text(text, prefix_index + len(prefix))
        if number_text != "":
            return int(number_text)
    return -1

def extract_number_text(text:str, index:int) -> str:
    liczba = ""
    if text[index] == " ":
        index += 1
    while index < len(text) and text[index].isdigit():
        liczba += text[index]
        index += 1
    return liczba