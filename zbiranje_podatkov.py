import requests
import time
import re
import os
import html
from urllib import parse
import csv

# ZBIRANJE PODATKOV

od = 1
do = 338

def shrani_osnovne_htmlje(od, do):
    os.makedirs("recepti", exist_ok=True)
    for stevilo in range(od, do):
        html = requests.get(f"https://okusno.je/iskanje?t=recipe&sort=score&p={stevilo}")
        if html.status_code == 200:
            with open(os.path.join("recepti", f"stran-{stevilo}.html"), "w", encoding="utf-8") as f:
                f.write(html.text)
            time.sleep(1)
        else:
            print(f"Napaka pri strani {stevilo}.")

def pridobi_povezave():
    povezave = set()
    for ime_datoteke in os.listdir("recepti"):
        if ime_datoteke.endswith(".html"):
            with open(os.path.join("recepti", ime_datoteke), encoding="utf-8") as f:
                vsebina = f.read()
                najdene = re.finditer(r'href=/recept/([^ >]+)', vsebina)
                for link in najdene:
                    povezave.add("https://okusno.je/recept/" + link)
    return list(povezave)


def shrani_posamezne_recepte(povezave):
    os.makedirs("posamezni_recepti", exist_ok=True)
    for povezava in povezave:
        ime = povezava.split("/")[-1] + ".html"
        pot = os.path.join("posamezni_recepti", ime)
        if not os.path.exists(pot):
            stran = requests.get(povezava)
            if stran.status_code == 200:
                with open(pot, "w", encoding="utf-8") as f:
                    f.write(stran.text)
                time.sleep(1)
            else:
                print(f"Napaka pri {povezava}")


# IZLUŠČEVANJE PODATKOV

def izlusci_osnovne_podatke(od, do):
    vzorec = re.compile(
        r'<a href=/recept/(?P<naslov_strani>[^ >]+) class="group border.*?'
        r'<span class="label bg-primary">(?P<oznaka>[^<]+)</span>.*?'
        r'<h2 class[^>]*>(?P<ime_recepta>[^<]+)</h2>.*?'
        r'</div><div class.*?difficulty difficulty-(?P<tezavnost>[1-3])">',
        re.DOTALL
    )

    osnovno_o_receptih = []
    for stevilo in range(od, do):
        with open(os.path.join("recepti", f"stran-{stevilo}.html"), encoding="utf-8") as f:
            besedilo = f.read()
            for najdba in vzorec.finditer(besedilo):
                osnovno_o_receptih.append((
                    najdba["ime_recepta"].strip(), 
                    najdba["naslov_strani"].strip(), 
                    najdba["oznaka"].strip(), 
                    int(najdba["tezavnost"])
                ))

    return osnovno_o_receptih

