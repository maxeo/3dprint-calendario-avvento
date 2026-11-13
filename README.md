# Calendario dell'Avvento · albero a scivolo

Albero di Natale da stampare in PETG che fa da calendario dell'Avvento: il nastro verde è uno scivolo chiuso a
serpentina. I 25 bussolotti (Ø20, tappo numerato a vite) si caricano dall'ingresso in alto, prima la 1 e per ultima
la 25, scendono da soli e ogni giorno si sfila quello in basso a sinistra. Il 25 contiene la chiave del cassetto
nascosto nel tronco.

**Guida di stampa e montaggio:** https://maxeo.github.io/3dprint-guide/calendario-avvento/guida.html

Oppure apri **[guida.html](guida.html)** (offline) per la vista 3D, i passaggi di montaggio e la lista di stampa.

## Pezzi (`stl/`)

| File | Pezzo | Quantità |
|---|---|---|
| P01_Nastro | nastro a scivolo, si stampa sul retro | 1 |
| P02_Corpo_capsula | corpo dei bussolotti 1–24 | 24 |
| P03_Tappo_01…24 | tappi a vite con il numero inciso | 1 ciascuno |
| P04_Corpo_capsula_25, P05_Tappo_25 | bussolotto 25 (rosso) | 1 |
| P06_Tronco, P07_Cassetto | tronco con tenone, cassetto con serratura | 1 |
| P08_Chiave | chiave del cassetto | 1 |
| P09_Stella | stella | 1 |
| P10_Pallina_sopra, P14_Pallina_sotto | palline in due metà avvitate | 4 |
| P15_Gancio | gancio a vite per appendere le palline | 4 |
| P16_Numero_01…25 | numeri da inserire nel solco dei tappi (facoltativi, altro colore) | 1 ciascuno |
| P11_Base | base con regali e pupazzo, pezzo unico | 1 |

Stampante di riferimento: Anycubic Kobra S1 (piatto 250 × 250). Nessun pezzo richiede supporti.

## Rigenerare

```
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python blender/costruisci.py
<python> dati/scrivi_spec.py
<python> <skill guida-stampa-3d>/scripts/build_guide.py dati/guida_spec.json
```

`blender/costruisci.py` è parametrico (misure in cima) e scrive il `.blend`, gli STL e `dati/geometria.json` con i
controlli (gioco del canale, pendenza, capienza, filetti, chiave). La guida legge i numeri da `geometria.json`.
