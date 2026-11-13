"""Scrive dati/guida_spec.json leggendo dati/geometria.json (i numeri non si copiano a mano).

Uso: <python> dati/scrivi_spec.py
"""
import json, os

DATI = os.path.dirname(os.path.abspath(__file__))
g = json.load(open(os.path.join(DATI, "geometria.json"), encoding="utf-8"))
P, C, POSE = g["pezzi"], g["controlli"], g["pose"]


def n(x, d=1):
    s = f"{x:.{d}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace(".", ",")


def part(pid, file, label, group, prt, qty=1, tri=1500, k=None, note=""):
    """k = None: tutte le copie montate (stessa rotazione) come instances; k = indice: solo quella copia."""
    pose = POSE[file]
    d = {"id": pid, "label": label, "group": group, "file": f"stl/{file}.stl", "quantity": qty,
         "print": prt, "mode": "mesh", "max_triangles": tri, "matrix": pose[0 if k is None else k]}
    if k is None and len(pose) > 1:
        t0 = [r[3] for r in pose[0][:3]]
        d["instances"] = [[round(r[3] - t0[i], 3) for i, r in enumerate(m[:3])] for m in pose]
    if note:
        d["note_html"] = note
    return d


N_PAL = len(POSE["P15_Gancio"])
DOVE = ["fianco destro della curva alta", "fianco sinistro della curva di mezzo", "fianco del fermo d'uscita",
        "sotto il ramo basso, a destra"]
parts = [
    part("B", "P11_Base", "Base con regali e pupazzo", "Base e tronco", "base", tri=6000),
    part("TR", "P06_Tronco", "Tronco", "Base e tronco", "grandi", tri=3000),
    part("CA", "P07_Cassetto", "Cassetto con serratura", "Base e tronco", "grandi", tri=2000),
    part("N", "P01_Nastro", "Nastro a scivolo", "Albero", "nastro", tri=24000),
    part("S", "P09_Stella", "Stella", "Stella", "piccoli", tri=1200),
]
for i in range(N_PAL):                             # copie con rotazioni diverse: un pezzo per copia (stesso STL)
    q = 1
    parts += [part(f"G{i + 1}", "P15_Gancio", f"Gancio {i + 1}", "Palline", "filetti", qty=q, tri=1200, k=i,
                   note=f"Si avvita nel {DOVE[i]}." if i < len(DOVE) else ""),
              part(f"PS{i + 1}", "P10_Pallina_sopra", f"Pallina {i + 1} · sopra", "Palline", "filetti", qty=q, tri=2000, k=i),
              part(f"PT{i + 1}", "P14_Pallina_sotto", f"Pallina {i + 1} · sotto", "Palline", "filetti", qty=q, tri=2000, k=i)]
parts.append(part("C", "P02_Corpo_capsula", "Corpo capsula 1–24", "Capsule", "capsule", qty=24, tri=1500))
for i in range(1, 25):
    parts.append(part(f"T{i:02d}", f"P03_Tappo_{i:02d}", f"Tappo {i}", "Tappi rossi" if i % 5 == 0 else "Tappi", "tappi", tri=9000))
parts += [
    part("C25", "P04_Corpo_capsula_25", "Corpo capsula 25", "Capsula 25", "capsule", tri=1500),
    part("T25", "P05_Tappo_25", "Tappo 25", "Capsula 25", "tappi", tri=9000),
    part("K", "P08_Chiave", "Chiave", "Capsula 25", "piccoli", tri=800),
]
tappi = [f"T{i:02d}" for i in range(1, 25)]
ganci = [f"G{i + 1}" for i in range(N_PAL)]
palline = [f"PS{i + 1}" for i in range(N_PAL)] + [f"PT{i + 1}" for i in range(N_PAL)]

M = g["montaggio"]
alt = round(M["max"][2])
larg = round(P["P11_Base"]["size"][0])
prof = round(P["P11_Base"]["size"][1])
peso = round(sum(v["peso_PETG_g"] * len(POSE[k]) for k, v in P.items()))
tappo_h = P["P03_Tappo_01"]["size"][2]
cambio = round(tappo_h - 0.6, 1)
cap_l = P["P02_Corpo_capsula"]["size"][2] + tappo_h - 6.0
fil = C["filetto_mm"]
nastro = P["P01_Nastro"]["size"]
base_h = 5.0

