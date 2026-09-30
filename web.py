from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()

sklad = {
    "jablko": [1, "ovocie", 1000],
    "banan": [2, "ovocie", 1000],
    "hruska": [2, "ovocie", 1000],
    "marhula": [2, "ovocie", 1000],
    "slivka": [1, "ovocie", 1000],
    "mrkva": [1, "zelenina", 1000],
    "petrzlen": [1, "zelenina", 1000],
    "celer": [2, "zelenina", 1000],
    "zemiak": [1, "zelenina", 1000],
    "cokolada": [3, "sladkost", 1000],
    "cukor": [1, "sladkost", 1000]
}

class PolozkaKosika(BaseModel):
    nazov: str
    mnozstvo: int

class Objednavka(BaseModel):
    polozky: list[PolozkaKosika]
    kupon: str = ""

@app.get("/api/sklad")
def get_sklad():
    return sklad

@app.post("/api/nakup")
def spracuj_nakup(objednavka: Objednavka):
    celkova_cena = 0
    uctenka = []
    
    for item in objednavka.polozky:
        polozka = item.nazov
        pocet_kusov = item.mnozstvo
        
        if polozka in sklad:
            cena_za_kus, kategoria, skladom = sklad[polozka]
            
            if pocet_kusov <= skladom:
                novy_sklad = skladom - pocet_kusov
                sklad[polozka][2] = novy_sklad
                
                cena_spolu = cena_za_kus * pocet_kusov
                celkova_cena += cena_spolu
                uctenka.append(f"{polozka} ({pocet_kusov}x) - {cena_spolu} eur (na sklade: {novy_sklad} ks)")
            else:
                uctenka.append(f"Chyba: {polozka} - pozadovane {pocet_kusov} ks, na sklade len {skladom} ks")
        else:
            uctenka.append(f"Chyba: {polozka} nemame v sklade")

    sprava_kupon = "bez zlavy"
    if objednavka.kupon == "ZLAVA10":
        celkova_cena = celkova_cena * 0.9
        sprava_kupon = "uplatnena zlava 10%"
    elif objednavka.kupon == "ZLAVA50":
        celkova_cena = celkova_cena * 0.5
        sprava_kupon = "uplatnena zlava 50%"
    elif objednavka.kupon != "":
        sprava_kupon = "neplatny kupon"

    return {
        "uctenka": uctenka,
        "celkova_cena": round(celkova_cena, 2),
        "kupon_info": sprava_kupon,
        "aktualny_sklad": sklad
    }

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!DOCTYPE html>
    <html lang="sk">
    <head>
        <meta charset="UTF-8">
        <title>Obchod - Web UI</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 30px auto; padding: 20px; background: #f4f6f8; }
            .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1, h2 { color: #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            button { background: #28a745; color: white; border: none; padding: 8px 14px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            button:hover { background: #218838; }
            input[type=number], input[type=text] { padding: 6px; border: 1px solid #ccc; border-radius: 4px; }
            .btn-danger { background: #dc3545; }
            .btn-danger:hover { background: #c82333; }
            .receipt { background: #e9f7ef; border-left: 5px solid #28a745; padding: 15px; margin-top: 15px; }
        </style>
    </head>
    <body>
        <h1>🛒 Internetovy Obchod (FastAPI)</h1>
        
        <div class="card">
            <h2>Ponuka na sklade</h2>
            <table id="skladTable">
                <tr>
                    <th>Polozka</th>
                    <th>Kategoria</th>
                    <th>Cena / ks</th>
                    <th>Na sklade</th>
                    <th>Pocet</th>
                    <th>Akcia</th>
                </tr>
            </table>
        </div>

        <div class="card">
            <h2>Vas nakupny kosik</h2>
            <ul id="kosikList"><li>Kosik je prazdny</li></ul>
            
            <p>
                <strong>Zlavovy kupon:</strong> 
                <input type="text" id="kuponInput" placeholder="napr. ZLAVA10 alebo ZLAVA50">
            </p>
            <button onclick="odoslatObjednavku()">Dokoncit nakup a zaplatit</button>
        </div>

        <div id="vysledokCard" class="card receipt" style="display:none;">
            <h2>Vysledok nakupu</h2>
            <div id="vysledokText"></div>
        </div>

        <script>
            let kosik = [];

            async function nacitajSklad() {
                let res = await fetch('/api/sklad');
                let sklad = await res.json();
                let table = document.getElementById('skladTable');
                
                table.innerHTML = `<tr>
                    <th>Polozka</th>
                    <th>Kategoria</th>
                    <th>Cena / ks</th>
                    <th>Na sklade</th>
                    <th>Pocet</th>
                    <th>Akcia</th>
                </tr>`;

                for (let [nazov, info] of Object.entries(sklad)) {
                    let [cena, kategoria, skladom] = info;
                    table.innerHTML += `
                        <tr>
                            <td><b>${nazov}</b></td>
                            <td>${kategoria}</td>
                            <td>${cena} eur</td>
                            <td>${skladom} ks</td>
                            <td><input type="number" id="mnozstvo_${nazov}" value="1" min="1" max="${skladom}" style="width: 50px;"></td>
                            <td><button onclick="pridatDoKosika('${nazov}')">Pridat</button></td>
                        </tr>
                    `;
                }
            }

            function pridatDoKosika(nazov) {
                let count = parseInt(document.getElementById('mnozstvo_' + nazov).value);
                kosik.push({ nazov: nazov, mnozstvo: count });
                vykresliKosik();
            }

            function vykresliKosik() {
                let list = document.getElementById('kosikList');
                if (kosik.length === 0) {
                    list.innerHTML = '<li>Kosik je prazdny</li>';
                    return;
                }
                list.innerHTML = '';
                kosik.forEach((item, index) => {
                    list.innerHTML += `<li>${item.nazov} (${item.mnozstvo} ks) <button class="btn-danger" style="padding:2px 6px; font-size:12px;" onclick="odstranit(${index})">X</button></li>`;
                });
            }

            function odstranit(index) {
                kosik.splice(index, 1);
                vykresliKosik();
            }

            async function odoslatObjednavku() {
                if (kosik.length === 0) {
                    alert('Kosik je prazdny!');
                    return;
                }
                let kupon = document.getElementById('kuponInput').value;
                let res = await fetch('/api/nakup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ polozky: kosik, kupon: kupon })
                });
                let data = await res.json();
                
                let text = '<ul>';
                data.uctenka.forEach(r => text += `<li>${r}</li>`);
                text += `</ul>`;
                text += `<p><b>Stav kuponu:</b> ${data.kupon_info}</p>`;
                text += `<h3><b>Konecna cena: ${data.celkova_cena} eur</b></h3>`;
                
                document.getElementById('vysledokText').innerHTML = text;
                document.getElementById('vysledokCard').style.display = 'block';
                
                kosik = [];
                vykresliKosik();
                nacitajSklad();
            }

            nacitajSklad();
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
