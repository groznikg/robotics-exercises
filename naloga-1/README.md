# TurtleBot WASD Teleop – ROS2 Jazzy

WASD upravljanje turtlesim želve, napisano v C#. Teče v Dockerju, tako da ni treba nameščati ROS2 lokalno.

Testirano na macOS, Windows in Linux sta nepreverjena.

---

## Kaj rabiš

### macOS

1. **Docker Desktop** – če ga še nimaš, ga prenesi in zaženi

2. **XQuartz** – brez tega se grafično okno ne odpre:
   ```bash
   brew install --cask xquartz
   ```
   > Po namestitvi se moraš odjaviti in znova prijaviti, drugače XQuartz ne bo deloval.

3. V XQuartz → Preferences → Security obkljukaj **"Allow connections from network clients"** in ga znova zaženi.

### Windows (WSL2)

1. WSL2 + Ubuntu:
   ```powershell
   # kot Administrator
   wsl --install
   ```

2. Docker Desktop z WSL2 – med namestitvijo izberi "Use WSL2 based engine", nato v Settings → Resources → WSL Integration omogoči svojo Ubuntu distribucijo.

3. WSLg (GUI podpora) je vgrajen v Windows 11 in 10 21H2+, `DISPLAY` se nastavi sam.

### Linux

```bash
sudo apt install docker.io docker-compose-plugin
sudo usermod -aG docker $USER  # potem se odjavi in prijavi
```

---

## Zagon

### macOS
```bash
cd /pot/do/Robotics
./run_mac.sh
```

Skripta sama preveri XQuartz, nastavi X11 dostop in zgradi sliko ob prvem zagonu (~5–10 min).

### Windows (WSL2)
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

## Tipke

| Tipka | Akcija |
|-------|--------|
| `W` | Naprej |
| `S` | Nazaj |
| `A` | Rotacija levo |
| `D` | Rotacija desno |
| `Q` | Izhod |

Karkoli drugega pošlje stop.

---

## Sprememba tipk / hitrosti

Uredi `ros2_ws/src/turtle_teleop_wasd/config/keybindings.json`:

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

Shrani in znova zaženi `docker compose up`.

---

## Struktura projekta

```
.
├── Dockerfile                        # ROS2 Jazzy + turtlesim + teleop paket
├── docker-compose.yml                # turtlesim (GUI) + teleop (tipkovnica)
├── entrypoint.sh                     # nastavi ROS2 okolje
├── run_mac.sh
├── run_wsl.sh
├── README.md
└── ros2_ws/
    └── src/
        └── turtle_teleop_wasd/
            └── TurtleTeleop/
                ├── Program.cs          # glavna logika
                ├── KeyBindings.cs      # branje konfiguracije
                ├── Terminal.cs         # raw terminal I/O
                ├── TurtleTeleop.csproj
                └── config/
                    └── keybindings.json
```

---

## Kako deluje

turtlesim teče kot ena Docker storitev, teleop kot druga. C# aplikacija terminal postavi v raw mode, jih pretvori v `geometry_msgs/Twist` sporočila in jih pošlje prek rosbridge WebSocket-a na `ws://localhost:9090`.

---

## Pogoste težave

| Težava | Rešitev |
|--------|---------|
| `Cannot connect to Docker daemon` | Docker Desktop še ni zagnan |
| `Unable to find application named 'XQuartz'` | `brew install --cask xquartz`, nato se odjavi in prijavi |
| Okno turtlesim se ne odpre | XQuartz → Preferences → Security → "Allow connections from network clients" |
| Tipkovnica ne reagira | Klikni na teleop terminal da dobi fokus |
| `xhost: command not found` | XQuartz ga namesti v `/opt/X11/bin/xhost` – skripta to že upošteva |
