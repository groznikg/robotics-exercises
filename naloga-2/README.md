# Naloga 2 – Simulator plovbe ladje

## Algoritem (1. del)

### Opis problema
Tovorna ladja pluje od točke **A** do točke **B** v 2D ravnini (enota: 100 km).
Začne iz mirovanja in je izpostavljena vetru, ki premika njeno efektivno hitrost.

### Krmilna zanka (minutni intervali)

Ladja začne pri točki A v mirovanju z začetno orientacijo. Vsako minuto izvede naslednje korake:

1. **Določi željeno smer** — iz trenutnega položaja izračuna kot, ki kaže direktno proti cilju B.

2. **Prilagodi smer plovbe** — zavije proti željeni smeri, vendar največ 5° na minuto. Če je razlika večja, se zavijanje razporedi čez več minut.

3. **Prilagodi hitrost** — če je ladja dovolj blizu cilja, da bo pri polnem zaviranju še pravočasno ustavila, začne zavirati (zmanjša hitrost za 2 km/h). Sicer pospeši do maksimalnih 30 km/h.

4. **Upošteva veter** — iz datoteke prebere vetrovni vpliv za trenutno uro. Veter se vektorsko doda hitrosti ladje — ladjo odriva v smeri pihanja ne glede na njeno orientacijo. Če je plovba daljša od datoteke, se vnosi ponavljajo ciklično.

5. **Posodobi položaj** — na podlagi trenutne smeri, hitrosti in vetra izračuna nov položaj po eni minuti.

6. **Preveri prihod** — ko se ladja dovolj približa točki B (manj kot 0,5 km), je plovba zaključena in program izpiše skupni čas potovanja.

**Razdalja zaustavljanja** se izračuna iz kinematike diskretnega zaviranja: pri hitrosti v in pojemku 2 km/h na minuto ladja potrebuje v²/240 km za zaustavitev.

---

## Zahteve

- Python 3.10+  (brez zunanjih paketov)

---

## Uporaba

```bash
python3 simulate.py x0 y0 xk yk phi0 vetrna_datoteka
```

| Argument         | Opis                                                        |
|------------------|-------------------------------------------------------------|
| `x0 y0`          | Začetna točka A  (enote 100 km)                            |
| `xk yk`          | Ciljna točka B  (enote 100 km)                             |
| `phi0`           | Začetna orientacija v stopinjah (0° = Vzhod, 90° = Sever, CCW) |
| `vetrna_datoteka`| Pot do datoteke z vetrnimi podatki                         |

### Format vetrne datoteke

```
N   hitrost[km/h]   smer[°]
1   10              90
2   5               30
...
```

- Glava (začne z ne-numeričnim znakom) se samodejno preskoči.
- Smer: kam veter **piha** (0° = Vzhod, 90° = Sever).

---

## Izhod

### Terminal
Stanje ladje se izpisuje **vsako uro (60 minut)** in ob prihodu.

### Dnevniška datoteka
Celoten **minutni log** se samodejno zapiše v `simulation_log.txt`.

## Primer zagona

```bash
bash run_example.sh
# ali neposredno:
python3 simulate.py 0 0 3 4 53 wind.txt
```

```
       Čas    Pozicija X    Pozicija Y     Hitrost  Dejanska hitrost      Smer   Razdalja do B   Odmik od trase
     [min]      [100 km]      [100 km]      [km/h]            [km/h]       [°]        [100 km]         [100 km]
---------------------------------------------------------------------------------------------------------------
         0        0.0000        0.0000        0.00              0.00      53.0         5.00000         0.000000
        60        0.1604        0.3109       30.00             38.41      52.4         4.65537         0.058215
       ...
       940        2.9989        3.9968       16.00             14.16      68.7         0.00344         0.001040

Arrival time  : 940 min  (15 h 40 min)
```

Stolpec **Odmik od trase** prikazuje pravokotno razdaljo ladje od idealne premice A–B.

---

## Testne vetrne datoteke

Mapa `test-winds/` vsebuje pripravljene scenarije za testiranje:

| Datoteka            | Opis                                      |
|---------------------|-------------------------------------------|
| `wind_zero.txt`     | Brez vetra                                |
| `wind_tailwind.txt` | Zarepni veter 20 km/h (~53°)              |
| `wind_headwind.txt` | Čelni veter 15 km/h (233°)               |
| `wind_crosswind.txt`| Bočni veter 25 km/h (pravokotno na traso) |
| `wind_changing.txt` | Spremenljiv veter, 6 smeri               |
