import os
import random

import src
from src import gui_stimuli, trial_logic, io_manager
from psychopy import core, visual
from psychopy.hardware import keyboard


# tu od was rzezczy
# od os 1: ladowanie konfiguracji (słownika)
from src.io_manager import load_config, save_data
# od os 3: tworzenie okna oraz obiektów strzałek/tekstów
from src.gui_stimuli import stworz_okno_i_gui, stworz_bodzce
# od os 2: logika pojedynczej próby 
from src.trial_logic import uruchom_pojedyncza_probe

config = load_config()  # wczytanie konfiguracji z pliku YAML, która zawiera parametry eksperymentu takie jak czasy fiksacji, czasy prezentacji bodźców, kryteria zaliczenia treningu itp. Ta konfiguracja jest następnie przekazywana do funkcji uruchom_pojedyncza_probe, aby dostosować zachowanie eksperymentu zgodnie z ustawieniami określonymi w pliku konfiguracyjnym.  

# f pomocnicze 

def wczytaj_instrukcje(nazwa_pliku):
    #wczytuje treść instrukcji z folderu instructions/
    sciezka = os.path.join("instructions", nazwa_pliku) # os.path.join łączy foldery w ścieżkę
    with open(sciezka, "r", encoding="utf-8") as f: # encoding="utf-8" - poprawne czytanie polskich znaków
        return f.read()



def wyswietl_ekran_tekstowy(win, text_stim, kb, tresc_tekstu):
    #wyświetla instrukcję i czeka na Spację (kontynuacja) lub Escape (wyjście).
    text_stim.height = 0.05  # Zmniejszamy tekst instrukcji, żeby na pewno zmieścił się na ekranie!
    text_stim.text = tresc_tekstu
    text_stim.draw()
    win.flip()  # przerzuca narysowany obiekt z pamięci karty graficznej na monitor
    
    kb.clearEvents() #czyści pamięć klawiatury przed oczekiwaniem na klawisz
    
    while True:
        keys = kb.getKeys(keyList=['space', 'escape'], waitRelease=False)  # waitRelease=False łapie kliknięcie od razu
        if keys:
            klawisze = [k.name for k in keys]  # Tworzy listę samych nazw wciśniętych klawiszy
            if 'escape' in klawisze: 
                win.close()
                core.quit()
            if 'space' in klawisze:
                break 

    text_stim.height = 0.08  # przywracamy większy rozmiar tekstu na dalszą część eksperymentu





def generuj_proby_treningowe(): 
    #generuje 6 zrównoważonych prób treningowych (2 zg, 2 niezg, 2 neutr)
    baza = [
        {"warunek": "congruent", "kierunek": "lewo", "bodziec": "<<<<<", "poprawny_klawisz": "a"},
        {"warunek": "congruent", "kierunek": "prawo", "bodziec": ">>>>>", "poprawny_klawisz": "l"},
        {"warunek": "incongruent", "kierunek": "prawo", "bodziec": "<<><<", "poprawny_klawisz": "l"},
        {"warunek": "incongruent", "kierunek": "lewo", "bodziec": ">><>>", "poprawny_klawisz": "a"},
        {"warunek": "neutral", "kierunek": "lewo", "bodziec": "--<--", "poprawny_klawisz": "a"},
        {"warunek": "neutral", "kierunek": "prawo", "bodziec": "-->--", "poprawny_klawisz": "l"}
    ]
    
    # pętla dopóki nie bedzie układu bez powtórzeń bodźców pod rząd
    while True:
        random.shuffle(baza)
        powtorka = False
        # sprawdzenie każdej pary sąsiadujących prób
        for i in range(len(baza) - 1):
            if baza[i]["bodziec"] == baza[i + 1]["bodziec"]:
                powtorka = True
                break
        # jeśli nie wykryto identycznych bodźców obok siebie, przerwanie pętli i zwrot gotowej listy
        if not powtorka:
            break
            
    return baza

