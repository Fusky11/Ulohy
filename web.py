from fastapi import FastAPI, HTTPException, status
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

# Model pre pridávanie tovaru adminom
class NovaPolozka(BaseModel):
    nazov: str
    cena: float
    kategoria: str
    mnozstvo: int
    heslo: str

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

# Nový API endpoint pre admina
@app.post("/api/admin/pridat")
def pridat_do_skladu(tovar: NovaPolozka):
    if tovar.heslo != "1111":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Nesprávne administrátorské heslo!"
        )
    
    # Ak už tovar existuje, pripočítame množstvo a aktualizujeme cenu/kategóriu
    if tovar.nazov in sklad:
        sklad[tovar.nazov][0] = tovar.cena
        sklad[tovar.nazov][1] = tovar.kategoria
        sklad[tovar.nazov][2] += tovar.mnozstvo
    else:
        # Ak neexistuje, vytvoríme nový záznam
        sklad[tovar.nazov] = [tovar.cena, tovar.kategoria, tovar.mnozstvo]
        
    return {"message": f"Tovar '{tovar.nazov}' bol úspešne aktualizovaný/pridaný.", "aktualny_sklad": sklad}

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
            .admin-card { background: #fff3cd; border-left: 5px solid #ffc107; }
            h1, h2 { color: #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            button { background: #28a745; color: white; border: none; padding: 8px 14px; border-radius: 4px; cursor: pointer; font-weight: bold; }
            button:hover { background: #218838; }
            .btn-admin { background: #ffc107; color: #212529; }
            .btn-admin:hover { background: #e0a800; }
            input[type=number], input[type=text], input[type=password] { padding: 6px; border: 1px solid #ccc; border-radius: 4px; margin-right: 5px; }
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

        <!-- NOVÝ ADMIN PANEL -->
        <div class="card admin-card">
            <h2>🔐 Admin panel (Pridávanie do skladu)</h2>
            <p>
                <input type="password" id="adminHeslo" placeholder="Heslo" style="width: 100px;">
                <input type="text" id="adminNazov" placeholder="Názov tovaru">
                <input type="text" id="adminKategoria" placeholder="Kategória" style="width: 100px;">
                <input type="number" id="adminCena" placeholder="Cena (€)" min="0" step="0.01" style="width: 70px;">
                <input type="number" id="adminMnozstvo" placeholder="Ks" min="1" style="width: 60px;">
                <button class="btn-admin" onclick="pridatTovarAdmin()">Pridať / Naskladniť</button>
            </p>
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

            // FUNKCIA PRE ADMINA
            async function pridatTovarAdmin() {
                let heslo = document.getElementById('adminHeslo').value;
                let nazov = document.getElementById('adminNazov').value.trim();
                let kategoria = document.getElementById('adminKategoria').value.trim();
                let cena = parseFloat(document.getElementById('adminCena').value);
                let mnozstvo = parseInt(document.getElementById('adminMnozstvo').value);

                if (!heslo || !nazov || !kategoria || isNaN(cena) || isNaN(mnozstvo)) {
                    alert('Vyplňte všetky polia v admin paneli!');
                    return;
                }

                let res = await fetch('/api/admin/pridat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        nazov: nazov,
                        kategoria: kategoria,
                        cena: cena,
                        mnozstvo: mnozstvo,
                        heslo: heslo
                    })
                });

                if (res.status === 401) {
                    alert('Nesprávne heslo!');
                    return;
                }

                if (res.ok) {
                    alert('Sklad bol úspešne aktualizovaný!');
                    document.getElementById('adminNazov').value = '';
                    document.getElementById('adminKategoria').value = '';
                    document.getElementById('adminCena').value = '';
                    document.getElementById('adminMnozstvo').value = '';
                    nacitajSklad();
                } else {
                    alert('Nastala chyba pri komunikácii so serverom.');
                }
            }

            nacitajSklad();
        </script>
    </body>
    </html>
    """

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return """
    <!DOCTYPE html>
    <html lang="sk">
    <head>
        <meta charset="UTF-8">
        <title>Admin Panel - Správa skladu</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 500px; margin: 50px auto; padding: 20px; background: #f4f6f8; }
            .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 5px solid #ffc107; }
            h2 { color: #333; margin-top: 0; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input { width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
            button { width: 100%; background: #ffc107; color: #212529; border: none; padding: 10px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 16px; }
            button:hover { background: #e0a800; }
            .back-link { display: inline-block; margin-top: 15px; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🔐 Admin panel (Pridávanie do skladu)</h2>
            <div class="form-group">
                <label>Heslo:</label>
                <input type="password" id="adminHeslo" placeholder="Zadajte heslo">
            </div>
            <div class="form-group">
                <label>Názov tovaru:</label>
                <input type="text" id="adminNazov" placeholder="Napr. jablko">
            </div>
            <div class="form-group">
                <label>Kategória:</label>
                <input type="text" id="adminKategoria" placeholder="Napr. ovocie">
            </div>
            <div class="form-group">
                <label>Cena za kus (€):</label>
                <input type="number" id="adminCena" min="0" step="0.01" placeholder="0.00">
            </div>
            <div class="form-group">
                <label>Množstvo (ks):</label>
                <input type="number" id="adminMnozstvo" min="1" placeholder="0">
            </div>
            <button onclick="pridatTovarAdmin()">Pridať / Naskladniť</button>
            <a href="/" class="back-link">⬅ Späť do obchodu</a>
        </div>

        <script>
            async function pridatTovarAdmin() {
                let heslo = document.getElementById('adminHeslo').value;
                let nazov = document.getElementById('adminNazov').value.trim();
                let kategoria = document.getElementById('adminKategoria').value.trim();
                let cena = parseFloat(document.getElementById('adminCena').value);
                let mnozstvo = parseInt(document.getElementById('adminMnozstvo').value);

                if (!heslo || !nazov || !kategoria || isNaN(cena) || isNaN(mnozstvo)) {
                    alert('Vyplňte všetky polia!');
                    return;
                }

                let res = await fetch('/api/admin/pridat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        nazov: nazov,
                        kategoria: kategoria,
                        cena: cena,
                        mnozstvo: mnozstvo,
                        heslo: heslo
                    })
                });

                if (res.status === 401) {
                    alert('Nesprávne heslo!');
                    return;
                }

                if (res.ok) {
                    alert('Sklad bol úspešne aktualizovaný!');
                    document.getElementById('adminNazov').value = '';
                    document.getElementById('adminKategoria').value = '';
                    document.getElementById('adminCena').value = '';
                    document.getElementById('adminMnozstvo').value = '';
                } else {
                    alert('Nastala chyba pri komunikácii so serverom.');
                }
            }
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
