#!/usr/bin/env python3
"""
Exercise 2 – Crab-angle corridor simulation

Simulates the ship using crab-angle wind compensation (CorridorSimulator).
The ship steers so that its ground-velocity vector points directly toward B,
minimising lateral deviation from the A–B line.

Usage:
    python simulate_corridor.py x0 y0 xk yk phi0 wind_file

Example:
    python simulate_corridor.py 0 0 3 4 53 wind.txt
"""

import math
import sys

from wind import WindData
from corridor_simulator import CorridorSimulator


def main() -> None:
    if len(sys.argv) != 7:
        print(__doc__)
        sys.exit(1)

    try:
        start_x             = float(sys.argv[1]) * 100.0
        start_y             = float(sys.argv[2]) * 100.0
        goal_x              = float(sys.argv[3]) * 100.0
        goal_y              = float(sys.argv[4]) * 100.0
        initial_heading_deg = float(sys.argv[5])
    except ValueError:
        print("Error: numeric arguments expected for coordinates and heading.")
        sys.exit(1)

    try:
        wind = WindData(sys.argv[6])
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    route_length_km = math.hypot(goal_x - start_x, goal_y - start_y)

    print("Ship Navigation Simulator - Corridor (crab-angle)")
    print("=" * 50)
    print(f"  A = ({start_x/100:.3f}, {start_y/100:.3f})  ->  B = ({goal_x/100:.3f}, {goal_y/100:.3f})  [100 km]")
    print(f"  Initial heading : {initial_heading_deg:.1f} deg")
    print(f"  A->B distance   : {route_length_km/100:.4f} units  ({route_length_km:.1f} km)")
    print(f"  Wind intervals  : {len(wind)}  (repeating)")
    print()

    log_path = "simulation_corridor_log.txt"
    print(f"  Full log        : {log_path}\n")

    sim = CorridorSimulator(start_x, start_y, goal_x, goal_y, initial_heading_deg, wind)
    sim.run(log_path)


if __name__ == "__main__":
    main()