def generuj_proby_testowe():
    proby = []
    uklady = {
        "congruent": {"lewo": "<<<<<", "prawo": ">>>>>"},
        "incongruent": {"lewo": "<<><<", "prawo": ">><>>"},
        "neutral": {"lewo": "--<--", "prawo": "-->--"}
    }
    #potrójna pętla generująca pełną pulę 36 zrównoważonych prób
    for warunek, kierunki in uklady.items():
        for kierunek, bodziec in kierunki.items():
            poprawny = "a" if kierunek == "lewo" else "l"
            for _ in range(6):  
                proby.append({
                    "warunek": warunek, "kierunek": kierunek, 
                    "bodziec": bodziec, "poprawny_klawisz": poprawny
                })
                
    random.shuffle(proby)
    
    #algorytm naprawiający sekwencję: przechodzi przez całą listę i w razie wykrycia identycznego bodźca pod rząd, zamienia go z losowym elementem z dalszej części puli
    for i in range(len(proby) - 1):
        # sprawdzenie czy bieżący bodziec jest taki sam jak następny
        if proby[i]["bodziec"] == proby[i + 1]["bodziec"]:
            # szukanie losowego indeksu dalej w liście, z którym możemy się zamienić miejscami
            for j in range(i + 2, len(proby)):
                # zamiana ma sens tylko wtedy, gdy nowy element nie stworzy kolejnej powtórki
                if proby[j]["bodziec"] != proby[i]["bodziec"]:
                    # klasyczna zamiana miejscami dwóch elementów w pythonie za pomocą krotki
                    proby[i + 1], proby[j] = proby[j], proby[i + 1]
                    break
                    
    return proby




def analizuj_wyniki_treningu(lista_wynikow):
    #oblicza średnią celność i średni czas reakcji dla prób poprawnych
    if not lista_wynikow:
        return 0.0, 0.0  
    celne = [p["ACC"] for p in lista_wynikow]  #tworzy szybką listę samych zer i jedynek z dokładności (ACC) za pomocą tzw. list comprehension
    srednia_celnosc = sum(celne) / len(celne)
    
    czasy = [p["RT"] for p in lista_wynikow if p["ACC"] == 1 and p["RT"] is not None] # RT tylko z prób, które były poprawne (ACC 1) i gdzie badany w ogóle kliknął
    sredni_rt = sum(czasy) / len(czasy) if czasy else 2.0
    return srednia_celnosc, sredni_rt


# glowna cz

def main():
    kb = keyboard.Keyboard()  # inicjalizacja sprzętowego sterownika klawiatury (milisekundowa precyzja pomiaru czasu reakcji)
    
    # wywołanie f przygotowanych os 1 i 3
    config = load_config()
    win, dane_badanego = stworz_okno_i_gui()
    text_stim = stworz_bodzce(win)
    
    Wszystkie_Dane_CSV = []
    
    # petla warnkowa - trening
    trening_zaliczony = False
    powtorka = False # sprawdza czy to pierwsze podejście, czy badany musi powtarzać trening
    
    while not trening_zaliczony:
        if not powtorka:
            tresc_inst_tren = wczytaj_instrukcje("instrukcja_trening.txt")
            wyswietl_ekran_tekstowy(win, text_stim, kb, tresc_inst_tren)
        else:
            tresc_inst_powt = wczytaj_instrukcje("instrukcja_powtorka.txt")
            wyswietl_ekran_tekstowy(win, text_stim, kb, tresc_inst_powt)
            
        proby_treningowe = generuj_proby_treningowe()
        wyniki_biezacego_treningu = []
        
        for i, proba in enumerate(proby_treningowe): # enumerate - jednocześnie indeks pętli (i = 0, 1, 2...) i samą próbę (proba)
            # petla od os 2
            wynik_proby = uruchom_pojedyncza_probe(win, text_stim, proba, faza="trening", kb=kb, config=config)
            wynik_proby["trial"] = i + 1 # wynik_proby to słownik - pod klucz "trial" aktualny nr próby (i + 1, czyli od 1 zamiast od 0)
            wyniki_biezacego_treningu.append(wynik_proby)
            
        celnosc, avg_rt = analizuj_wyniki_treningu(wyniki_biezacego_treningu)
        
        # weryfikacja kryteriów z pliku konfig os 1
        if celnosc >= config["procent_celnosci_trening"] and avg_rt <= config["max_rt_trening"]: 
            trening_zaliczony = True
        else:
            powtorka = True #aktywuje załadowanie instrukcji poprawkowej przy następnym obrocie pętli
            
    # afza eksperymentalna
    tresc_inst_test = wczytaj_instrukcje("instrukcja_test.txt")
    wyswietl_ekran_tekstowy(win, text_stim, kb, tresc_inst_test)
    
    proby_testowe = generuj_proby_testowe()
    
    for i, proba in enumerate(proby_testowe):
        # znowu kod os 2 - dla fazy właściwej
        wynik_proby = uruchom_pojedyncza_probe(win, text_stim, proba, faza="test", kb=kb, config=config)
        wynik_proby["trial"] = i + 1
        Wszystkie_Dane_CSV.append(wynik_proby)
        
    # zapis danych (os)
    save_data(dane_badanego, Wszystkie_Dane_CSV)
    
    text_stim.text = "Dziękujemy za udział w badaniu!"
    text_stim.draw()
    win.flip()
    core.wait(3.5)
    win.close()
    core.quit()

if __name__ == "__main__":
    main()
