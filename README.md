# Calendario dell'Avvento · albero a scivolo

Albero di Natale da stampare in PETG che fa da calendario dell'Avvento: il nastro verde è uno scivolo chiuso a
serpentina. I 25 bussolotti (Ø42, tappo numerato a vite: dentro ci sta un Ferrero Rocher) si caricano dall'ingresso in alto, prima la 1 e per ultima
la 25, scendono da soli e ogni giorno si sfila quello in basso a sinistra. Il 25 contiene la chiave del cassetto
nascosto nel tronco.

**Guida di stampa e montaggio:** https://maxeo.github.io/3dprint-guide/calendario-avvento/guida.html

Oppure apri **[guida.html](guida.html)** (offline) per la vista 3D, i passaggi di montaggio e la lista di stampa.

## Pezzi (`stl/`)

| File | Pezzo | Quantità |
|---|---|---|
| P01_Nastro_1…4 | corpi del nastro (pareti del canale), uno per livello, si stampano sul retro | 1 ciascuno |
| P23_Telaio_davanti_1…3, P24_Telaio_dietro_1…3 | telai con bordini e colonnine, perni stampati nel pezzo | 1 ciascuno |
| P02_Corpo_capsula | corpo dei bussolotti 1–24 | 24 |
| P03_Tappo_01…24 | tappi a vite con il numero inciso | 1 ciascuno |
| P04_Corpo_capsula_25, P05_Tappo_25 | bussolotto 25 (rosso) | 1 |
| P06_Tronco, P07_Cassetto | tronco con tenone, cassetto con serratura | 1 |
| P08_Chiave | chiave del cassetto | 1 |
| P09_Stella | stella | 1 |
| P10_Pallina_sopra, P14_Pallina_sotto | palline Ø36 in due metà avvitate | 10 |
| P15_Gancio | gancio a vite per appendere le palline | 10 |
| P16_Numero_01…25 | numeri da inserire nel solco dei tappi (facoltativi, altro colore) | 1 ciascuno |
| P11_Base | base con il pupazzo e i fori dei regali | 1 |
| P12_Regalo | regalo con due fori sotto e il solco del nastro (uno verde, due rossi) | 3 |
| P17_Perno_regalo | perno che ferma il regalo sulla base | 6 |
| P20_Nastro_regalo | nastro a croce da infilare nel solco del regalo (due verdi, uno rosso) | 3 |
| P18_Cappello | cappello nero del pupazzo, sul perno in cima alla testa | 1 |
| P19_Naso, P21_Occhio | naso giallo avvitato (filetto Ø3 passo 1), occhi neri Ø2,4 a incastro | 1 + 2 |

Stampante di riferimento: Anycubic Kobra S1 (piatto 250 × 250). Ogni pezzo sta in 230 × 230 mm; nessuno richiede supporti.

## Rigenerare

```
"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python blender/costruisci.py
<python> dati/scrivi_spec.py
<python> <skill guida-stampa-3d>/scripts/build_guide.py dati/guida_spec.json
```

`blender/costruisci.py` è parametrico (misure in cima) e scrive il `.blend`, gli STL e `dati/geometria.json` con i
controlli (gioco del canale, pendenza, capienza, filetti, chiave). La guida legge i numeri da `geometria.json`.
