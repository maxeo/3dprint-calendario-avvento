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


def part(pid, file, label, group, prt, qty=1, tri=1500, k=None, note="", vista=None):
    """k = None: tutte le copie montate (stessa rotazione) come instances; k = indice: solo quella copia.
    vista: opzioni del viewer, es. {"smooth": 35, "cull": True, "comune": "tappo_corpo"}; con vista la mesh
    mostrata è dati/vista/<file>.stl (solo le superfici visibili, scritta da costruisci.py) e non si decima."""
    pose = POSE[file]
    d = {"id": pid, "label": label, "group": group, "file": f"stl/{file}.stl", "quantity": qty,
         "print": prt, "mode": "mesh", "max_triangles": tri, "matrix": pose[0 if k is None else k]}
    if k is None and len(pose) > 1:
        t0 = [r[3] for r in pose[0][:3]]
        d["instances"] = [[round(r[3] - t0[i], 3) for i, r in enumerate(m[:3])] for m in pose]
    if vista is not None:
        d["view_file"] = f"dati/vista/{file}.stl"
        d["max_triangles"] = 100000
        if vista.get("comune"):                    # mesh comune a più pezzi, una volta sola nella pagina
            d["view_shared"] = f"dati/vista/{vista['comune']}.stl"
        d.update({k: v for k, v in vista.items() if k in ("smooth", "cull")})
    elif CHIUSO.get(file):                         # mesh chiuse: le facce posteriori non si disegnano
        d["cull"] = True
    if note:
        d["note_html"] = note
    return d


LISCIO = {"smooth": 35, "cull": True}            # pezzi torniti: luce interpolata, spigoli vivi oltre 35°
CHIUSO = {f: P[f].get("non_manifold_edges", 1) == 0 for f in P}
N_PAL = len(POSE["P15_Gancio"])
DOVE = ["fianco destro della curva alta", "fianco sinistro della curva di mezzo", "fianco del fermo d'uscita",
        "sotto il ramo basso, a destra"]
parts = [
    dict(part("B", "P11_Base", "Base con pupazzo", "Base", "base", tri=20000), smooth=35, cull=True),   # pupazzo liscio
    part("R1", "P12_Regalo", "Regalo rosso · davanti a sinistra", "Regali rossi", "regali", k=0),
    part("R2", "P12_Regalo", "Regalo verde · davanti a destra", "Regalo verde", "regali", k=1),
    part("R3", "P12_Regalo", "Regalo rosso · dietro a destra", "Regali rossi", "regali", k=2),
    part("NR1", "P20_Nastro_regalo", "Nastro verde · regalo davanti a sinistra", "Nastri verdi", "regali", k=0),
    part("NR2", "P20_Nastro_regalo", "Nastro rosso · regalo verde", "Nastro rosso", "regali", k=1),
    part("NR3", "P20_Nastro_regalo", "Nastro verde · regalo dietro a destra", "Nastri verdi", "regali", k=2),
    part("CP", "P18_Cappello", "Cappello del pupazzo", "Cappello e occhi", "pupazzo"),
    part("NS", "P19_Naso", "Naso del pupazzo (si avvita)", "Naso", "pupazzo", tri=600),
    part("OC1", "P21_Occhio", "Occhio sinistro (a incastro)", "Cappello e occhi", "pupazzo", k=0, tri=600),
    part("OC2", "P21_Occhio", "Occhio destro (a incastro)", "Cappello e occhi", "pupazzo", k=1, tri=600),
    part("PR", "P17_Perno_regalo", "Perno dei regali", "Perni", "regali", qty=len(POSE["P17_Perno_regalo"]), tri=300),
    part("TR", "P06_Tronco", "Tronco", "Tronco", "grandi", tri=3000),
    part("CA", "P07_Cassetto", "Cassetto con serratura", "Cassetto", "grandi", tri=2000),
    part("N", "P01_Nastro", "Nastro a scivolo", "Albero", "nastro", tri=24000),
    part("S", "P09_Stella", "Stella", "Stella", "piccoli", tri=1200),
]
for i in range(N_PAL):                             # copie con rotazioni diverse: un pezzo per copia (stesso STL)
    q = 1
    parts += [part(f"G{i + 1}", "P15_Gancio", f"Gancio {i + 1}", "Ganci", "filetti", qty=q, k=i, vista=LISCIO,
                   note=f"Si avvita nel {DOVE[i]}." if i < len(DOVE) else ""),
              part(f"PS{i + 1}", "P10_Pallina_sopra", f"Pallina {i + 1} · sopra", "Palline", "filetti", qty=q, k=i, vista=LISCIO),
              part(f"PT{i + 1}", "P14_Pallina_sotto", f"Pallina {i + 1} · sotto", "Palline", "filetti", qty=q, k=i, vista=LISCIO)]