spec = {
    "root": "..",
    "output": "guida.html",
    "title": "Calendario dell'Avvento · albero a scivolo · Guida",
    "theme": {"accent": "#1f7a4a", "viewer_bg": "#14201a"},
    "header": {
        "eyebrow": "Calendario dell'Avvento · albero a scivolo · PETG",
        "h1": "Venticinque bussolotti, uno al giorno.",
        "intro_html": "<b>Il nastro verde è uno scivolo chiuso a serpentina.</b> I bussolotti si caricano dall'ingresso in alto, "
                      "scendono da soli lungo i rami inclinati e le curve, e ogni giorno si sfila quello in basso a sinistra: "
                      "il successivo rotola al suo posto. I tappi numerati si avvitano. Il 25 è rosso e contiene la chiave del "
                      "cassetto nascosto nel tronco. Tutto si stampa <b>senza supporti</b>.",
        "facts": [
            {"value": f"{alt} mm", "label": "altezza con la stella"},
            {"value": f"{larg} × {prof} mm", "label": "base"},
            {"value": "25 bussolotti", "label": f"Ø20 × {n(cap_l)} mm, tappo a vite"},
            {"value": f"≈ {peso} g", "label": "PETG in tutto"},
        ],
    },
    "camera": {"yaw": -0.35, "pitch": 0.22},
    "caption": "Albero montato: 25 bussolotti nello scivolo, quattro palline appese, cassetto chiuso a chiave.",
    "model_note_html": f"<span class='badge'>Quote del modello</span><p>Nastro {n(nastro[0])} × {n(nastro[1])} × {n(nastro[2])} mm "
                       f"(si stampa coricato sul retro) · base {larg} × {prof} mm</p>",
    "groups": {"Base e tronco": {"color": "#8a5a3c"}, "Albero": {"color": "#2e8b57"},
               "Palline": {"color": "#c0392b"}, "Capsule": {"color": "#7fbf8a"},
               "Tappi": {"color": "#e8e6e0"}, "Tappi rossi": {"color": "#c0392b"}, "Capsula 25": {"color": "#c0392b"}, "Stella": {"color": "#e0b040"}},
    "steps_section": {
        "eyebrow": "01 / Montaggio", "h2": "Dal tronco alla stella, poi i bussolotti.",
        "intro_html": "Davanti = il lato dei tappi. Destra e sinistra guardando l'albero da davanti.",
        "start_html": "<h3>Prima prova i filetti.</h3><p>Stampa un corpo con il suo tappo, una pallina e un gancio. "
                      f"Il tappo deve avvitarsi a mano fino in battuta (passo {n(fil['passo'])} mm, gioco radiale "
                      f"{n(fil['gioco_radiale'])} mm). Se è duro, aumenta di 0,1 mm la compensazione dei fori nello slicer "
                      "o stampa con layer più bassi; non forzare.</p>",
    },
    "steps": [
        {"title": "Tronco sulla base", "short": "2 perni · dall'alto",
         "text": f"Appoggia il tronco sulla base: i due perni Ø{n(C['perni_fori_mm'][0], 2)} della base entrano nei fori sotto il tronco. "
                 "L'apertura del cassetto guarda davanti.",
         "parts": ["B", "TR"], "built": ["B", "TR"], "moving": ["TR"], "dir": [0, 0, 1], "travel": 40},
        {"title": "Cassetto nel tronco", "short": "da davanti",
         "text": f"Infila il cassetto nel tronco finché il frontale va in battuta. Gioco {n(C['gioco_cassetto_mm'])} mm per lato.",
         "parts": ["CA"], "built": ["B", "TR", "CA"], "moving": ["CA"], "dir": [0, -1, 0], "travel": 45},
        {"title": "Nastro sul tronco", "short": "tenone · da davanti verso il retro",
         "text": f"Sopra il tronco c'è un tenone {n(C['tenone_scanalatura_mm'][0])} × {n(C['tenone_scanalatura_mm'][2])} mm; "
                 "sotto il nastro, una scanalatura aperta sul retro. Appoggia il nastro sul tronco spostato in avanti e fallo "
                 "scorrere verso il retro: si ferma quando il tenone tocca il bordino davanti. Una goccia di colla se vuoi l'albero fisso.",
         "parts": ["N"], "built": ["B", "TR", "CA", "N"], "moving": ["N"], "dir": [0, -1, 0], "travel": 50},
        {"title": "Stella in cima", "short": "linguetta · dall'alto",
         "text": "Infila la linguetta della stella nella fessura della cresta in cima al nastro, con la punta della stella verso davanti.",
         "parts": ["S"], "built": ["B", "TR", "CA", "N", "S"], "moving": ["S"], "dir": [0, 0, 1], "travel": 30},
        {"title": "Ganci a vite", "short": f"{N_PAL} ganci",
         "text": "Avvita i ganci a mano nei fori filettati finché il collarino tocca il nastro: due sui fianchi delle curve, "
                 "uno nel fianco del fermo d'uscita e uno sotto il ramo basso a destra (questo entra dal davanti). "
                 "La gola del piolo deve restare libera.",
         "parts": ganci, "built": ["B", "TR", "CA", "N", "S"] + ganci, "moving": ganci, "dir": [0, -1, 0], "travel": 14},
        {"title": "Palline appese", "short": "due metà · occhiello sul piolo",
         "text": "Avvita la metà sotto (quella con il collare) dentro la metà sopra (quella con l'occhiello) fino a chiuderle. "
                 "Infila l'occhiello sul piolo del gancio: passa sopra la punta e cade nella gola, dove resta appeso.",
         "parts": palline, "built": ["B", "TR", "CA", "N", "S"] + ganci + palline, "moving": palline, "dir": [0, 0, -1], "travel": 18},
        {"title": "Riempi e carica i bussolotti", "short": "dall'ingresso in alto · prima la 1",
         "text": f"Riempi i corpi (bocca Ø{n(C['bocca_capsula_d_mm'])}, interno lungo {n(C['interno_capsula_l_mm'])} mm: cioccolatini piccoli, "
                 "caramelle, un biglietto) e avvita i tappi. Carica dall'ingresso in alto a sinistra, coricati e con il tappo davanti: "
                 "<b>prima la 1</b>, che rotola fino al fermo in basso, poi la 2, la 3… fino alla 24. "
                 "Ognuno spinge e scende dietro al precedente.",
         "parts": ["C"] + tappi, "built": ["B", "TR", "CA", "N", "S"] + ganci + palline + ["C"] + tappi,
         "moving": ["C"] + tappi, "dir": [0, -1, 0], "travel": 60},
        {"title": "Per ultima la 25", "short": "con la chiave",
         "text": f"Metti la chiave nel bussolotto rosso 25 (la chiave è lunga {n(C['chiave_lunghezza_mm'])} mm), avvita il tappo con il numero d'oro "
                 "e caricalo per ultimo: resta all'ingresso, sotto la stella.",
         "parts": ["C25", "T25"], "built": [p["id"] for p in parts if p["id"] != "K"], "moving": ["C25", "T25"], "dir": [0, -1, 0], "travel": 60},
        {"title": "Ogni giorno", "short": "dall'uscita in basso a sinistra",
         "text": "Il bussolotto del giorno è in basso a sinistra, contro il fermo: lì il bordino davanti è tagliato, quindi si sfila "
                 "in avanti. Il successivo rotola al suo posto. Il 25 dicembre la chiave apre il cassetto: infila la mappa in "
                 f"verticale nella serratura ({n(C['mappa_chiave_vs_fessura_mm'][0])} mm nella fessura da {n(C['mappa_chiave_vs_fessura_mm'][1])}), "
                 "gira di 90° e tira.",
         "parts": ["C", "T01", "CA", "K"], "built": [p["id"] for p in parts]},
    ],
    "map": {"eyebrow": "02 / Sigle", "h2": "Uno scivolo, venticinque bussolotti.",
            "cards": [{"title": "Albero · vista frontale", "columns": 3, "top_label": "Alto", "bottom_label": "Basso",
                       "ids": ["", "S", "", "C25", "T25", "K", "G1", "N", "G2", "PS1", "C", "PT1", "T01", "T24", "G4",
                               "TR", "CA", "B"],
                       "note_html": f"I bussolotti 1–24 hanno lo stesso corpo (C, 24 copie) e un tappo numerato ciascuno. "
                                    f"Ganci e palline sono {N_PAL} copie dello stesso pezzo (G, PS, PT)."}]},
    "print": {
        "eyebrow": "03 / Stampa", "h2": "Lista e parametri di stampa.",
        "common_html": "<b>Punto di partenza da verificare:</b> PETG · ugello 0,4 · Anycubic Kobra S1 (piatto 250 × 250). "
                       "Nessun pezzo richiede supporti: gli STL sono già orientati per la stampa.",
        "profiles": [
            {"key": "nastro", "title": "Nastro a scivolo",
             "rows": [["Orientamento", "retro sul piatto (come nello STL)"], ["Layer", "0,20"], ["Pareti", "3"],
                      ["Infill", "15% Gyroid"], ["Brim", "5 mm"]],
             "why": f"Coricato sul retro tutte le pareti del canale sono verticali e i bordini a gradini da 1,33 mm "
                    f"escono a 45°. Ingombro {n(nastro[0])} × {n(nastro[1])} mm, alto {n(nastro[2])}. I fori filettati dei ganci "
                    "sui fianchi restano orizzontali: diametro piccolo, si stampano senza supporti. Il brim tiene giù le punte delle curve.",
             "summary": "retro sul piatto · 3 pareti · 15% · brim"},
            {"key": "base", "title": "Base con regali e pupazzo",
             "rows": [["Layer", "0,20"], ["Pareti", "3"], ["Infill", "15%"], ["Colore", f"regali rossi: multicolore o cambio filamento da {n(base_h)} mm"]],
             "why": "Regali e pupazzo sono uniti alla base. Con un solo filamento esce tutto bianco; con il multicolore i regali sono rossi "
                    "(nello STL sono corpi separati che lo slicer unisce: si possono colorare uno per uno).",
             "summary": "3 pareti · 15%"},
            {"key": "grandi", "title": "Tronco e cassetto",
             "rows": [["Pareti", "3"], ["Infill", "15% Gyroid"], ["Orientamento", "come nello STL"]],
             "why": "Il tronco si stampa sul retro con l'apertura in alto e il tenone che sale dal piatto; il cassetto sul frontale. Niente ponti lunghi.",
             "summary": "3 pareti · 15%"},
            {"key": "capsule", "title": "Corpi dei bussolotti",
             "rows": [["Layer", "0,16"], ["Pareti", "3"], ["Infill", "0% (parete piena)"], ["Orientamento", "fondo sul piatto"]],
             "why": f"Il filetto del collo (passo {n(fil['passo'])}, dente {n(fil['dente'])} mm) viene meglio con layer bassi. "
                    "Stampa i 24 corpi verdi in un piatto e il 25 in rosso.",
             "summary": "0,16 · fondo sul piatto"},
            {"key": "tappi", "title": "Tappi numerati",
             "rows": [["Layer", "0,16 (0,20 l'ultimo strato)"], ["Orientamento", "bocca sul piatto, numero in alto"],
                      ["Cambio colore", f"a {n(cambio)} mm (inizio del numero)"]],
             "why": f"Il numero è in rilievo di 0,6 mm sul cielo. Con una pausa a {n(cambio)} mm il numero esce in un altro colore: "
                    "rosso sui tappi bianchi, bianco sui tappi rossi (5, 10, 15, 20), oro sul 25. "
                    f"La parete del tappo attorno al filetto è {n(fil['parete_tappo'])} mm: almeno 3 perimetri.",
             "summary": f"cambio colore a {n(cambio)} mm"},
            {"key": "filetti", "title": "Ganci e palline",
             "rows": [["Layer", "0,12"], ["Pareti", "4"], ["Infill", "100% (ganci)"], ["Orientamento", "come nello STL"]],
             "why": "Pezzi piccoli con filetti fini (passo 1,5): layer basso e pieni. La metà sopra della pallina si stampa sul giunto "
                    "con l'occhiello in alto; la metà sotto capovolta, sul collare; il gancio in piedi, punta del piolo sul piatto.",
             "summary": "0,12 · 4 pareti"},
            {"key": "piccoli", "title": "Stella e chiave",
             "rows": [["Pareti", "3"], ["Infill", "20%"], ["Velocità", "ridotta"]],
             "why": "Pezzi piatti: la stella ha il retro sul piatto e la linguetta nel suo stesso piano.",
             "summary": "3 pareti · 20%"},
        ],
        "note_html": "Colori del video di partenza: nastro verde, corpi verdi, tappi bianchi con i multipli di 5 rossi, tronco marrone, "
                     "base bianca, stella e chiave oro, palline rosse.",
    },
    "notes": {"eyebrow": "04 / Lo scivolo", "h2": "Perché i bussolotti scendono da soli.", "nav": "Scivolo",
              "cards": [
                  {"title": "Il canale", "html":
                   f"<ul><li>Canale alto {n(C['canale_altezza_mm'])} mm: {n(C['gioco_capsula20_mm'])} mm d'aria sopra il bussolotto Ø20, "
                   "due bussolotti non possono sovrapporsi</li>"
                   f"<li>Rami inclinati di {n(C['pendenza_rami_gradi'])}° verso la curva successiva; curve a U con raggio {n(C['raggio_mediana_curve_mm'])} mm in mezzeria</li>"
                   f"<li>Percorso lungo {n(C['lunghezza_percorso_mm'])} mm: 25 bussolotti e {n(C['spazio_libero_ingresso_mm'])} mm liberi all'ingresso</li>"
                   f"<li>Canale passante, con un bordino da {n(C['bordino_mm'][0])} mm davanti e dietro: il bussolotto resta centrato "
                   f"({n(C['aria_capsula_fra_i_bordini_mm'])} mm d'aria in profondità) e dal retro se ne vedono i fondi</li>"
                   f"<li>{C['colonnine_per_lato']} colonnine da 3 mm davanti e altrettante dietro uniscono i rami fra loro (il canale passante altrimenti li staccherebbe): stanno nello spessore dei bordini, {n(C['colonnine_aria_bussolotto_mm'][0])} mm prima del bussolotto</li>"
                  "<li>All'ingresso i gradini dei bordini diventano rampe: il bussolotto entra senza impuntarsi</li></ul>"},
                  {"title": "Filetti", "html":
                   f"<ul><li>Tappo: passo {n(fil['passo'])}, dente {n(fil['dente'])}, gioco radiale {n(fil['gioco_radiale'])} mm</li>"
                   "<li>Pallina: passo 1,5, cono a 45° che centra le due metà</li>"
                   "<li>Gancio: passo 1,5 nel foro del nastro, 7 mm in presa</li></ul>"
                   "<p>Avvita sempre a mano: se un filetto è duro, non forzarlo con la pinza.</p>"},
                  {"title": "Chiave e serratura", "html":
                   f"<p>La fessura nel frontale del cassetto è {n(C['mappa_chiave_vs_fessura_mm'][3])} × {n(C['mappa_chiave_vs_fessura_mm'][1])} mm. "
                   f"La mappa della chiave è {n(C['mappa_chiave_vs_fessura_mm'][2])} × {n(C['mappa_chiave_vs_fessura_mm'][0])} mm: entra solo in verticale. "
                   "Girata di 90° resta dietro il frontale e fa da maniglia.</p>"
                   "<svg viewBox='0 0 220 110' width='100%'><rect x='10' y='10' width='90' height='90' fill='#c0392b'/>"
                   "<rect x='53' y='37' width='4' height='36' fill='#111'/><text x='55' y='108' font-size='9' text-anchor='middle' fill='currentColor'>fessura 3,2 × 9</text>"
                   "<rect x='130' y='40' width='60' height='9' fill='#e0b040'/><rect x='186' y='29' width='9' height='31' fill='#e0b040'/>"
                   "<circle cx='126' cy='44' r='11' fill='none' stroke='#e0b040' stroke-width='7'/><text x='165' y='80' font-size='9' text-anchor='middle' fill='currentColor'>mappa 2,4 × 7,6</text></svg>"}]},
    "files": {"h2": "I file.", "intro_html": "Script parametrico in Blender: cambia le misure in cima e rigenera tutto.",
              "links": [{"label": "README", "href": "README.md"}, {"label": "Script Blender", "href": "blender/costruisci.py"},
                        {"label": "Geometria e controlli", "href": "dati/geometria.json"}]},
    "footer_html": "Guida offline: aprire questo file dalla cartella del progetto.",
    "parts": parts,
}
json.dump(spec, open(os.path.join(DATI, "guida_spec.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("ok", len(parts), "pezzi")
