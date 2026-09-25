sklad = {
    "jablko": (1, "ovocie", 1000),
    "banan": (2, "ovocie", 1000),
    "hruska": (2, "ovocie", 1000),
    "marhula": (2, "ovocie", 1000),
    "slivka": (1, "ovocie", 1000),
    "mrkva": (1, "zelenina", 1000),
    "petrzlen": (1, "zelenina", 1000),
    "celer": (2, "zelenina", 1000),
    "zemiak": (1, "zelenina", 1000),
    "cokolada": (3, "sladkost", 1000),
    "cukor": (1, "sladkost", 1000)
}

celkova_cena = 0

nakupny_kosik = []

while True:
    print("co chcete pridat do kosika?")
    vstup = input()
    if vstup == "uz nic" or vstup == "koniec":
        break
    print("kolko kusov chcete pridat do kosika?")
    mnozstvo = int(input())
    nakupny_kosik.append((vstup, mnozstvo))

print("-----------------------------------------------------------------")

for polozka, pocet_kusov in nakupny_kosik:
    if polozka in sklad:
        cena_za_kus, kategoria, skladom = sklad[polozka]
        
        if pocet_kusov <= skladom:
            novy_sklad = skladom - pocet_kusov
            sklad[polozka] = (cena_za_kus, kategoria, novy_sklad)
            
            cena_spolu = cena_za_kus * pocet_kusov
            print(f"{polozka} ({pocet_kusov}x) je {kategoria} a stoji spolu {cena_spolu} eur, na sklade zostalo {novy_sklad} ks")
            celkova_cena = celkova_cena + cena_spolu
        else:
            print(f"nemame dostatok {polozka} na sklade, na sklade je len {skladom} ks")
    else:
        print(f"{polozka} nemame v sklade")

while True:
    print("mas kupon na zlavovy kod? (ano/nie)")
    odpoved = input()
    if odpoved == "ano":
        print("zadaj zlavovy kod:")
        zlavovy_kod = input()
        if zlavovy_kod == "ZLAVA10":
            celkova_cena = celkova_cena * 0.9
            break
        elif zlavovy_kod == "ZLAVA50":
            celkova_cena = celkova_cena * 0.5
            print("zlavovy kod bol uplatneny")
        else:
            print("zlavovy kod je neplatny")

print("-------------------------------------------------------------------------------------------")
print("")
print(f"celkova cena: {celkova_cena} eur")
print("")
print("-------------------------------------------------------------------------------------------")
