#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# run_mac.sh – start the TurtleBot WASD teleop on macOS via Docker + XQuartz
# ─────────────────────────────────────────────────────────────────────────────
set -e

# 1. Make sure XQuartz is installed and running (needed for GUI)
XQUARTZ_APP="/opt/X11/bin/Xquartz"
if [ ! -f "$XQUARTZ_APP" ] && [ ! -d "/Applications/Utilities/XQuartz.app" ]; then
    echo "[ERROR] XQuartz not found. Install it first:"
    echo "        brew install --cask xquartz"
    echo "        Then log out and back in once, and re-run this script."
    exit 1
fi

if ! pgrep -x "quartz-wm" > /dev/null 2>&1 && ! pgrep -x "Xquartz" > /dev/null 2>&1; then
    echo "[INFO] Starting XQuartz..."
    open -a /Applications/Utilities/XQuartz.app 2>/dev/null || open -a XQuartz
    echo "[INFO] Waiting for XQuartz to start..."
    sleep 5
fi

# 2. Allow Docker to connect to the X server
IP=$(ifconfig en0 | grep "inet " | awk '{print $2}')
if [ -z "$IP" ]; then
    IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
fi
echo "[INFO] Host IP: $IP"

# xhost needs DISPLAY pointed at the local XQuartz before it can run
export DISPLAY=:0
XHOST="/opt/X11/bin/xhost"
"$XHOST" + "$IP"
echo "[INFO] X11 access granted to $IP"

export DISPLAY="$IP:0"

# 3. Build image if not already built
if ! docker image inspect turtle_teleop_wasd > /dev/null 2>&1; then
    echo "[INFO] Building image (first time)..."
    docker compose build
fi

echo ""
echo "==========================================="
echo "  Controls:  W=forward  S=backward"
echo "             A=rotate L  D=rotate R"
echo "  Press  q  to quit"
echo "==========================================="
echo ""

# 4. Run turtlesim + teleop in a single container (avoids DDS inter-container issues)
docker run -it --rm \
    -e DISPLAY="$IP:0" \
    turtle_teleop_wasd \
    /start.sh
