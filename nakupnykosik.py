ovocie = {"jablko": 1, "banan": 2, "hruska": 2, "marhula": 2, "slivka": 1}
zelenina = {"mrkva": 1, "petrzlen": 1, "celer": 2, "zemiak": 1}
sladkosti = {"cokolada": 3, "cukor": 1}

celkova_cena = 0

nakupny_kosik = []

while True:
    print("co chcete pridat do kosika?")
    vstup = input()
    if vstup == "uz nic" or vstup == "koniec":
        break 
    else: 
        nakupny_kosik.append(vstup)

print("-------------------------------------------------------------------------------------------")

for polozka in nakupny_kosik: 
    if polozka in ovocie:
        print(f"{polozka} je ovocie")
        celkova_cena = celkova_cena + ovocie[polozka]
    elif polozka in zelenina:
        print(f"{polozka} je zelenina")
        celkova_cena = celkova_cena + zelenina[polozka]
    elif polozka in sladkosti:
        print(f"{polozka} je sladkost")
        celkova_cena = celkova_cena + sladkosti[polozka]
    else:
        print(f"{polozka} je nieco ine")

print(f"celkova cena: {celkova_cena}")
