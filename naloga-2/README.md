# Naloga 2 – Simulator plovbe ladje

## Algoritem (osnovna simulacija)

Tovorna ladja pluje od točke A do točke B v 2D ravnini (enota: 100 km). Začne iz mirovanja, izpostavljena je vetru.

Vsako minuto simulator naredi naslednje:

1. Izračuna smer proti cilju B.
2. Zavije proti tej smeri – največ 5° na minuto, torej pri večjih kotih traja več minut.
3. Pospeši do max 30 km/h. Ko je dovolj blizu, da pri zaviranju (2 km/h na minuto) še pravočasno ustavi, začne zavirati.
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

| Argument          | Opis                                                      |
|-------------------|-----------------------------------------------------------|
| `x0 y0`           | Začetna točka A (enote 100 km)                            |
| `xk yk`           | Ciljna točka B (enote 100 km)                             |
| `phi0`            | Začetna orientacija v stopinjah (0° = Vzhod, 90° = Sever) |
| `vetrna_datoteka` | Pot do datoteke z vetrnimi podatki                        |

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
       940        2.9984        3.9955       14.00             12.16      68.5         0.00477         0.001379

Arrival time  : 940 min  (15 h 40 min)
```

Stolpec "Odmik od trase" je pravokotna razdalja od idealne premice A–B.

---

## Zakaj greedy ni optimalno

Osnovna strategija (`simulate.py`) vedno usmeri nos ladje direktno proti B. Ko je veter bočen, ladja zanese v stran, se popravi, zanese spet — pot je cik-cak, ne ravna črta.

**Optimalna strategija: crab angle (kompenzacija vetra)**

Ladja se usmeri rahlo v veter, tako da je **rezultantni vektor** (motor + veter) usmerjen direktno proti B:

```
Greedy:                  Crab angle:
   B                        B
  /↑                       /↑
 / | veter                /←← veter
/←←                      /
A                         A  (nos ladje kaže levo od B,
                               veter jo potisne desno,
                               skupaj gre direktno v B)
```

Crab angle se izračuna kot:

```
w_perp = komponenta vetra pravokotno na smer A→B
alpha  = arcsin(-w_perp / hitrost_motorja)       # krab kot
desired_heading = smer_proti_B + alpha
```

Ko hitrost motorja = 0 (start, zaviranje), se krab kot ne da izračunati → ladja kaže direktno v B.

---

## Razširitev: minimalna širina koridorja

### Opis problema

Na morju so čeri in druge ladje – ladja sme pluti le znotraj varnega koridorja širine W, ki je centriran na premico A–B. Zunaj koridorja ni varno.

**Podvprašanje:** kolikšna je minimalna širina koridorja W, da ladja lahko prispe iz A v B?

Pogoj: navigacijska strategija ne sme biti umetno počasnejša samo zato, da ostane v koridorju.

### Dve strategiji — primerjava

| Strategija                | Datoteka               | Čas prihoda | Max odmik | Min koridor   |
|---------------------------|------------------------|-------------|-----------|---------------|
| Greedy (direktno v B)     | `simulate.py`          | 940 min     | 7.00 km   | **14.010 km** |
| Crab angle (kompenzacija) | `simulate_corridor.py` | 951 min     | 0.40 km   | **0.843 km**  |

Max odmik = enostranski pravokotni odmik od premice A–B. Min koridor = 2 × max odmik (greedy) oz. bisekcija (crab angle).

Primer: A = (0, 0), B = (3, 4) [100 km], wind.txt.

- Greedy zaide do **7 km** od idealne trase → potrebuje **14 km** koridor.
- Crab angle zmanjša odmik **17-krat** (7 km → 0.40 km) in potrebuje le **0.843 km** koridorja — **17-krat** ožji koridor kot greedy.
- Crab angle korekcija aktivira le ko ladja zaide v **zunanjo polovico** koridorja, da pri velikih W ne vpliva na čas plovbe.

### Implementacija koridorske simulacije

`CorridorSimulator` (v `corridor_simulator.py`) razširi `ShipSimulator` z dvema popravkoma smeri:

1. **Crab angle** — kompenzira bočni veter, da se zemeljski vektor hitrosti usmeri proti cilju.
2. **Lateralni popravek** — ko je ladja odmaknjena od sredinske črte A–B, doda proporcionalni popravek smeri nazaj proti sredini:

```
alpha        = signed_deviation / corridor_half_width   # v [-1, 1]
correction   = -MAX_LATERAL_CORRECTION_DEG * alpha      # max ±30°
goal_dir    += correction
```

Oba popravka se seštejeta v en `desired_heading`, ki ga ladja sledi z max 5°/min.

### Bisekcija minimalne širine

`find_min_corridor.py` poišče minimalni W z bisekcijo (20 iteracij ≈ natančnost ~0.01 km):

```
low = 0, high = dolžina_trase
repeat 20-krat:
    mid = (low + high) / 2
    poženemo CorridorSimulator z crab angle + corridor_half_width = mid
    če ladja prispe brez kršitve in v sprejemljivem času (≤ crab angle čas):
        high = mid   # lahko gre ožje
    sicer:
        low  = mid   # preozko
```

### Datoteke

| Datoteka                      | Opis                                                                    |
|-------------------------------|-------------------------------------------------------------------------|
| `ship_simulator.py`           | Osnovna simulacija (greedy)                                             |
| `simulate.py`                 | Vstopna točka za greedy simulacijo                                      |
| `corridor_simulator.py`       | `CorridorSimulator` – crab angle + lateralni popravek + sledenje odmiku |
| `simulate_corridor.py`        | Vstopna točka za crab angle simulacijo (analogno `simulate.py`)         |
| `find_min_corridor.py`        | Bisekcija: greedy baseline + crab angle baseline + iskanje min W        |
| `simulation_log.txt`          | Greedy log                                                              |
| `simulation_corridor_log.txt` | Crab angle log                                                          |

### Zagon

```bash
# samo crab angle simulacija:
python3 simulate_corridor.py 0 0 3 4 53 wind.txt

# primerjava + iskanje minimalnega koridorja:
python3 find_min_corridor.py 0 0 3 4 53 wind.txt
```

---

## Testne vetrne datoteke

V mapi `test-winds/`:

| Datoteka             | Opis                                      |
|----------------------|-------------------------------------------|
| `wind_zero.txt`      | Brez vetra                                |
| `wind_tailwind.txt`  | Zarepni veter 20 km/h (~53°)              |
| `wind_headwind.txt`  | Čelni veter 15 km/h (233°)                |
| `wind_crosswind.txt` | Bočni veter 25 km/h (pravokotno na traso) |
| `wind_changing.txt`  | Spremenljiv veter, 6 smeri                |
