# Naloga 2 – Simulator plovbe ladje

## Algoritem

Tovorna ladja pluje od točke A do točke B v 2D ravnini (enota: 100 km). Začne iz mirovanja, izpostavljena je vetru.

Vsako minuto simulator naredi naslednje:

1. Izračuna smer proti cilju B.
2. Zavije proti tej smeri – največ 5° na minuto, torej pri večjih kotih traja več minut.
3. Pospeši do max 30 km/h. Ko je dovolj blizu, da pri zaviranju (2 km/h na minuto) še pravočasno ustavi, začne zavirati. Razdalja zaustavljanja je v·(v+2)/(240) km (eksaktni diskretni seštevek korakov po 2 km/h).
4. Doda vetrovni vpliv iz datoteke za trenutno uro – veter se prišteje vektorsko, ne glede na orientacijo ladje. Če je plovba daljša od datoteke, se vnosi ponavljajo.
5. Posodobi položaj.
6. Preveri ali je ladja znotraj 0,5 km od B – če ja, konec.

---

## Zahteve

Python 3.10+, brez zunanjih paketov.

---

## Uporaba

```bash
python3 simulate.py x0 y0 xk yk phi0 vetrna_datoteka
```

| Argument | Opis |
|----------|------|
| `x0 y0` | Začetna točka A (enote 100 km) |
| `xk yk` | Ciljna točka B (enote 100 km) |
| `phi0` | Začetna orientacija v stopinjah (0° = Vzhod, 90° = Sever, CCW) |
| `vetrna_datoteka` | Pot do datoteke z vetrnimi podatki |

### Format vetrne datoteke

```
N   hitrost[km/h]   smer[°]
1   10              90
2   5               30
...
```

Vrstica z glavo (začne z ne-numeričnim znakom) se preskoči. Smer pove kam veter **piha** (0° = Vzhod, 90° = Sever).

---

## Izhod

V terminalu se stanje izpiše vsako uro in ob prihodu. Celoten minutni log se zapiše v `simulation_log.txt`.

## Primer

```bash
bash run_example.sh
# ali direktno:
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

Stolpec "Odmik od trase" je pravokotna razdalja od idealne premice A–B.

---

## Testne vetrne datoteke

V mapi `test-winds/`:

| Datoteka | Opis |
|----------|------|
| `wind_zero.txt` | Brez vetra |
| `wind_tailwind.txt` | Zarepni veter 20 km/h (~53°) |
| `wind_headwind.txt` | Čelni veter 15 km/h (233°) |
| `wind_crosswind.txt` | Bočni veter 25 km/h (pravokotno na traso) |
| `wind_changing.txt` | Spremenljiv veter, 6 smeri |
