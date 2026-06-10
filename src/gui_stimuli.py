from psychopy import visual, gui, core

def stworz_okno_i_gui(): #funkcja tworzy okno i GUI do zbierania danych uczestnika, zwraca oba obiekty
    info = { 
        'ID uczestnika': '', 
        'Imię i nazwisko': '',
        'Wiek': '',
        'Płeć': ['Kobieta', 'Mężczyzna', 'Inna'],
        'Grupa': ['Kontrolna', 'Eksperymentalna']
    }

    dlg = gui.DlgFromDict( 
        dictionary=info, #słownik z kluczami jako etykiety i wartościami jako pola do wypełnienia
        title='Dane uczestnika', 
        sortKeys=False  #zapobiega sortowaniu pól alfabetycznie, zachowując kolejność zdefiniowaną w słowniku
    )

    if not dlg.OK: 
        core.quit()

    #okno dopasowane do pełnego ekranu z poprawnymi jednostkami
    win = visual.Window(
        size=(),  
        color='#bdb3b3',
        units='height', #bodźce skalują się proporcjonalnie do wysokości ekranu niezależnie czy monitor jest kwadratowy czy panoramiczny
        fullscr=True,   #tryb pełnoekranowy i blokada powiadomien z systemu
        allowGUI=False, #blokuje interfejs systemowy (np. pasek zadań), żeby nie rozpraszać uczestnika 
        screen=0        #wybór ekranu (0 to główny monitor, 1 to drugi monitor, itd.)
    )
    return win, info

def stworz_bodzce(win):
    #powiększony uniwersalny obiekt tekstowy dla strzałek na pełnym ekranie
    text_stim = visual.TextStim(
        win,         #okno, w którym będzie wyświetlany bodziec
        text='',    
        color='black',
        height=0.08  #rozmiar tekstu dostosowany do pełnego ekranu, można modyfikować dynamicznie w trakcie eksperymentu
    )
    return text_stim
