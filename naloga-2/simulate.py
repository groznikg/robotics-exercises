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

MAX_SPEED_KMH = 30.0        # km/h
MAX_ACCEL     = 2.0         # km/h per minute
MAX_TURN_RATE = 5.0         # degrees per minute
DT_H          = 1.0 / 60.0 # time step: 1 minute expressed in hours
ARRIVAL_KM    = 0.5         # arrival threshold [km]


def parse_wind_file(path: str) -> list[tuple[float, float]]:
    """
    Read wind file. Expected format (whitespace-separated):
        N   speed[km/h]   direction[deg]
        1   10            90
        ...
    Header lines (non-numeric first token) and blank lines are skipped.
    Returns list of (speed_km_h, direction_deg).
    """
    winds: list[tuple[float, float]] = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            parts = raw.split()
            if len(parts) < 3:
                continue
            try:
                float(parts[0])
                winds.append((float(parts[1]), float(parts[2])))
            except ValueError:
                continue
    return winds


def wind_vector_at(winds: list[tuple[float, float]], t_min: int) -> tuple[float, float]:
    """Return wind velocity (vx, vy) km/h at simulation time t_min [minutes]."""
    speed, deg = winds[(t_min // 60) % len(winds)]
    rad = math.radians(deg)
    return speed * math.cos(rad), speed * math.sin(rad)


def angle_diff(target: float, current: float) -> float:
    """Signed shortest difference (target - current) in (-180, +180]."""
    return ((target - current + 180.0) % 360.0) - 180.0


def stopping_distance_km(speed_kmh: float) -> float:
    """
    Minimum distance needed to decelerate from speed_kmh to 0.
    Exact discrete sum over n = v/MAX_ACCEL steps:
        d = v * (v + MAX_ACCEL) / (2 * MAX_ACCEL * 60)
    """
    return speed_kmh * (speed_kmh + MAX_ACCEL) / (2.0 * MAX_ACCEL * 60.0)


def line_deviation_km(px: float, py: float,
                      ax: float, ay: float,
                      bx: float, by: float) -> float:
    """Perpendicular distance from point P to line segment A-B [km]."""
    ab = math.hypot(bx - ax, by - ay)
    if ab == 0.0:
        return math.hypot(px - ax, py - ay)
    return abs((bx - ax) * (ay - py) - (ax - px) * (by - ay)) / ab



def simulate(ax: float, ay: float,
             bx: float, by: float,
             phi0: float,
             winds: list[tuple[float, float]],
             log_path: str) -> None:
    """Run minute-by-minute simulation and print results. All positions are in km internally."""

    x, y = ax, ay
    phi  = phi0
    v    = 0.0
    t    = 0

    col = [
        ("Čas",             "[min]",    10),
        ("Pozicija X",      "[100 km]", 12),
        ("Pozicija Y",      "[100 km]", 12),
        ("Hitrost",         "[km/h]",   10),
        ("Dejanska hitrost","[km/h]",   16),
        ("Smer",            "[°]",       8),
        ("Razdalja do B",   "[100 km]", 14),
        ("Odmik od trase",  "[100 km]", 15),
    ]
    header = "  ".join(f"{name:>{w}}" for name, _, w in col)
    units  = "  ".join(f"{unit:>{w}}" for _, unit, w in col)
    sep    = "-" * len(header)

    actual_speed = 0.0

    def format_row(dist: float, dev: float) -> str:
        vals = [t, x/100, y/100, v, actual_speed, phi, dist/100, dev/100]
        fmts = [">10d", ">12.4f", ">12.4f", ">10.2f", ">16.2f", ">8.1f", ">14.5f", ">15.6f"]
        return "  ".join(format(val, f) for val, f in zip(vals, fmts))

    last_print_t = -1

    with open(log_path, "w", encoding="utf-8") as log:
        log.write(header + "\n")
        log.write(units + "\n")
        log.write(sep + "\n")
        print(header)
        print(units)
        print(sep)

        while True:
            dist = math.hypot(bx - x, by - y)
            dev  = line_deviation_km(x, y, ax, ay, bx, by)

            if t != last_print_t:
                row = format_row(dist, dev)
                log.write(row + "\n")
                if (t % 60 == 0 or dist < ARRIVAL_KM):
                    print(row)
                last_print_t = t

            if dist < ARRIVAL_KM:
                break

            # 1. Desired heading toward B
            desired_phi = math.degrees(math.atan2(by - y, bx - x))

            # 2. Turn toward desired heading (max MAX_TURN_RATE deg/min)
            turn = max(-MAX_TURN_RATE, min(MAX_TURN_RATE, angle_diff(desired_phi, phi)))
            phi  = (phi + turn) % 360.0

            # 3. Wind at current time
            wx, wy = wind_vector_at(winds, t)

            # 4. Speed control
            # Compute ground speed toward B (engine speed adjusted for wind component)
            phi_rad_now = math.radians(phi)
            tailwind = wx * math.cos(phi_rad_now) + wy * math.sin(phi_rad_now)
            v_ground  = v + tailwind  # actual speed toward B over ground
            # Stopping distance based on ground speed (ship stops when v_ground reaches 0)
            v_ground_stop = max(0.0, v_ground)
            ground_stop_dist = stopping_distance_km(v_ground_stop)
            if ground_stop_dist >= dist:
                # Keep enough engine speed to maintain positive ground speed (at least 1 km/h)
                min_v = max(0.0, -tailwind + 1.0)
                v = max(min_v, v - MAX_ACCEL)
            else:
                v = min(MAX_SPEED_KMH, v + MAX_ACCEL)

            # 5. Update position
            phi_rad = math.radians(phi)
            vx_total = v * math.cos(phi_rad) + wx
            vy_total = v * math.sin(phi_rad) + wy
            actual_speed = math.hypot(vx_total, vy_total)
            x += vx_total * DT_H
            y += vy_total * DT_H

            t += 1

            if t > 500_000:
                print("WARNING: Simulation exceeded 500 000 minutes — aborting.")
                break

        log.write(sep + "\n")
        h, m = divmod(t, 60)
        footer = (
            f"\nArrival time  : {t} min  ({h} h {m} min)\n"
            f"Final position: ({x/100:.5f}, {y/100:.5f})  [units of 100 km]\n"
            f"Distance to B : {dist/100:.5f} units  ({dist:.3f} km)"
        )
        log.write(footer + "\n")
        print(sep)
        print(footer)



def main() -> None:
    if len(sys.argv) != 7:
        print(__doc__)
        sys.exit(1)

    try:
        ax   = float(sys.argv[1]) * 100.0
        ay   = float(sys.argv[2]) * 100.0
        bx   = float(sys.argv[3]) * 100.0
        by   = float(sys.argv[4]) * 100.0
        phi0 = float(sys.argv[5])
    except ValueError:
        print("Error: numeric arguments expected for coordinates and heading.")
        sys.exit(1)

    wind_path = sys.argv[6]
    winds = parse_wind_file(wind_path)
    if not winds:
        print(f"Error: no valid wind data found in '{wind_path}'.")
        sys.exit(1)

    total_km = math.hypot(bx - ax, by - ay)

    print("Ship Navigation Simulator - Exercise 2")
    print("=" * 40)
    print(f"  A = ({ax/100:.3f}, {ay/100:.3f})  ->  B = ({bx/100:.3f}, {by/100:.3f})  [100 km]")
    print(f"  Initial heading : {phi0:.1f} deg")
    print(f"  A->B distance   : {total_km/100:.4f} units  ({total_km:.1f} km)")
    print(f"  Wind intervals  : {len(winds)}  (repeating)")
    print()

    log_path = "simulation_log.txt"
    print(f"  Full log        : {log_path}\n")
    simulate(ax, ay, bx, by, phi0, winds, log_path)


if __name__ == "__main__":
    main()
