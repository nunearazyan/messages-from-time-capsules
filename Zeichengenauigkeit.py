import os
from difflib import SequenceMatcher

"""
Der Code vergleicht drei Texte von derselben Botschaft zeichenweise und gibt die Übereinstimmung in Prozent zurück.
    
    :param finereader_text: Text aus ABBYY FineReader
    :param rehand_text: Text aus rehand.ru
    :param reference_text: Text zum Abgleich
    :return: Übereinstimmung zwischen OCR aus ABBYY FineReader und Referenz, und OCR aus rehand.ru und Referenz in Prozent
"""

def compare_texts(finereader_text, rehand_text, reference_text):
    if finereader_text is None:
        finereader_similarity = None
    else:
        finereader_similarity = SequenceMatcher(None, finereader_text, reference_text).ratio() # die Schleife wurde erstellt, da nicht für alle Texte eine FineReader-Transkription sinnvoll war
    
    rehand_similarity = SequenceMatcher(None, rehand_text, reference_text).ratio()
    
    finereader_percentage = round(finereader_similarity * 100, 2) if finereader_similarity is not None else 'N/A'
    rehand_percentage = round(rehand_similarity * 100, 2)
    
    return finereader_percentage, rehand_percentage

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        # Zeilenumbrüche und Leerzeichen entfernen
        cleaned_text = text.replace('\n', ' ').replace('\r', ' ')
        return ' '.join(cleaned_text.split())  # Entfernt zusätzliche Leerzeichen

def process_files_in_directory(directory):
    files = os.listdir(directory)
    
    finereader_files = [f for f in files if f.endswith('_FINEREADER.txt')]
    rehand_files = [f for f in files if f.endswith('_REHAND.txt')]
    abgleich_files = [f for f in files if f.endswith('_ABGLEICH.txt')]

    # Liste aller Basisnamen (vor _FINEREADER, _REHAND oder _ABGLEICH) wird erstellt
    all_basenames = set([f.replace('_FINEREADER.txt', '').replace('_REHAND.txt', '').replace('_ABGLEICH.txt', '') for f in files])

    # Für jede Basisdatei werden FINEREADER-, REHAND- und ABGLEICH-Dateien gefunden
    for base_name in all_basenames:
        finereader_file = f"{base_name}_FINEREADER.txt"
        rehand_file = f"{base_name}_REHAND.txt"
        abgleich_file = f"{base_name}_ABGLEICH.txt"

        finereader_text = None
        if finereader_file in finereader_files:
            finereader_text = read_file(os.path.join(directory, finereader_file))
        
        if rehand_file in rehand_files and abgleich_file in abgleich_files:
            rehand_text = read_file(os.path.join(directory, rehand_file))
            abgleich_text = read_file(os.path.join(directory, abgleich_file))

            # Vergleiche zwischen OCR und Referenz
            finereader_accuracy, rehand_accuracy = compare_texts(finereader_text, rehand_text, abgleich_text)
            if finereader_accuracy != 'N/A':
                print(f"Übereinstimmung zwischen {finereader_file} und {abgleich_file}: {finereader_accuracy}%")
            print(f"Übereinstimmung zwischen {rehand_file} und {abgleich_file}: {rehand_accuracy}%")
        else:
            # Ausgabe, wenn eine der Dateien fehlt
            if not rehand_file in rehand_files:
                print(f"Kein REHAND für {base_name} gefunden.")
            if not abgleich_file in abgleich_files:
                print(f"Kein ABGLEICH für {base_name} gefunden.")

directory_path = 'C:/Users/User/Documents/Botschaften aus Zeitkapseln/Texterkennung'
process_files_in_directory(directory_path)

# Somit wurde festgestellt, dass eine niedrige Zeichengenauigkeit bei der Botschaft aus Sankt Petersburg durch falsche bzw. fehlende Erkennung der Interpunktionszeichen und falsche Segmentierung erklärt werden kann
file_path = 'C:/Users/User/Documents/Botschaften aus Zeitkapseln/Texterkennung/SPB_REHAND.txt'
print(read_file(file_path))
file_path = 'C:/Users/User/Documents/Botschaften aus Zeitkapseln/Texterkennung/SPB_ABGLEICH.txt'
print(read_file(file_path))