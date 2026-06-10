import os
import csv
import yaml
from datetime import datetime

def load_config(path="config.yaml"):    #domyślna ścieżka do pliku konfiguracyjnego, można ją zmienić przy wywołaniu funkcji
    try:
        with open(path, "r", encoding="utf-8") as file:  # encoding="utf-8" - poprawne czytanie polskich znaków w pliku konfiguracyjnym
            return yaml.safe_load(file)  # wczytuje zawartość pliku YAML i zwraca jako słownik
    except FileNotFoundError: 
        raise FileNotFoundError(f"Nie znaleziono pliku konfiguracyjnego: {path}")  # obsługa błędu, jeśli plik nie istnieje

def create_data_folder(folder_name="data"):  #tworzy folder do przechowywania wyników, jeśli jeszcze nie istnieje
    os.makedirs(folder_name, exist_ok=True)  #exist_ok=True - nie zgłasza błędu, jeśli folder już istnieje

def generate_filename(participant_id, folder_name="data"):  #generuje unikalną nazwę pliku na podstawie ID uczestnika i aktualnego timestampu, umieszczając go w folderze danych
    create_data_folder(folder_name)                         # zapewnia, że folder istnieje przed próbą zapisu pliku
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")    #tworzy unikalny timestamp w formacie RRRRMMDD_GGMMSS, co pozwala na łatwe sortowanie plików i uniknięcie nadpisywania wyników
    return os.path.join(folder_name, f"{participant_id}_{timestamp}.csv") #generuje pełną ścieżkę do pliku wynikowego, łącząc folder docelowy z nazwą pliku zawierającą ID uczestnika i timestamp

def save_data(participant_info, results):  #zapisuje wyniki eksperymentu do pliku CSV, korzystając z informacji o uczestniku do wygenerowania unikalnej nazwy pliku
    participant_id = participant_info.get('ID uczestnika', 'BRAK_ID')
    filename = generate_filename(participant_id)

    fieldnames = ["trial", "phase", "condition", "direction", "key", "RT", "ACC"]  

    with open(filename, "w", newline="", encoding="utf-8") as file:     # otwiera plik do zapisu, używając UTF-8 do poprawnego zapisu polskich znaków, oraz newline="" aby uniknąć dodatkowych pustych linii w pliku CSV
        writer = csv.DictWriter(file, fieldnames=fieldnames)            # tworzy obiekt writer, który będzie używany do zapisywania danych w formie słowników, z kluczami odpowiadającymi nazwom kolumn określonym w fieldnames
        writer.writeheader()                                            # zapisuje nagłówek do pliku CSV, czyli pierwszą linię z nazwami kolumn                          

        for row in results:              # iteruje przez każdą próbę w wynikach eksperymentu, mapując dane z każdej próby na odpowiednie kolumny w pliku CSV
            mapped_row = {
                "trial": row.get("trial"),
                "phase": row.get("faza"),
                "condition": row.get("warunek"),
                "direction": row.get("kierunek"),
                "key": row.get("reakcja_badanego"),
                "RT": row.get("RT"),
                "ACC": row.get("ACC")
            }
            writer.writerow(mapped_row)   # zapisuje każdą próbę jako osobną linię w pliku CSV, korzystając z mapped_row do mapowania kluczy z wyników na odpowiednie kolumny w pliku

    print(f"Wyniki zapisano do: {filename}")
    return filename                  