parts.append(part("C", "P02_Corpo_capsula", "Corpo capsula 1–24", "Capsule", "capsule", qty=24, vista=LISCIO))
for i in range(1, 25):
    parts.append(part(f"T{i:02d}", f"P03_Tappo_{i:02d}", f"Tappo {i}", "Tappi rossi" if i % 5 == 0 else "Tappi", "tappi",
                      vista=dict(LISCIO, comune="tappo_corpo")))
parts += [
    part("C25", "P04_Corpo_capsula_25", "Corpo capsula 25", "Capsula 25", "capsule", vista=LISCIO),
    part("T25", "P05_Tappo_25", "Tappo 25", "Tappi rossi", "tappi", vista=dict(LISCIO, comune="tappo_corpo")),
    part("K", "P08_Chiave", "Chiave", "Chiave", "piccoli", tri=800),
]
for i in range(1, 26):                             # numeri da inserire nel solco (facoltativi, altro colore)
    parts.append(part(f"N{i:02d}", f"P16_Numero_{i:02d}", f"Numero {i} da inserire",
                      "Capsula 25" if i == 25 else ("Numeri bianchi" if i % 5 == 0 else "Numeri rossi"), "numeri", vista={"cull": True},
                      note="Facoltativo: si preme a filo nel numero inciso del tappo."))
parts[-1]["color"] = "#e0b040"                     # N25: nel gruppo della capsula 25, ma il numero resta oro
tappi = [f"T{i:02d}" for i in range(1, 25)]
numeri = [f"N{i:02d}" for i in range(1, 26)]
ganci = [f"G{i + 1}" for i in range(N_PAL)]
palline = [f"PS{i + 1}" for i in range(N_PAL)] + [f"PT{i + 1}" for i in range(N_PAL)]
regali = ["R1", "R2", "R3"]
nastri = ["NR1", "NR2", "NR3"]
BASE_OK = ["B", "PR"] + regali + nastri + ["CP", "NS", "OC1", "OC2"]   # base con regali, nastri e pupazzo finiti

M = g["montaggio"]
alt = round(M["max"][2])
larg = round(P["P11_Base"]["size"][0])
prof = round(P["P11_Base"]["size"][1])
peso = round(sum(v["peso_PETG_g"] * len(POSE[k]) for k, v in P.items()))
tappo_h = P["P03_Tappo_01"]["size"][2]
cap_l = P["P02_Corpo_capsula"]["size"][2] + tappo_h - 6.0
fil = C["filetto_mm"]
nastro = P["P01_Nastro"]["size"]
base_h = 5.0

# filamento di ogni pezzo (per gli ZIP «Scarica per colore»): un solo verde; il giallo vale anche per la stella
FILAMENTI = {"verde": {"label": "Verde", "color": "#2e8b57"}, "rosso": {"label": "Rosso", "color": "#c0392b"},
             "bianco": {"label": "Bianco", "color": "#efede6"}, "giallo": {"label": "Giallo", "color": "#f2c418"},
             "marrone": {"label": "Marrone", "color": "#8a5a3c"}, "nero": {"label": "Nero", "color": "#26262a"}}
