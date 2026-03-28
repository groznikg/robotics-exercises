#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# run_wsl.sh – start the TurtleBot WASD teleop on Windows WSL2
# Prerequisites: WSL2 with Ubuntu, Docker Desktop with WSL2 backend,
#                or native ROS2 Jazzy installed in WSL.
# ─────────────────────────────────────────────────────────────────────────────
set -e

# WSLg provides DISPLAY automatically; fall back to :0
export DISPLAY="${DISPLAY:-:0}"

echo "[INFO] DISPLAY=$DISPLAY"

# Build image if not already built
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

# Run turtlesim + rosbridge + teleop in a single container
docker run -it --rm \
    -e DISPLAY="$DISPLAY" \
    turtle_teleop_wasd \
    /start.sh
