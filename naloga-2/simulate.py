#!/usr/bin/env python3
"""
Exercise 2 – Ship Navigation Simulator

Simulates a cargo ship travelling from point A to point B,
accounting for wind drift and ship kinematic constraints:
  - Max speed:        30 km/h
  - Max acceleration:  2 km/h per minute
  - Max turn rate:     5 deg/min

Coordinates use the problem's base unit of 100 km.
Heading convention: 0 deg = East (+x), 90 deg = North (+y), counter-clockwise.

Usage:
    python simulate.py x0 y0 xk yk phi0 wind_file

    x0, y0    - start point A  [units of 100 km]
    xk, yk    - goal  point B  [units of 100 km]
    phi0      - initial heading [degrees, 0=East, 90=North]
    wind_file - path to wind data file

Example:
    python simulate.py 0 0 3 4 45 wind.txt
"""

import math
import sys

from wind import WindData
from ship_simulator import ShipSimulator


def main() -> None:
    if len(sys.argv) != 7:
        print(__doc__)
        sys.exit(1)

    try:
        start_x           = float(sys.argv[1]) * 100.0
        start_y           = float(sys.argv[2]) * 100.0
        goal_x            = float(sys.argv[3]) * 100.0
        goal_y            = float(sys.argv[4]) * 100.0
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

    print("Ship Navigation Simulator - Exercise 2")
    print("=" * 40)
    print(f"  A = ({start_x/100:.3f}, {start_y/100:.3f})  ->  B = ({goal_x/100:.3f}, {goal_y/100:.3f})  [100 km]")
    print(f"  Initial heading : {initial_heading_deg:.1f} deg")
    print(f"  A->B distance   : {route_length_km/100:.4f} units  ({route_length_km:.1f} km)")
    print(f"  Wind intervals  : {len(wind)}  (repeating)")
    print()

    log_path = "simulation_log.txt"
    print(f"  Full log        : {log_path}\n")

    sim = ShipSimulator(start_x, start_y, goal_x, goal_y, initial_heading_deg, wind)
    sim.run(log_path)


if __name__ == "__main__":
    main()
