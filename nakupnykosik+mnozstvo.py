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

print("-------------------------------------------------------------------------------------------")

for polozka, pocet_kusov in nakupny_kosik:
    if polozka in sklad:
        cena_za_kus, kategoria, skladom = sklad[polozka]
        cena_spolu = cena_za_kus * pocet_kusov
        print(f"{polozka} ({pocet_kusov}x) je {kategoria} a stoji spolu {cena_spolu}€")
        celkova_cena = celkova_cena + cena_spolu
    else:
        print(f"{polozka} nemame v sklade")

print("-------------------------------------------------------------------------------------------")
print("")
print(f"celkova cena: {celkova_cena}€")
print("")
print("-------------------------------------------------------------------------------------------")
