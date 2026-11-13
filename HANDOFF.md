# Handoff · Calendario Avvento

## Obiettivo

Rifare in Blender (UI visibile tramite il server BlenderMCP, porta 9876) un progetto stampabile simile al video
`C:\Users\matteo\Downloads\Video\New advent calendar🎄 #3dprint ... _1080p.mp4`: calendario dell'Avvento ad albero di Natale.
Poi il pacchetto solito (skill `progetto-stampa-3d`): STL in `stl/`, `blender/costruisci.py` parametrico,
`dati/geometria.json`, `guida.html` (skill `guida-stampa-3d`), README, repo git (commit solo quando l'utente lo dice).
Stampante: Anycubic Kobra S1, piatto 250 × 250 × 250, PETG. Rispondere in italiano.

## Com'è l'originale

Vedi `originale/foto_video.png` e `originale/mosaico_video.png` (fotogrammi del video, 2 al secondo).
Distributore a gravità: nastro verde a serpentina = scivolo chiuso; si carica dall'alto, si prende in basso a sinistra.
Dal retro si vedono i fondi verdi dei bussolotti (canale passante). Numeri: ramo basso 2…9 da sinistra, sopra 15…10, ecc.

## Decisioni prese con l'utente (2026-11-13)

- **Retro aperto**: canale passante da davanti a dietro, niente parete di fondo. Bordino **a 3 gradini** (4 mm, 45°)
  sia davanti sia dietro: tiene il bussolotto centrato in profondità. ("anche dietro bordato", "il fondo deve essere passante")
- **Sagoma "come prima"**: rami spessi + mezzi dischi nelle curve + cunei fra i rami (primo render). L'unione di
  inviluppi convessi (tutto pieno fra le curve) è stata **rifiutata**: "non sembra più un albero".
- **Pendenza 2°** (cuneo fra i livelli leggero, ~5 → 12 mm).
- **Bussolotti tutti uguali Ø20**, anche la 25 (rossa, numero oro).
- **Colori**: corpo dei bussolotti verde (chiaro); tappi bianchi con numero rosso; **multipli di 5 rossi** con numero
  bianco; 25 rossa con numero oro.
- **Tappo avvitato** al bussolotto: filetto passo 2, dente 0,8, gioco radiale 0,3; parete del tappo 1,3 mm.
- L'utente vuole **essere interpellato con domande** quando qualcosa non è chiaro, invece di indovinare.
- **Fermo d'uscita** alto 12 mm (sopra il centro della capsula 1).
- **Ingresso in alto**: negli ultimi 20 mm i gradini dei bordini diventano rampe morbide (`imbocco()`, un solo
  solido per l'ultimo ramo: gradini → rampa → bocca aperta).
- **Palline appese**, non davanti: gancio a vite (`P15_Gancio`: perno filettato M≈6 passo 1,5, collarino, piolo con
  gola) avvitato nel nastro; la pallina ha un occhiello in cima che si infila sul piolo e resta nella gola.
  Attacchi: fianco destro della curva alta e fianco sinistro della curva di mezzo (foro radiale orizzontale in un
  rinforzo sul profilo), sul fianco sinistro del fermo d'uscita (stesso tipo, foro orizzontale), sotto il ramo
  basso a destra (aletta sotto lo smusso, foro che entra dal davanti lungo Y). Quattro palline in tutto;
  pupazzo spostato dietro a sinistra del tronco.
- **Palline tonde Ø24 in due metà avvitate** come le palline per i gatti (`D:\3D Print\Palline Traforate`):
  sotto «vite» (cono 45° + collare filettato, si stampa capovolta sul collare), sopra «madrevite» (svasatura +
  filetto interno + occhiello, si stampa sul giunto).

## Stato attuale

`blender/costruisci.py` riscritto e funzionante nel Blender aperto (exec via MCP; in GUI costruisce solo la scena,
i file li scrive solo con `-b`). Controlli (tutti ok): canale 23 mm (gioco 3), percorso 520 mm, 25 capsule +
1 posto libero all'ingresso, nastro 181 × 136 × 57,4 (sta sul piatto, si stampa sul retro), baricentro x −1,9
col tronco a x −1, bocca capsula Ø12,8, chiave (anello R6) entra nella 25.

- Tracciato: `X_USCITA -72`, curve `[62, -58, 22]`, ingresso `-32`; 4 livelli, 3 curve a U (raggio mediana 14).
- Uscita: il canale finisce sul fermo (capsula 1); tetto del ramo basso solo dopo `TETTO_USCITA`; davanti alla
  capsula 1 il bordino è tagliato (finestra) per sfilarla in avanti.
- Tronco 52 × 57,4 × 60 con **tenone 36 × 4** che entra dal retro in una scanalatura sotto il nastro (si ferma contro
  il bordino davanti). Cassetto con serratura 3,2 × 9 e chiave come prima.
- Palline: fori Ø2,4 passanti in Y nella parete esterna delle 3 curve (filo).
- Stella con linguetta nella fessura di una cresta sul tetto del ramo alto.

Canale: **un solo solido spazzato lungo tutto il percorso** (`canale_intero()`: stazioni sui rami e ogni 3° nelle
curve, sezione a gradini nel piano (y, normale a sinistra del verso di percorrenza); "aperto" = niente bordino da quel
lato, fra stazione a gradini e aperta i gradini diventano rampe). Tagli separati per rami e curve sovrapposti davano
decine di spigoli aperti per facce dei gradini coincidenti: non tornare indietro.
Uscita rifinita: fermo spesso 9 mm alto 12,5 con raccordi R3, gancio della pallina nel suo fianco sinistro (niente
rinforzo); tetto del ramo basso con punta arrotondata e gradini in rampa per 12 mm (`RAMPA_TETTO`).

Base: **pezzo unico** con regali (rossi, `material_index` 1) e pupazzo uniti con `join_into` (affondano 0,2 mm,
li unisce lo slicer): `P12_Regalo` e `P13_Pupazzo` non esistono più (cancellare i vecchi STL quando si rigenera).
Chiave staccata dal modello: nel montaggio è sul tavolo davanti alla base.

**Rigenerato il 2026-11-13** (su richiesta dell'utente): 36 STL in `stl/`, tutti con 0 spigoli non-manifold
(l'ultimo si è chiuso inclinando di 0,6 mm il cielo del fermo), `dati/geometria.json`, `.blend`.
Gli STL del primo tentativo sono stati spostati fuori dal progetto (scratchpad della sessione), non cancellati.
`dati/scrivi_spec.py` riscritto → `dati/guida_spec.json` → `guida.html` (9 passaggi, 45 pezzi; ganci e palline
hanno rotazioni diverse, quindi una riga per copia invece di `instances`). Verificata con `shoot.py`: forma giusta,
nessun errore JavaScript. Scritti `README.md` e `.gitignore` (`*.blend1`). Nessun repo git ancora.

**Aggiornato il 2026-11-13 (dopo):** colonnine 3 mm davanti e dietro nei bordini (`COL_*`, 9 per lato) perché
il canale passante staccava i rami; si ricavano togliendole dal solido del canale (unirle al nastro dava 367
spigoli aperti). Chiave: l'utente vuole solo maniglia, nessuna serratura. Guida in alta definizione (tappi a
piena risoluzione, multipli di 5 nel gruppo «Tappi rossi»), 5,8 MB. STL rigenerati, 0 spigoli aperti.

**Numeri incisi (2026-11-13, sera):** solco 0,8 nel cielo del tappo (`NUM_H`), tappi di un colore. Numeri da inserire
facoltativi `P16_Numero_01…25` (`numero_inserto()`: rientro 0,1 con `inset_region` sulla faccia piana; l'offset della
curva FONT dava spigoli aperti), stampati capovolti. Repo `maxeo/3dprint-calendario-avvento` pubblico; guida
pubblicata su 3dprint-guide (`calendario-avvento`). La guida ha `guida_stl.js` (STL compressi) per lo zip della selezione.

**Viewer della guida alleggerito (2026-11-13, sera):** solo la vista, gli STL di stampa sono identici.
`costruisci.py` scrive in `dati/vista/` mesh con le sole superfici visibili (`viste`, `comuni`): palline = calotte
sferiche chiuse dal disco del giunto (+ occhiello), ganci e capsule senza filetto, tappi = cielo con il numero
inciso (`vista_tappo_cielo`) + corpo comune `tappo_corpo.stl` (`vista_tappo_corpo`), numeri con il font a
`resolution_u` 5 (`V_RES`). `scrivi_spec.py` le passa con `view_file`, `view_shared` (corpo dei tappi), `smooth` 35
e `cull` (tutte le mesh chiuse, anche nastro e base). Opzioni nuove della skill guida-stampa-3d (template +
`build_guide.py` + `references/spec.md`; copia dei file originali nello scratchpad della sessione). Risultato:
triangoli 296k → 86k, guida 6,8 → 1,9 MB, un fotogramma ~80 → ~34 ms (Chrome headless, canvas 862 × 520).
Isolato, un pezzo con vista leggera si mostra con lo STL di stampa (`full`, decompresso da `guida_stl.js`).
Gruppi della guida: base bianca, tronco marrone, chiave e ganci gialli, tappo 25 tra i «Tappi rossi», N25 oro
nel gruppo «Capsula 25» con il suo corpo. Sigle spente all'apertura (`"labels": False`).

**Regali staccati dalla base (2026-11-13, sera):** come nel taglio fatto dall'utente nello slicer (base.3mf con
6 connettori). `P12_Regalo` (3 copie: davanti a destra verde, `REG_VERDE`, gli altri rossi; `REG_POS`), due fori Ø3,6 × 3
sotto ogni regalo e nella base (`REG_PERNI` in diagonale), `P17_Perno_regalo` Ø3,4 × 5,6 (6 copie). Il pupazzo
resta unito alla base. Nella guida: R1–R3, PR e il passaggio «Regali sulla base».
Poi (stessa sera): verde spostato davanti a destra (`REG_VERDE = 1`). Nastri a croce `P20_Nastro_regalo` (3, si
infilano dall'alto nel solco 3,3 × 0,8 del regalo, sporgono 0,6; verdi sui regali rossi, rosso sul verde; colore per
oggetto in Blender con `material_slots[0].link = 'OBJECT'`). Pupazzo: testa piatta a 25,5 con perno Ø3 per
`P18_Cappello` (nero); `P19_Naso` (giallo) e 2 × `P21_Occhio` (neri, bottone) avvitati: filetto Ø3 passo 1 dente 0,4
gioco 0,2 (`PF_*`, `madrevite()`, `vite_codolo()`, `asse_testa()`); occhi a 48° di lato e 26° in alto, fori 2,2 e
naso 2,4: calcolato che le madreviti non si toccano e gli occhi stanno sotto la tesa. Cassetto rosso anche nella guida.
I fori della testa vanno tagliati uno per volta e cilindro + filetto uniti con un booleano: fusi con `merge` il
booleano svuotava il pupazzo.
Occhi rifatti più piccoli su richiesta: a incastro a forza (`OCCHI_D` 1,7 codolo = foro), bottone Ø2,4, a 36° di
lato e 30° in alto; solo il naso è avvitato. Pupazzo a 96 spicchi; nella guida la base non si decima (20000) e ha
`smooth` 35.
Rigenerare con Blender riscrive i `P16_Numero_*` con lo stesso contenuto in ordine diverso: `git checkout -- stl/`.

## Cosa ha funzionato

- ffmpeg: `%LOCALAPPDATA%\Microsoft\WinGet\Links`; mosaico `ffmpeg -i <video> -vf "fps=2,scale=360:-1,tile=8x4" tile_%d.png`.
- Blender: avviarlo in GUI con il .blend (`blender.exe blender/Calendario_Avvento.blend`): l'addon apre la porta
  9876 da solo (auto-start). Eseguire lo script con `exec(open(...).read(), {"__name__": "__main__"})` dentro
  `contextlib.redirect_stdout` per leggere i controlli stampati.
- Profilo 2D nel piano XZ estruso in Y; unione dei pieni con un solo booleano EXACT `use_self=True`, poi un solo
  DIFFERENCE con tutti i taglienti uniti (`merge`), `use_self=True`.
- Bordini a gradini: un unico solido per ramo/curva con `loft_multi` (sezioni successive, due sezioni alla stessa y
  = gradino). Tagliare i gradini con pezzi separati sovrapposti dava ~200 spigoli aperti.
- I rami entrano 0,6 mm (`EXT`) nelle curve: niente lamelle al raccordo.
- Filetto: `filetto()` costruisce un tubo con raggio funzione di (z − passo·θ/2π); maschio = UNION sul collo,
  femmina = DIFFERENCE nel tappo. Il tappo si gira con una **rotazione** di 180° su X (non con scala −1: lo
  specchio inverte il verso del filetto). Tappo base costruito una volta, i numeri si uniscono a copie.
- Numeri: font `ariblk.ttf`, `new_from_object` + `join_into` con `material_index`.
- Prima degli STL: `remove_doubles(1e-3)` + `dissolve_degenerate`.

## Cosa non ha funzionato

- Primo tentativo a ripiani piatti (le capsule non scendono, nastro a sbalzo su due perni).
- Volume pieno come unione di inviluppi convessi: profilo pulito ma non sembra un albero (rifiutato).
- Heredoc Python da Bash: `python3` non esiste e il fallback ha aperto la REPL interattiva bloccando la shell.
  Usare Edit/Write o `sed`.

## Prossimi passi (aggiornati)

1. Prova di stampa consigliata all'utente: un bussolotto con tappo, una pallina, un gancio, un tratto di curva.
2. `git init` + commit solo quando l'utente lo chiede (italiano, niente Co-Authored-By); poi eventuale pubblicazione
   nel repo delle guide (vedi memoria "Pubblicare le guide").

## Prossimi passi (storici, già fatti)

1. Chiudere l'ultimo spigolo aperto del nastro (fermo d'uscita).
2. Far confermare all'utente la forma in Blender (vista davanti e dietro); chiedere se vanno bene palline, cresta
   della stella, finestra della capsula 1.
3. Rigenerare con `blender -b --factory-startup --python blender/costruisci.py` (STL + geometria.json + .blend);
   eliminare da `stl/` gli STL non più prodotti se ce ne sono.
4. Prova di stampa consigliata: un bussolotto + un tappo (filetto) e un pezzo di curva per lo scorrimento.
5. Aggiornare `dati/scrivi_spec.py` (caricare dall'ingresso in alto **prima la 1, ultima la 25**; prendere
   dall'uscita in basso a sinistra; tappi avvitati; tenone del tronco dal retro), eseguirlo, `build_guide.py`,
   screenshot con `shoot.py`, README, `.gitignore`. `git init` + commit solo su richiesta (italiano, niente Co-Authored-By).
