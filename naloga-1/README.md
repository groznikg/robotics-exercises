# TurtleBot WASD Teleop – ROS2 Jazzy

Upravljanje želve s tipkovnico WASD za `turtlesim`, implementirano v **C#** na **ROS2 Jazzy Jalisco**.
Deluje v Dockerju – lokalna namestitev ROS2 ni potrebna. Podprti sistemi: **macOS**, **Linux** in **Windows WSL2**.

---

## Predpogoji

### macOS - Testirano

1. **Docker Desktop**
   - Prenesi in namesti z https://www.docker.com/products/docker-desktop/
   - Odpri Docker Desktop in počakaj, da se prikaže "Docker Desktop is running" (ikona kita v menijski vrstici)

2. **XQuartz** (X11 strežnik – potreben za prikaz grafičnega okna turtlesim)
   ```bash
   brew install --cask xquartz
   ```
   > **Pomembno:** Po namestitvi XQuartz se moraš **odjaviti in znova prijaviti**.
   > XQuartz se registrira pri macOS window serverju ob prijavi – brez tega koraka ne bo deloval.

3. **Varnostna nastavitev XQuartz** (dovoli omrežne povezave)
   - Odpri XQuartz → Preferences → zavihek Security
   - Obkljukaj **"Allow connections from network clients"**
   - Znova zaženi XQuartz

### Windows (WSL2) - Nepreverjeno

1. **WSL2 z Ubuntu**
   ```powershell
   # Zaženi v PowerShell kot Administrator
   wsl --install
   # Ko se zahteva, znova zaženi računalnik
   ```

2. **Docker Desktop z WSL2 zaledjem**
   - Prenesi z https://www.docker.com/products/docker-desktop/
   - Med namestitvijo omogoči "Use WSL2 based engine"
   - V Docker Desktop → Settings → Resources → WSL Integration → omogoči svojo Ubuntu distribucijo

3. **WSLg** (podpora za GUI – vgrajena v Windows 11 in Windows 10 21H2+)
   - Dodatnih korakov ni; `DISPLAY` se znotraj WSL nastavi samodejno

### Linux - Nepreverjeno

1. **Docker** + **docker compose plugin**
   ```bash
   sudo apt install docker.io docker-compose-plugin
   sudo usermod -aG docker $USER   # po tem se odjavi in znova prijavi
   ```

---

## Hiter zagon

### macOS
```bash
cd /pot/do/Robotics
./run_mac.sh
```

Skripta bo:
- Preverila, ali je XQuartz nameščen
- Zagnala XQuartz, če še ne teče
- Zaznala IP gostitelja in dovolila Docker dostop do X11
- Zgradila Docker sliko (samo ob prvem zagonu, ~5–10 min)
- Zagnala GUI turtlesim + terminal za upravljanje

### Windows (WSL2 terminal)
```bash
cd /pot/do/Robotics
./run_wsl.sh
```

### Linux
```bash
export DISPLAY=:0
xhost +local:docker
docker compose up
```

---

## Upravljanje

| Tipka | Ukaz |
|-------|------|
| `W` | Naprej |
| `S` | Nazaj |
| `A` | Rotacija levo |
| `D` | Rotacija desno |
| `Q` | Izhod |

Vsaka druga tipka pošlje ukaz **stop** (ničelna hitrost).

---

## Nastavitev tipk

Uredi datoteko `ros2_ws/src/turtle_teleop_wasd/config/keybindings.json`:

```json
{
  "key_forward":   "w",
  "key_backward":  "s",
  "key_left":      "a",
  "key_right":     "d",
  "key_quit":      "q",
  "linear_speed":  2.0,
  "angular_speed": 2.0
}
```

Ponovnega prevajanja ni potrebno – datoteka je ob zagonu priključena v vsebnik. Samo uredi in znova zaženi:
```bash
docker compose up
```

---

## Struktura projekta

```
.
├── Dockerfile                        # Slika ROS2 Jazzy + turtlesim + teleop paket
├── docker-compose.yml                # Storitve: turtlesim (GUI) + teleop (tipkovnica)
├── entrypoint.sh                     # Nastavi ROS2 okolje znotraj vsebnika
├── run_mac.sh                        # Zaganjalnik za macOS
├── run_wsl.sh                        # Zaganjalnik za Windows WSL2
├── README.md                         # Ta datoteka
└── ros2_ws/
    └── src/
        └── turtle_teleop_wasd/
            └── TurtleTeleop/
                ├── Program.cs          # Glavna logika upravljanja
                ├── KeyBindings.cs      # Nalaganje konfiguracije
                ├── Terminal.cs         # Neobdelani terminalski V/I
                ├── TurtleTeleop.csproj
                └── config/
                    └── keybindings.json  # Konfiguracija tipk in hitrosti
```

---

## Kako deluje

1. Storitev **turtlesim** zažene standardni ROS2 grafični simulator želve.
2. Storitev **teleop** zažene vozlišče `turtle_teleop_wasd`, ki:
   - Terminal preklopi v **raw način**, da se posamezni pritiski tipk berejo brez pritiska Enter.
   - Vsak pritisk tipke preslika v sporočilo `geometry_msgs/Twist` na temi `/turtle1/cmd_vel`.
   - Nastavitve tipk in hitrosti se ob zagonu naložijo iz `keybindings.json`.
3. Aplikacija C# se poveže z **rosbridge** (WebSocket na vratih 9090) za objavo sporočil hitrosti brez izvornih RCL vezav.

---

## Odpravljanje težav

| Težava | Rešitev |
|--------|---------|
| `Cannot connect to Docker daemon` | Odpri Docker Desktop in počakaj, da se popolnoma zažene |
| `Unable to find application named 'XQuartz'` | Zaženi `brew install --cask xquartz`, nato se odjavi in znova prijavi |
| Okno turtlesim se ne prikaže | XQuartz → Preferences → Security → omogoči "Allow connections from network clients", znova zaženi XQuartz |
| Tipkovnica ne deluje | Klikni okno terminala teleop, da mu daš fokus |
| `xhost: command not found` | XQuartz ga namesti v `/opt/X11/bin/xhost`, kar privzeto ni v PATH – skripta samodejno uporablja polno pot |