FIL_GRUPPO = {"Base": "bianco", "Tronco": "marrone", "Cassetto": "rosso", "Albero": "verde", "Stella": "giallo",
              "Palline": "rosso", "Ganci": "giallo", "Capsule": "verde", "Tappi": "bianco", "Tappi rossi": "rosso",
              "Capsula 25": "rosso", "Chiave": "giallo", "Numeri rossi": "rosso", "Numeri bianchi": "bianco",
              "Regalo verde": "verde", "Regali rossi": "rosso", "Nastri verdi": "verde", "Nastro rosso": "rosso",
              "Perni": "bianco", "Cappello e occhi": "nero", "Naso": "giallo"}
for pp in parts:
    pp["filament"] = "giallo" if pp["id"] == "N25" else FIL_GRUPPO[pp["group"]]

spec = {
    "root": "..",
    "filaments": FILAMENTI,
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
    "labels": False,                               # 70 pezzi: sigle spente all'apertura, il pulsante «Sigle» le riaccende
    "model_note_html": f"<span class='badge'>Quote del modello</span><p>Nastro {n(nastro[0])} × {n(nastro[1])} × {n(nastro[2])} mm "
                       f"(si stampa coricato sul retro) · base {larg} × {prof} mm</p>",
    "groups": {"Base": {"color": "#efede6"}, "Tronco": {"color": "#8a5a3c"}, "Albero": {"color": "#2e8b57"},
               "Palline": {"color": "#c0392b"}, "Capsule": {"color": "#7fbf8a"},
               "Tappi": {"color": "#e8e6e0"}, "Tappi rossi": {"color": "#c0392b"}, "Capsula 25": {"color": "#c0392b"}, "Chiave": {"color": "#f2c418"}, "Regali rossi": {"color": "#c0392b"}, "Regalo verde": {"color": "#3fae5a"}, "Nastri verdi": {"color": "#3fae5a"}, "Nastro rosso": {"color": "#c0392b"}, "Cappello e occhi": {"color": "#26262a"}, "Cassetto": {"color": "#c0392b"}, "Naso": {"color": "#f2c418"}, "Perni": {"color": "#d8d4c8"}, "Ganci": {"color": "#f2c418"}, "Stella": {"color": "#e0b040"},
               "Numeri rossi": {"color": "#a8241c"}, "Numeri bianchi": {"color": "#f4f2ec"}},
    "steps_section": {
        "eyebrow": "01 / Montaggio", "h2": "Dal tronco alla stella, poi i bussolotti.",
        "intro_html": "Davanti = il lato dei tappi. Destra e sinistra guardando l'albero da davanti.",
        "start_html": "<h3>Prima prova i filetti.</h3><p>Stampa un corpo con il suo tappo, una pallina e un gancio. "
                      f"Il tappo deve avvitarsi a mano fino in battuta (passo {n(fil['passo'])} mm, gioco radiale "
                      f"{n(fil['gioco_radiale'])} mm). Se è duro, aumenta di 0,1 mm la compensazione dei fori nello slicer "
                      "o stampa con layer più bassi; non forzare.</p>",
    },
    "steps": [
        {"title": "Regali sulla base", "short": "2 perni per regalo · dall'alto",
         "text": f"Infila i perni (Ø{n(C['regali_mm']['perno'][0], 2)} × {n(C['regali_mm']['perno'][1])} mm, due per regalo) nei fori della base, "
                 f"poi appoggia sopra i regali: i due fori sotto ogni regalo vanno sui suoi perni. Il verde va davanti a destra, "
                 "accanto al tronco; i rossi davanti a sinistra, vicino al pupazzo, e dietro a destra. Se un perno balla, un punto di colla.",
         "parts": ["PR"] + regali, "built": ["B", "PR"] + regali, "moving": regali, "dir": [0, 0, 1], "travel": 25},
        {"title": "Nastri sui regali", "short": "dall'alto · nel solco",
         "text": f"Ogni nastro è una croce con quattro gambe: si infila dall'alto nel solco del regalo "
                 f"({n(C['nastro_regalo_mm']['solco'][0])} × {n(C['nastro_regalo_mm']['solco'][1])} mm) e ne sporge "
                 f"{n(C['nastro_regalo_mm']['sporgenza'])} mm. Nastro verde sui regali rossi, rosso su quello verde.",
         "parts": nastri, "built": ["B", "PR"] + regali + nastri, "moving": nastri, "dir": [0, 0, 1], "travel": 20},
        {"title": "Cappello al pupazzo", "short": "perno in cima alla testa",
         "text": f"Il cappello nero si infila sul perno Ø{n(C['pupazzo_mm']['perno_cappello'][0])} in cima alla testa "
                 f"(foro Ø{n(C['pupazzo_mm']['foro_cappello'][0])}). Se balla, un punto di colla.",
         "parts": ["CP"], "built": ["B", "PR"] + regali + nastri + ["CP"], "moving": ["CP"], "dir": [0, 0, 1], "travel": 15},
        {"title": "Naso e occhi al pupazzo", "short": "naso avvitato · occhi a incastro",
         "text": f"Il naso giallo ha un codolo filettato Ø{n(C['pupazzo_mm']['filetto_viso']['diametro'])} "
                 f"(passo {n(C['pupazzo_mm']['filetto_viso']['passo'])}): avvitalo a mano, un paio di giri, finché la base "
                 f"tocca la testa. Gli occhi neri (bottone Ø{n(C['pupazzo_mm']['occhi']['bottone_d'])}) entrano a forza: codolo "
                 f"e foro sono Ø{n(C['pupazzo_mm']['occhi']['foro'][0])} e i fori così piccoli escono un po' stretti. Spingili con il pollice.",
         "parts": ["NS", "OC1", "OC2"], "built": BASE_OK, "moving": ["NS", "OC1", "OC2"], "dir": [0, -1, 0], "travel": 10},
        {"title": "Tronco sulla base", "short": "2 perni · dall'alto",
         "text": f"Appoggia il tronco sulla base: i due perni Ø{n(C['perni_fori_mm'][0], 2)} della base entrano nei fori sotto il tronco. "
                 "L'apertura del cassetto guarda davanti.",
         "parts": ["TR"], "built": BASE_OK + ["TR"], "moving": ["TR"], "dir": [0, 0, 1], "travel": 40},
        {"title": "Cassetto nel tronco", "short": "da davanti",
         "text": f"Infila il cassetto nel tronco finché il frontale va in battuta. Gioco {n(C['gioco_cassetto_mm'])} mm per lato.",
         "parts": ["CA"], "built": BASE_OK + ["TR", "CA"], "moving": ["CA"], "dir": [0, -1, 0], "travel": 45},
        {"title": "Nastro sul tronco", "short": "tenone · da davanti verso il retro",
         "text": f"Sopra il tronco c'è un tenone {n(C['tenone_scanalatura_mm'][0])} × {n(C['tenone_scanalatura_mm'][2])} mm; "
                 "sotto il nastro, una scanalatura aperta sul retro. Appoggia il nastro sul tronco spostato in avanti e fallo "
                 "scorrere verso il retro: si ferma quando il tenone tocca il bordino davanti. Una goccia di colla se vuoi l'albero fisso.",
         "parts": ["N"], "built": BASE_OK + ["TR", "CA", "N"], "moving": ["N"], "dir": [0, -1, 0], "travel": 50},
        {"title": "Stella in cima", "short": "linguetta · dall'alto",
         "text": "Infila la linguetta della stella nella fessura della cresta in cima al nastro, con la punta della stella verso davanti.",
         "parts": ["S"], "built": BASE_OK + ["TR", "CA", "N", "S"], "moving": ["S"], "dir": [0, 0, 1], "travel": 30},
        {"title": "Ganci a vite", "short": f"{N_PAL} ganci",
         "text": "Avvita i ganci a mano nei fori filettati finché il collarino tocca il nastro: due sui fianchi delle curve, "
                 "uno nel fianco del fermo d'uscita e uno sotto il ramo basso a destra (questo entra dal davanti). "
                 "La gola del piolo deve restare libera.",
         "parts": ganci, "built": BASE_OK + ["TR", "CA", "N", "S"] + ganci, "moving": ganci, "dir": [0, -1, 0], "travel": 14},
        {"title": "Palline appese", "short": "due metà · occhiello sul piolo",
         "text": "Avvita la metà sotto (quella con il collare) dentro la metà sopra (quella con l'occhiello) fino a chiuderle. "
                 "Infila l'occhiello sul piolo del gancio: passa sopra la punta e cade nella gola, dove resta appeso.",
         "parts": palline, "built": BASE_OK + ["TR", "CA", "N", "S"] + ganci + palline, "moving": palline, "dir": [0, 0, -1], "travel": 18},
        {"title": "Riempi e carica i bussolotti", "short": "dall'ingresso in alto · prima la 1",
         "text": f"Riempi i corpi (bocca Ø{n(C['bocca_capsula_d_mm'])}, interno lungo {n(C['interno_capsula_l_mm'])} mm: cioccolatini piccoli, "
                 "caramelle, un biglietto) e avvita i tappi. Se hai stampato i numeri da inserire, premili a filo nel solco del tappo "
                 "(rossi nei tappi bianchi, bianchi nei rossi; una goccia di colla se sono lenti). Carica dall'ingresso in alto a sinistra, coricati e con il tappo davanti: "
                 "<b>prima la 1</b>, che rotola fino al fermo in basso, poi la 2, la 3… fino alla 24. "
                 "Ognuno spinge e scende dietro al precedente.",
         "parts": ["C"] + tappi + numeri[:24], "built": BASE_OK + ["TR", "CA", "N", "S"] + ganci + palline + ["C"] + tappi + numeri[:24],
         "moving": ["C"] + tappi + numeri[:24], "dir": [0, -1, 0], "travel": 60},
        {"title": "Per ultima la 25", "short": "con la chiave",
         "text": f"Metti la chiave nel bussolotto rosso 25 (la chiave è lunga {n(C['chiave_lunghezza_mm'])} mm), avvita il tappo rosso con il 25 "
                 "e caricalo per ultimo: resta all'ingresso, sotto la stella.",
         "parts": ["C25", "T25", "N25"], "built": [p["id"] for p in parts if p["id"] != "K"], "moving": ["C25", "T25", "N25"], "dir": [0, -1, 0], "travel": 60},
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
                               "TR", "CA", "B", "R1", "NR1", "PR", "CP", "NS", "OC1"],
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
            {"key": "base", "title": "Base con pupazzo",
             "rows": [["Layer", "0,20"], ["Pareti", "3"], ["Infill", "15%"], ["Colore", "bianco"]],
             "why": f"Il pupazzo è unito alla base (lo unisce lo slicer). I sei fori dei regali sono ciechi, profondi "
                    f"{n(C['regali_mm']['foro'][1])} mm: sotto restano {n(C['regali_mm']['fondo_sotto_foro_base'])} mm di base.",
             "summary": "3 pareti · 15%"},
            {"key": "pupazzo", "title": "Cappello, occhi e naso",
             "rows": [["Layer", "0,12"], ["Pareti", "3"], ["Infill", "100%"], ["Brim", "3 mm su naso e occhi"],
                      ["Colore", "cappello e occhi neri, naso giallo"]],
             "why": f"Pezzi piccoli: il cappello si stampa sulla tesa con il foro in basso; naso e occhi in piedi sul codolo. Il naso ha il filetto "
                    f"(Ø{n(C['pupazzo_mm']['filetto_viso']['diametro'])}, il più piccolo che viene bene con l'ugello 0,4; gioco radiale "
                    f"{n(C['pupazzo_mm']['filetto_viso']['gioco_radiale'])} mm). "
                    "Il brim tiene giù il naso; stampali insieme ad altri pezzi dello stesso colore così il layer ha il tempo di raffreddare.",
             "summary": "0,12 · 100%"},
            {"key": "regali", "title": "Regali, nastri e perni",
             "rows": [["Layer", "0,20"], ["Pareti", "3"], ["Infill", "15%"], ["Orientamento", "fondo forato sul piatto"],
                      ["Colore", "un regalo verde e due rossi; nastri: due verdi e uno rosso; perni di qualsiasi colore"]],
             "why": f"Un solo STL per i tre regali e uno per i nastri: un regalo verde e due rossi, due nastri verdi e uno rosso. Il nastro si stampa capovolto, croce sul piatto e gambe in alto. I perni "
                    f"Ø{n(C['regali_mm']['perno'][0], 2)} entrano nei fori Ø{n(C['regali_mm']['foro'][0])} con "
                    f"{n(C['regali_mm']['aria_in_fondo_ai_fori'])} mm d'aria in fondo: si stampano in piedi, punte smussate.",
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
             "rows": [["Layer", "0,16"], ["Orientamento", "bocca sul piatto, numero in alto"],
                      ["Colore", "uno solo: bianco, rosso per 5, 10, 15, 20 e 25"]],
             "why": f"Il numero è inciso {n(C['numero_inciso_mm'])} mm nel cielo del tappo (sotto restano "
                    f"{n(C['cielo_sotto_numero_mm'])} mm): niente cambi filamento, si legge per l'ombra del solco. "
                    "Se lo vuoi colorato, ripassa il solco con un pennarello indelebile e pulisci la superficie. "
                    f"La parete del tappo attorno al filetto è {n(fil['parete_tappo'])} mm: almeno 3 perimetri.",
             "summary": "numero inciso · un colore"},
            {"key": "numeri", "title": "Numeri da inserire (facoltativi)",
             "rows": [["Layer", "0,16 o 0,20"], ["Orientamento", "stesi sul piatto"], ["Pareti", "2"], ["Infill", "100%"],
                      ["Colore", "rossi (bianchi per 5, 10, 15, 20; oro il 25)"]],
             "why": f"Spessi {n(C['numero_inciso_mm'])} mm come il solco e più stretti di {n(C['numero_da_inserire_gioco_mm'])} mm "
                    "per lato: si premono a filo con il pollice. Se entrano lenti, una goccia di colla; se sono duri, riduci "
                    "l'espansione orizzontale nello slicer (−0,05). Il primo strato liscio finisce a vista: piatto pulito.",
             "summary": "stesi · 100% · facoltativi"},
            {"key": "filetti", "title": "Ganci e palline",
             "rows": [["Layer", "0,12"], ["Pareti", "4"], ["Infill", "100% (ganci)"], ["Orientamento", "come nello STL"]],
             "why": f"Pezzi piccoli con filetti fini (passo 1,5): layer basso. Le palline sono vuote come quelle per il gatto: "
                    f"guscio da {n(C['pallina_mm']['guscio'])} mm, filetto Ø{n(C['pallina_mm']['filetto_cresta_d'])} vicino al giunto, "
                    "collare forato (con 4 pareti il guscio esce pieno di perimetri, niente infill dentro). "
                    "La metà sopra si stampa sul giunto con l'occhiello in alto (svasatura a 45° e cupola senza supporti); "
                    "la metà sotto capovolta, sul collare; il gancio in piedi, punta del piolo sul piatto.",
             "summary": "0,12 · 4 pareti"},
            {"key": "piccoli", "title": "Stella e chiave",
             "rows": [["Pareti", "3"], ["Infill", "20%"], ["Velocità", "ridotta"]],
             "why": "Pezzi piatti: la stella ha il retro sul piatto e la linguetta nel suo stesso piano.",
             "summary": "3 pareti · 20%"},
        ],
        "note_html": "Colori del video di partenza: nastro verde, corpi verdi, tappi bianchi con i multipli di 5 rossi, tronco marrone, "
                     "base e pupazzo bianchi, cappello e occhi neri, naso giallo, cassetto rosso, regali uno verde e due rossi con i nastri del colore opposto, stella oro, chiave e ganci gialli, palline rosse.",
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
                   "<li>Pallina: vuota, passo 1,5 su Ø18 vicino al giunto, cono a 45° che centra le due metà</li>"
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
