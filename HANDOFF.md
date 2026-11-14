# Handoff · Calendario Avvento

## Obiettivo

Calendario dell'Avvento ad albero di Natale, stampabile, rifatto in Blender da un video
(`originale/foto_video.png`, `originale/mosaico_video.png`). È un distributore a gravità: un nastro verde a serpentina
fa da scivolo chiuso. Si carica dall'alto e si prende in basso a sinistra. Il pacchetto è quello solito (skill
`progetto-stampa-3d`):
- STL in `stl/`
- `blender/costruisci.py` parametrico
- `dati/geometria.json`
- `guida.html` (skill `guida-stampa-3d`)
- README
- repo git `maxeo/3dprint-calendario-avvento`

Stampante: Anycubic Kobra S1, piatto 250 × 250. Ogni pezzo deve stare in **230 × 230** ("stai un po' sotto").
Materiale PETG.

Regole per l'utente:
- Rispondere in italiano.
- Fare domande quando qualcosa non è chiaro.
- Mostrare le modifiche nel Blender aperto prima di rigenerare.
- Commit solo su richiesta: in italiano, senza Co-Authored-By, senza force-push.

## Stato attuale (2026-11-14): tutto fatto e pubblicato

**Ingrandito per il Ferrero Rocher.** Il Ferrero misura circa 30 mm (nessun dato ufficiale) e va nella sola stagnola.
- Bussolotti: `CAP_D = 42` (bocca Ø34,8), `CORPO_L = 32`, spazio interno alto 36,4 mm.
- Albero: 7 livelli, tracciato `X_USCITA=-75`, `X_CURVE=[68,-55,56,-42,42,-27]`, `X_INGRESSO=0`.
- Percorso 1126,6 mm: 25 capsule più 55 mm liberi all'ingresso. Altezza circa 526 mm con la stella.
- Base 230 × 150. Pupazzo ×1,6. Regali `REG_L=22`. Palline Ø36 (×1,5). Stella `RS=36`.

**Nastro in 10 pezzi**, perni stampati nel pezzo (niente perni staccati: `P22` e `PERNI_N` eliminati):
- `P01_Nastro_1..4`: corpi, cioè le sole pareti del canale. Tagli a metà delle curve di destra (`TAGLI=[0,2,4]`),
  a scalino (`SCALINI`, `corpo_di()`): il muro fra il ramo k e il k+1 va sempre intero nel corpo sopra. Così il
  corpo 1 è un pezzo solo; i corpi 2–4 restano due metà incastrate (i due "pettini" divisi dal canale passante),
  tenute insieme dai telai.
- `P23_Telaio_davanti_1..3` e `P24_Telaio_dietro_1..3`: bordini, colonnine e bottoni. Tagli a metà delle curve di
  sinistra (`TAGLI_TELAI=[1,3]`). Ogni telaio scavalca un taglio dei corpi.
- Piani di separazione: `Y_TF=Y_LIP+0.3` e `Y_TD=Y_LIP_DIETRO-0.3`.
- Tronco liscio (venature tolte il 2026-11-14): si stampa senza supporti. Base bianca e bussolotti già stampati:
  non toccarli.
- Perni Ø2,6 × 3 in fori Ø3 × 3,4 (`PT_*`), 40 davanti e 40 dietro. Davanti stanno sui corpi, dietro sui telai.
  Tutti i pezzi si stampano con `Rx(-90)`, quindi i perni restano sempre in alto.
- `SMUSSO_TAGLIO=0.8` sul canale del corpo sotto, dove due corpi si toccano.
- Il pezzo più grande è 230,5 mm. Tutti i pezzi hanno 0 spigoli non-manifold. Nessun perno volante (controllo
  union-find sui componenti degli STL).

**Palline:** 10, tutte rosse, con il gancio a piolo lungo (`G_PUNTA=-24`).
- 6 sui fianchi delle curve: `FIANCHI` (indice curva, dz).
- 2 davanti su bottoni: `DAVANTI`, `BOTTONE=6`.
- 1 sotto il ramo basso, anche questa con un bottone davanti.
- 1 sul fermo d'uscita.
- Distanza minima dal nastro: 3,2 mm.

**Guida:** 108 pezzi, 15 passaggi, nessun errore JavaScript. I passaggi del nastro sono tre: corpi sul tronco,
telai dietro, telai davanti.

