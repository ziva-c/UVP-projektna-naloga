# Projektna naloga za UVP

## Opis programa
Projektna naloga je sestavljena iz funkcij v Pythonu in predstavitve podatkov v Jupyter Notebooku. Podatki za to nalogo so bili zbrani s spletne strani **okusno.je**. Analiziranih je bilo 6733 receptov in njihovih podrobnejših podatkov: avtor, oznaka, težavnost, število sestavin, dolžina navodil, čas priprave, čas kuhanja, skupni čas, energijska vrednost na 100 g jedi ter energijska vrednost porcije jedi. Z grafičnimi predstavitvami so bili raziskani odnosi med temi spremenljivkami.

## Navodila za uporabo
### 1. Potrebni paketi
Poleg standardnih paketov v Pythonu morate imeti nameščene še:
- requests,
- pandas,
- matplotlib,
- seaborn.
Pakete lahko namestite s pomočjo *pip* ukaza: pip install requests pandas matplotlib seaborn.

### 2. Pridobivanje podatkov
Naložite lahko podatke s spletnih strani, oštevilčenih od 1 do 337. Na vsaki od teh strani je objavljenih 20 receptov. Funkcije so dostopne v datoteki `zbiranje_podatkov.py`.
- Najprej shranite želene spletne strani s funkcijo `shrani_osnovne_htmlje(od, do)`, kjer namesto *od* vpišite prvo številko strani, ki jo želite naložiti, namesto *do* pa zadnjo število strani, ki jo želite naložiti, ter številki prištejte 1. Če bi na primer želeli shraniti strani od 1 do 10, bi uporabili `shrani_osnovne_htmlje(1, 11)`. Strani bodo shranjene v mapo `recepti`.
- Da boste pridobili povezave do posameznih receptov, uporabite funkcijo `pridobi_povezave()`. Rezultat shranite v spremenljivko *povezave*.
- Za shranjevanje html datotek posameznih receptov uporabite funkcijo `shrani_posamezne_recepte(povezave)`. Strani bodo shranjene v mapo `posamezni_recepti`.
- Nadaljujete lahko z izluščevanjem podatkov. Najprej izluščite osnovne podatke z uporabo funkcije `izlusci_osnovne_podatke(od, do)`, kjer namesto *od* in *do* vstavite isti številki kot prej. Rezultat shranite v spremenljivko *osnovno_o_receptih*.
- Da boste izluščili še ostale podatke o receptih, uporabite funkcijo `izlusci_podatke_o_receptih(osnovno_o_receptih)` ter rezultat shranite v spremenljivko *podatki*.
- Na koncu vse zbrane podatke shranite v CSV datoteko z uporabo funkcije `shrani_recepte_csv(podatki)`.

### 3. Analiza podatkov
Za ogled analize podatkov odprite datoteko `analiza.ipynb`. Vsako celico lahko ponovno poženete in si ogledate analizo podatkov z grafičnimi predstavitvami.
