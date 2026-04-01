#!/usr/bin/env python3
"""
Exercise 2 – Minimum corridor width finder

Runs greedy and crab-angle simulations for comparison, then uses binary search
to find the narrowest corridor (centred on A–B) in which the crab-angle
strategy can complete the journey.

Usage:
    python find_min_corridor.py x0 y0 xk yk phi0 wind_file

Example:
    python find_min_corridor.py 0 0 3 4 53 wind.txt
"""

import math
import sys

from wind import WindData
from ship_simulator import ShipSimulator
from corridor_simulator import CorridorSimulator

BISECT_ITERATIONS = 20      # ~1 m precision after 20 halvings of a 500 km range


def _run_silent(sim, time_limit_min: int = 500_000) -> None:
    """Step through a simulation without printing."""
    while True:
        if math.hypot(sim.goal_x - sim.x, sim.goal_y - sim.y) < sim.ARRIVAL_KM:
            break
        sim._step()
        if sim.elapsed_min > time_limit_min:
            break


def run_greedy(start_x, start_y, goal_x, goal_y, heading, wind_path) -> tuple[int, float]:
    """Run greedy simulation with logging. Returns (elapsed_min, max_deviation_km)."""
    wind = WindData(wind_path)
    sim  = ShipSimulator(start_x, start_y, goal_x, goal_y, heading, wind)
    sim.run("simulation_log.txt")
    return sim.elapsed_min, sim.max_deviation_km


def run_crab(start_x, start_y, goal_x, goal_y, heading, wind_path) -> tuple[int, float]:
    """Run crab-angle simulation with logging. Returns (elapsed_min, max_deviation_km)."""
    wind = WindData(wind_path)
    sim  = CorridorSimulator(start_x, start_y, goal_x, goal_y, heading, wind)
    sim.run("simulation_corridor_log.txt")
    return sim.elapsed_min, sim.max_deviation_km


def bisect_min_corridor(start_x, start_y, goal_x, goal_y,
                        heading, wind_path, time_limit_min) -> float:
    """Return minimum corridor half-width [km] via binary search using crab-angle strategy."""
    low  = 0.0
    high = math.hypot(goal_x - start_x, goal_y - start_y)

    for _ in range(BISECT_ITERATIONS):
        mid  = (low + high) / 2.0
        wind = WindData(wind_path)
        sim  = CorridorSimulator(start_x, start_y, goal_x, goal_y, heading, wind,
                                 corridor_half_width_km=mid)
        _run_silent(sim, time_limit_min=time_limit_min)
        feasible = (not sim.corridor_violated) and (sim.elapsed_min <= time_limit_min)
        if feasible:
            high = mid
        else:
            low  = mid

    return high


def main() -> None:
    if len(sys.argv) != 7:
        print(__doc__)
        sys.exit(1)

    try:
        start_x = float(sys.argv[1]) * 100.0
        start_y = float(sys.argv[2]) * 100.0
        goal_x  = float(sys.argv[3]) * 100.0
        goal_y  = float(sys.argv[4]) * 100.0
        heading = float(sys.argv[5])
    except ValueError:
        print("Error: numeric arguments expected for coordinates and heading.")
        sys.exit(1)

    wind_path = sys.argv[6]
    route_km  = math.hypot(goal_x - start_x, goal_y - start_y)

    print("Minimum Corridor Finder")
    print("=" * 55)
    print(f"  A = ({start_x/100:.3f}, {start_y/100:.3f})  →  "
          f"B = ({goal_x/100:.3f}, {goal_y/100:.3f})  [100 km]")
    print(f"  A→B distance : {route_km/100:.4f} units  ({route_km:.1f} km)")
    print()

    print("Running greedy simulation …")
    greedy_time, greedy_dev = run_greedy(start_x, start_y, goal_x, goal_y, heading, wind_path)
    print()

    print("Running crab-angle simulation …")
    crab_time, crab_dev = run_crab(start_x, start_y, goal_x, goal_y, heading, wind_path)
    print()

    print("Searching for minimum corridor (crab angle) …")
    crab_half = bisect_min_corridor(start_x, start_y, goal_x, goal_y, heading, wind_path,
                                    crab_time)

    sep = "-" * 60
    print()
    print(sep)
    print(f"{'':30s} {'Čas [min]':>10}  {'Max odmik [km]':>14}  {'Min koridor [km]':>16}")
    print(sep)
    # Greedy min corridor = 2 × max deviation (no bisection needed — greedy has no
    # corridor-awareness, so the tightest feasible corridor equals its observed track width).
    print(f"{'Greedy (direktno v B)':30s} {greedy_time:>10d}  {greedy_dev:>14.2f}  {greedy_dev*2:>16.3f}")
    print(f"{'Crab angle':30s} {crab_time:>10d}  {crab_dev:>14.2f}  {crab_half*2:>16.3f}")
    print(sep)
    print(f"\nMinimalni koridor – greedy    : {greedy_dev*2:.3f} km  (direktno iz max odmika)")
    print(f"Minimalni koridor – crab angle: {crab_half*2:.3f} km  (bisekcija)")


if __name__ == "__main__":
    main()