def izlusci_podatke_o_receptih(osnovno_o_receptih):
    podatki = []
    for recept in osnovno_o_receptih:
        ime_recepta = recept[0]
        naslov_strani = recept[1]
        oznaka = recept[2]
        tezavnost = recept[3]

        with open(os.path.join("posamezni_recepti", f"{naslov_strani}.html"), encoding="utf-8") as f:
            besedilo = f.read()
        
        # izluščimo ime avtorja
        avtor_re = re.search(r'<a href=/avtor/(?P<avtor>.+?) class', besedilo, re.DOTALL)
        if avtor_re:
            avtor = str(avtor_re.group("avtor").strip())
            avtor = html.unescape(parse.unquote(avtor))
            avtor = avtor.replace('%20', '')
            avtor = avtor.replace('. ', '.')
            avtor = avtor.replace('.', '. ').strip()
        else:
            avtor = None
            print(f"Neznan avtor za {ime_recepta}.")
        
        # izluščimo število sestavin
        sestavine_sez = []
        vzorec_sestavine = re.compile(
            r'<div class="w-2/3 md:4/5 lg:w-2/3 p-8 leading-normal flex items-center">(?P<sestavina>[^<]+)</div>'
        )
        for najdba in vzorec_sestavine.finditer(besedilo):
            sestavine_sez.append(najdba["sestavina"].strip())
        if len(sestavine_sez) == 0:
            print(f"Napaka pri sestavinah za {ime_recepta}.")
        sestavine = len(sestavine_sez)

        # izluščimo čas priprave, čas kuhanja in skupni čas ter pretvorimo v minute
        cas_priprave = re.search(r'PRIPRAVA</span>(?P<cas_priprave>[^<]+)</div>', besedilo)
        cas_kuhanja = re.search(r'KUHANJE</span>(?P<cas_kuhanja>[^<]+)</div>', besedilo)
        cas_priprave_v_min = 0
        cas_kuhanja_v_min = 0
        
        if cas_priprave:
            cas_priprave_v_min = 0
            cas_priprave_str = cas_priprave.group("cas_priprave").strip()
            ure_priprava = re.search(r'(\d*) h', cas_priprave_str)
            if ure_priprava:
                cas_priprave_v_min = 60 * int(ure_priprava.group(1))
            minute_priprava = re.search(r'(\d*) min', cas_priprave_str)
            if minute_priprava:
                cas_priprave_v_min += int(minute_priprava.group(1))
            if cas_priprave_v_min == 0:
                cas_priprave_v_min = None
        else:
            print(f"Napaka pri času priprave za {ime_recepta}.")
        
        if cas_kuhanja:
            cas_kuhanja_v_min = 0
            cas_kuhanja_str = cas_kuhanja.group("cas_kuhanja").strip()
            ure_kuhanje = re.search(r'(\d*) h', cas_kuhanja_str)
            if ure_kuhanje:
                cas_kuhanja_v_min = 60 * int(ure_kuhanje.group(1))
            minute_kuhanje = re.search(r'(\d*) min', cas_kuhanja_str)
            if minute_kuhanje:
                cas_kuhanja_v_min += int(minute_kuhanje.group(1))
            if cas_kuhanja_v_min == 0:
                cas_kuhanja_v_min = None
        else:
            print(f"Napaka pri času kuhanja za {ime_recepta}.")
        
        if cas_priprave_v_min is None and cas_kuhanja_v_min is None:
            skupni_cas = None
        elif cas_priprave_v_min is None:
            skupni_cas = cas_kuhanja_v_min
        elif cas_kuhanja_v_min is None:
            skupni_cas = cas_priprave_v_min
        else:
            skupni_cas = cas_priprave_v_min + cas_kuhanja_v_min

        # izluščimo dolžino navodil za pripravo recepta
        posamezna_navodila = []
        vzorec_navodil = re.compile(r'<p>(?P<navodilo>.*?)</div>', re.DOTALL)
        for najdba in vzorec_navodil.finditer(besedilo):
            posamezna_navodila.append(najdba["navodilo"].strip())
        if len(posamezna_navodila) == 0:
            print(f"Napaka pri navodilih za {ime_recepta}.")
            navodila = None
        else:
            navodila_str = "".join(posamezna_navodila)
            navodila_str = html.unescape(navodila_str)
            navodila_str = re.sub(r'<[^>]+>', '', navodila_str)
            navodila = len(navodila_str.strip())
        
        # izluščimo energijsko vrednost na 100 g jedi ter na porcijo
        energija = []
        vzorec_energije = re.compile(r'<td>(?P<energija>[\d\.]+) kCal')
        for najdba in vzorec_energije.finditer(besedilo):
            energija.append(float(najdba["energija"].strip()))
        if len(energija) != 2:
            energija_100g = None
            energija_porcija = None
            print(f"Napaka pri energijski vrednosti za {ime_recepta}.")
        else:
            energija_100g = None if energija[0] == 0.0 else energija[0]
            energija_porcija = None if energija[1] == 0.0 else energija[1]
        

        podatki.append({
            "ime": ime_recepta,
            "oznaka": oznaka,
            "tezavnost": tezavnost,
            "avtor": avtor,
            "stevilo_sestavin": sestavine,
            "cas_priprave_v_min": cas_priprave_v_min,
            "cas_kuhanja_v_min": cas_kuhanja_v_min,
            "skupni_cas": skupni_cas,
            "dolzina_navodil": navodila,
            "energija_100g": energija_100g,
            "energija_porcija": energija_porcija
        })
    
    return podatki


# SHRANIMO CSV

def shrani_recepte_csv(recepti):
    with open("recepti.csv", "w", encoding="utf-8", newline='') as f:
        pisatelj = csv.writer(f)
        pisatelj.writerow([
            "ime",
            "oznaka",
            "tezavnost",
            "avtor",
            "stevilo_sestavin",
            "cas_priprave",
            "cas_kuhanja",
            "skupni_cas",
            "dolzina_navodil",
            "energija_100g",
            "energija_porcija"
        ])

        for recept in recepti:
            pisatelj.writerow([
                recept["ime"],
                recept["oznaka"],
                recept["tezavnost"],
                recept["avtor"],
                recept["stevilo_sestavin"],
                recept["cas_priprave_v_min"],
                recept["cas_kuhanja_v_min"],
                recept["skupni_cas"],
                recept["dolzina_navodil"],
                recept["energija_100g"],
                recept["energija_porcija"]
            ])