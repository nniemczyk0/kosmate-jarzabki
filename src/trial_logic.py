import random
from psychopy import core

def uruchom_pojedyncza_probe(win, text_stim, proba, faza, kb, config=None):
    # Pobranie czasów z konfiguracji lub bezpieczne domyślne
    # config.get bezpiecznie wyciąga wartości z pliku yaml. jeśli pliku nie ma, random.uniform losuje domyślne czasy
    if config:
        czas_fiksacji = random.uniform(config.get("fixation_min", 0.4), config.get("fixation_max", 1.0))
        czas_bodzca = random.uniform(config.get("stimulus_min", 0.1), config.get("stimulus_max", 0.2))
    else:
        czas_fiksacji = random.uniform(0.4, 1.0)
        czas_bodzca = random.uniform(0.1, 0.2)

    # 1. Punkt fiksacji
    text_stim.text = "+"
    text_stim.draw()
    win.flip()                # wyświetla punkt fiksacji na ekranie
    core.wait(czas_fiksacji)  #czas fiksacji jest losowy w zakresie 400-1000 ms, co pomaga zapobiegać przewidywalności i utrzymuje uwagę uczestnika na ekranie przed pojawieniem się bodźca

    # 2. Rysowanie strzałek
    text_stim.text = proba["bodziec"]
    text_stim.draw()
    win.flip()

    kb.clock.reset()         # resetuje wewnętrzny zegar klawiatury, aby dokładnie mierzyć czas reakcji od momentu pojawienia się bodźca
    kb.clearEvents()         # czyści pamięć klawiatury, aby uniknąć rejestrowania przypadkowych klawiszy naciśniętych przed pojawieniem się bodźca
    
    timer_odpowiedzi = core.Clock()
    klawisz = None           # zmienna do przechowywania naciśniętego klawisza, która będzie aktualizowana w pętli zbierania reakcji
    RT = None                # zmienne do przechowywania reakcji i czasu reakcji, które będą aktualizowane w pętli zbierania reakcji
    bodziec_ukryty = False   # flaga, która pozwala ukryć bodziec po określonym czasie, ale nadal czekać na reakcję uczestnika przez pełne 2 sekundy, co jest ważne dla oceny reakcji w warunkach treningowych, gdzie feedback jest natychmiastowy, a uczestnik może potrzebować więcej czasu na reakcję.

    # 3. Pętla zbierania reakcji
    while timer_odpowiedzi.getTime() < 2.0:  #pętla while non-stop sprawdza czas i klawiaturę aż miną 2 sekundy
        if not bodziec_ukryty and timer_odpowiedzi.getTime() >= czas_bodzca:
             # logika znikania strzałek: jeśli czas prezentacji minął, a bodziec jeszcze jest widoczny (bodziec_ukryty == False) to win.flip() ktory czyści ekran na szaro. badany nadal ma czas na odpowiedź, ale strzałek już nie widzi
             win.flip()  # jednorazowe czyszczenie ekranu po wyznaczonym czasie strzałek
             bodziec_ukryty = True  # ustawienie flagi, aby nie ukrywać bodźca ponownie w kolejnych iteracjach pętli

        keys = kb.getKeys(keyList=['a', 'l', 'escape'], waitRelease=False)   # waitRelease=False pozwala na rejestrowanie klawiszy natychmiast po naciśnięciu, co jest ważne dla dokładnego pomiaru czasu reakcji, zwłaszcza w warunkach treningowych, gdzie uczestnicy mogą reagować bardzo szybko po pojawieniu się bodźca.
        if keys:
            wybrany_klawisz = keys[-1]
            if wybrany_klawisz.name == 'escape':
                win.close()
                core.quit()
            
            klawisz = wybrany_klawisz.name
            RT = wybrany_klawisz.rt
            break

    # Ocena poprawności
    wynik = "timeout" # domyślnie ustawiamy wynik na "timeout", który będzie aktualizowany na "dobrze" lub "błąd" w zależności od reakcji uczestnika
    acc = 0           # domyślnie ustawiamy ACC na 0 (niepoprawna reakcja), który będzie aktualizowany na 1 (poprawna reakcja) jeśli uczestnik naciśnie poprawny klawisz  

    if klawisz is not None:
        if klawisz == proba["poprawny_klawisz"]:
            wynik = "dobrze"
            acc = 1
        else:
            wynik = "błąd"

    # 4. Feedback w treningu
    if faza == "trening":
        if wynik == "dobrze":
            text_stim.text = f"Dobrze!\nRT: {RT:.3f} s"
        elif wynik == "błąd":
            text_stim.text = "Błąd!"
        else:
            text_stim.text = "Timeout!"
        text_stim.draw()
        win.flip()
        core.wait(random.uniform(0.5, 1.0))

    # 5. Przerwa ISI - czysty ekran
    win.flip()
    random_ISI = random.uniform(0.8, 1.0)   # losowy ISI między 800 a 1000 ms, co pomaga zapobiegać przewidywalności i utrzymuje uwagę uczestnika na ekranie przed kolejnym bodźcem
    core.wait(random_ISI)

    return {
        "trial": None,
        "faza": faza,
        "warunek": proba["warunek"],
        "kierunek": proba["kierunek"],
        "wyswietlony_bodziec": proba["bodziec"],
        "poprawny_klawisz": proba["poprawny_klawisz"],
        "reakcja_badanego": klawisz if klawisz else "Brak",
        "RT": RT if RT else None,
        "ACC": acc,
        "wynik": wynik
    }