**Commit:**
- Progetto `e85016b` «Ingranditi bussolotti e albero per il Ferrero Rocher», pushato.
- 3dprint-guide `c74d1ad` «Aggiornata la guida del Calendario ingrandito», pushato.
- Guida online: https://maxeo.github.io/3dprint-guide/calendario-avvento/guida.html

## Come si lavora

- **Rigenerare:**
  `"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python blender/costruisci.py`.
  Questo scrive gli STL, `geometria.json`, `dati/vista/` e il `.blend`. Poi eliminare da `stl/` gli STL non più prodotti.
- **Ripristinare i numeri:** rigenerare riscrive i `P16_Numero_*` in ordine diverso. Riportarli com'erano con
  `git checkout -- stl/P16_*`.
- **Mostrare in Blender:**
  - Aprire la GUI col `.blend`; l'addon MCP apre da solo la porta 9876.
  - Eseguire lo script con `exec(open(...).read(), {"__name__": "__main__"})`.
  - L'exec può andare in timeout ("No data received") ma finisce lo stesso.
  - I risultati stanno in `builtins._cal_out` e `builtins._cal_g`.
- **Generare la guida:**
  1. `python dati/scrivi_spec.py`
  2. `python ~/.claude/skills/guida-stampa-3d/scripts/build_guide.py dati/guida_spec.json`
  3. `shoot.py` per screenshot ed errori JavaScript.
- **Pubblicare:**
  1. In `D:\3D Print\3dprint-guide` lanciare `./aggiorna_guide.sh`.
  2. In `index.html` ripristinare le date `data-aggiornata` di skinkocchiali e supporto-tablet, che lo script cambia
     senza motivo.
  3. Commit e push.

## Cosa ha funzionato

- **Booleani:**
  - Booleani EXACT con taglienti **disgiunti** (un box per lato) e `self_int=True`.
  - Prima un'unica UNION dei pieni, poi un'unica DIFFERENCE dei taglienti uniti con `merge`.
- **Canale:** un unico solido spazzato lungo tutto il percorso (`canale_intero()`). Le colonnine si ricavano
  togliendole dal solido del canale.
- **Buchi dopo i tagli:** i piccoli buchi ai nuclei delle curve a U si chiudono all'export con
  `bmesh.ops.holes_fill(..., sides=16)`.
- **Posizione dei perni:** `dentro()` usa BVH `find_nearest` per il margine, poi tre raggi obliqui con voto a
  maggioranza e dedup dei doppi colpi. Il candidato deve stare dentro sia il corpo (6 mm dalla faccia) sia il telaio
  (metà spessore). La scelta è greedy, con passo 30.
- **Baricentro:** si calcola con `baricentro_x()` prima di dividere il nastro.
- **Filetti:**
  - Il tappo si gira con una rotazione, mai con uno specchio: lo specchio inverte il verso del filetto.
  - I fori della testa del pupazzo vanno tagliati uno alla volta.
- **Capienza:** simulazione del percorso nello scratchpad (`percorso.py`) prima di toccare il modello.

## Cosa non ha funzionato

- **INTERSECT EXACT con tolleranza:** svuotava i pezzi.
- **Box di taglio sovrapposti fusi in un solo tagliente:** davano geometria spazzatura.
- **Pulizia della mesh prima dei tagli:** rompeva i booleani.
- **`dentro()` con un solo raggio, o col segno della normale:** falsi positivi vicino al tetto inclinato di 2°.
  Ne uscivano perni volanti.
- **Ganci e bottoni sui piani di taglio dei telai:** spezzavano i telai. Sono stati spostati sulle pareti delle curve
  di destra.
- **Finestra e scanalatura fino al piano del telaio:** lasciavano lamelle da 0,2–0,3 mm. Ora arrivano a
  `Y_LIP+0.8/0.9`.
- **Taglio dei telai alla curva 5:** staccava la striscia in cima, quindi è stato tolto.
- **Primi tentativi rifiutati:** il primo tentativo a ripiani piatti e la sagoma fatta di inviluppi convessi
  ("non sembra un albero").
- **Python in heredoc da Bash:** `python3` non esiste. Usare Edit/Write o script nello scratchpad.

## Prossimi passi

1. Aspettare il riscontro dell'utente sulla guida pubblicata e sulle stampe.
2. Prova di stampa consigliata: un telaio piccolo più il suo corpo, per sentire come entrano i perni. Se entrano duri,
   aumentare la compensazione dei fori di 0,1 o regolare `PT_FORO`. Poi un bussolotto con tappo e un Ferrero dentro.
3. Peso del nastro: circa 785 g di PETG in totale.
